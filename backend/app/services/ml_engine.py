"""
ml engine for erebys intelligence suite.

implements:
1. dynamic pricing recommendations (demand-based + feature-driven)
2. no-show risk prediction (logistic regression + rule-based fallback)
3. what-if price simulator (demand curve projection)
4. churn risk scoring (recency/frequency heuristic)

all models are interpretable — we return top contributing factors for every prediction.
"""

import logging
import math
from datetime import date, timedelta
from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.event import Event, EventType
from app.models.booking import Booking, BookingStatus
from app.models.attendance import Attendance
from app.models.payment import Payment
from app.models.athlete import Athlete
from app.models.coach import Coach
from app.models.organization import Organization
from app.models.pricing import PricingRecommendation

logger = logging.getLogger(__name__)

@dataclass
class PricingFeatures:
    fill_rate: float  # 0-1, historical avg for similar events
    days_to_start: int
    coach_rating: float  # 0-5
    event_type_weight: float  # camp=1.0, clinic=0.8, private=1.2
    seasonality_factor: float  # 0.7 (low season) to 1.3 (peak)
    competition_proxy: float  # 1-10
    current_price: float
    base_price: float
    capacity: int
    booked_count: int

@dataclass
class PricingResult:
    suggested_price: float
    confidence_score: int  # 0-100
    price_change_pct: float
    expected_demand_change: float  # % change in bookings
    expected_revenue_change: float  # % change in revenue
    explanation: str
    drivers: dict  # top factors with their contribution


# seasonal demand multipliers — june/july are peak, december is dead
SEASONALITY = {
    1: 0.85,   # january - post-holiday dip
    2: 0.90,   # february
    3: 1.00,   # march - spring season starts
    4: 1.10,   # april
    5: 1.15,   # may
    6: 1.30,   # june - peak summer camps
    7: 1.30,   # july - peak
    8: 1.20,   # august
    9: 1.05,   # september - back to school
    10: 0.95,  # october
    11: 0.85,  # november
    12: 0.80,  # december - holiday dip
}

EVENT_TYPE_WEIGHTS = {
    EventType.CAMP: 1.0,
    EventType.CLINIC: 0.85,
    EventType.PRIVATE: 1.25,
    "camp": 1.0,
    "clinic": 0.85,
    "private": 1.25,
}


async def generate_pricing_recommendation(
    db: AsyncSession,
    event: Event,
    org: Organization,
) -> PricingResult:
    """
    runs the pricing model on an event and returns a recommendation.

    algorithm:
    1. compute features (fill rate, seasonality, coach rating, etc.)
    2. estimate demand elasticity from historical data
    3. calculate optimal price point that maximizes expected revenue
    4. apply confidence scoring based on data quality
    5. generate human-readable explanation with top drivers
    """

    features = await _extract_pricing_features(db, event, org)
    elasticity = await _estimate_price_elasticity(db, event.organization_id, event.event_type)

    # demand score on a 0-1 scale
    demand_score = _calculate_demand_score(features)

    # convert demand score to a price multiplier
    price_multiplier = _calculate_price_multiplier(features, demand_score)
    suggested_price = round(features.base_price * price_multiplier, 2)

    # keep price within 50%-200% of base so we don't go crazy
    suggested_price = max(features.base_price * 0.5, min(suggested_price, features.base_price * 2.0))
    suggested_price = round(suggested_price / 5) * 5  # round to nearest $5

    # figure out expected impact of the price change
    price_change_pct = round((suggested_price - features.current_price) / features.current_price * 100, 1)
    demand_change = _estimate_demand_change(price_change_pct, elasticity)
    revenue_change = _estimate_revenue_change(price_change_pct, demand_change)

    # how confident are we? depends on how much data we have
    confidence = _calculate_confidence(features, db)

    # build the drivers dict and explanation text
    drivers = _identify_top_drivers(features, demand_score, price_multiplier)
    explanation = _generate_explanation(features, suggested_price, drivers)

    return PricingResult(
        suggested_price=suggested_price,
        confidence_score=confidence,
        price_change_pct=price_change_pct,
        expected_demand_change=round(demand_change, 1),
        expected_revenue_change=round(revenue_change, 1),
        explanation=explanation,
        drivers=drivers,
    )


async def what_if_simulation(
    db: AsyncSession,
    event: Event,
    org: Organization,
    price_points: list[float],
) -> list[dict]:
    """
    simulates demand and revenue at different price points.
    returns a curve of (price, demand, revenue, utilization).
    """
    features = await _extract_pricing_features(db, event, org)
    elasticity = await _estimate_price_elasticity(db, event.organization_id, event.event_type)

    # use actual booked count if available, otherwise estimate from fill rate
    base_demand = features.booked_count if features.booked_count > 0 else features.capacity * features.fill_rate

    results = []
    for price in price_points:
        pct_change = (price - features.current_price) / features.current_price * 100
        demand_change = _estimate_demand_change(pct_change, elasticity)
        estimated_demand = max(0, base_demand * (1 + demand_change / 100))
        estimated_demand = min(estimated_demand, features.capacity)
        estimated_revenue = estimated_demand * price
        estimated_utilization = estimated_demand / max(features.capacity, 1) * 100

        results.append({
            "price": price,
            "estimated_demand": round(estimated_demand, 1),
            "estimated_revenue": round(estimated_revenue, 2),
            "estimated_utilization": round(estimated_utilization, 1),
        })

    return results


async def predict_no_show_risk(
    db: AsyncSession,
    athlete_id: str,
    event_id: str | None = None,
) -> dict:
    """
    predicts no-show probability for an athlete.

    uses a hybrid approach:
    1. rule-based scoring from historical patterns
    2. logistic regression if enough data exists
    """
    athlete = await db.get(Athlete, athlete_id)
    if not athlete:
        return {"risk_score": 0.5, "risk_level": "unknown", "factors": ["Athlete not found"]}

    # pull the features we need
    historical_no_show_rate = athlete.no_show_rate / 100.0
    total_bookings = athlete.total_bookings
    days_since_last = (
        (date.today() - athlete.last_booking_date).days
        if athlete.last_booking_date
        else 365
    )

    # always compute the rule-based score first
    rule_score = _rule_based_no_show_score(
        historical_no_show_rate, total_bookings, days_since_last
    )

    # try ml if we have enough data, otherwise stick with rules
    ml_score = None
    if total_bookings >= 5:
        ml_score = await _ml_no_show_score(db, athlete)

    # ml takes precedence when available
    final_score = ml_score if ml_score is not None else rule_score

    if final_score > 0.4:
        level = "high"
    elif final_score > 0.2:
        level = "medium"
    else:
        level = "low"

    factors = []
    if historical_no_show_rate > 0.2:
        factors.append(f"High historical no-show rate ({historical_no_show_rate:.0%})")
    if total_bookings < 3:
        factors.append("Limited booking history")
    if days_since_last > 90:
        factors.append(f"Inactive for {days_since_last} days")
    if historical_no_show_rate <= 0.1 and total_bookings >= 5:
        factors.append("Consistent attendance record")

    return {
        "risk_score": round(final_score, 3),
        "risk_level": level,
        "factors": factors if factors else ["Within normal patterns"],
        "model_used": "ml" if ml_score is not None else "rules",
    }


async def calculate_churn_risk(db: AsyncSession, athlete: Athlete) -> dict:
    """
    scores churn risk based on how recently and how often they book — simple rfm-style heuristic
    """
    if not athlete.last_booking_date:
        return {"churn_risk": 0.9, "risk_level": "high", "reason": "No booking history"}

    days_since_last = (date.today() - athlete.last_booking_date).days

    # frequency: avg bookings per month
    if athlete.first_booking_date:
        months_active = max(1, (date.today() - athlete.first_booking_date).days / 30)
        freq = athlete.total_bookings / months_active
    else:
        freq = 0

    # recency maxes out at 6 months gone, frequency floors out at 2+/month
    recency_factor = min(1.0, days_since_last / 180)  # max at 6 months
    frequency_factor = max(0, 1.0 - freq / 2)  # 2+ bookings/month = low risk

    churn_risk = round(recency_factor * 0.6 + frequency_factor * 0.4, 3)

    if churn_risk > 0.6:
        level = "high"
    elif churn_risk > 0.3:
        level = "medium"
    else:
        level = "low"

    return {
        "churn_risk": churn_risk,
        "risk_level": level,
        "days_since_last_booking": days_since_last,
        "booking_frequency": round(freq, 2),
    }


async def _extract_pricing_features(
    db: AsyncSession, event: Event, org: Organization
) -> PricingFeatures:
    """pulls together all the features the pricing model needs"""

    # historical fill rate for similar event types at this org
    similar_events = await db.execute(
        select(func.avg(Event.booked_count * 1.0 / func.nullif(Event.capacity, 0)))
        .where(
            Event.organization_id == org.id,
            Event.event_type == event.event_type,
            Event.status.in_(["completed", "published", "full"]),
        )
    )
    fill_rate = float(similar_events.scalar() or 0.5)

    # days until the event starts
    days_to_start = max(0, (event.start_date - date.today()).days)

    # coach rating if we have one
    coach_rating = 3.0
    if event.coach_id:
        coach = await db.get(Coach, event.coach_id)
        if coach and coach.avg_rating > 0:
            coach_rating = coach.avg_rating

    # event type weight — privates command a premium
    event_type_weight = EVENT_TYPE_WEIGHTS.get(event.event_type, 1.0)

    # seasonality based on start month
    target_month = event.start_date.month
    seasonality_factor = SEASONALITY.get(target_month, 1.0)

    return PricingFeatures(
        fill_rate=fill_rate,
        days_to_start=days_to_start,
        coach_rating=coach_rating,
        event_type_weight=event_type_weight,
        seasonality_factor=seasonality_factor,
        competition_proxy=org.competition_proxy,
        current_price=event.current_price,
        base_price=event.base_price,
        capacity=event.capacity,
        booked_count=event.booked_count,
    )


async def _estimate_price_elasticity(
    db: AsyncSession, org_id: str, event_type
) -> float:
    """
    estimates how sensitive demand is to price changes from historical data.
    returns a negative number (e.g., -1.5 means 1% price increase → 1.5% demand decrease).
    """
    # compare fill rates at different price levels for completed events
    result = await db.execute(
        select(Event.current_price, Event.booked_count, Event.capacity)
        .where(
            Event.organization_id == org_id,
            Event.event_type == event_type,
            Event.capacity > 0,
            Event.status.in_(["completed", "full"]),
        )
        .order_by(Event.current_price)
    )
    rows = result.all()

    if len(rows) < 5:
        # not enough data — use category defaults
        defaults = {"camp": -1.2, "clinic": -1.0, "private": -0.8}
        et = event_type.value if hasattr(event_type, 'value') else event_type
        return defaults.get(et, -1.0)

    # simple linear regression on log(price) vs log(fill_rate)
    prices = np.array([r[0] for r in rows])
    fill_rates = np.array([r[1] / r[2] for r in rows])
    fill_rates = np.clip(fill_rates, 0.01, 1.0)

    log_prices = np.log(prices)
    log_fills = np.log(fill_rates)

    # elasticity = d(log Q) / d(log P)
    if np.std(log_prices) > 0:
        elasticity = np.corrcoef(log_prices, log_fills)[0, 1] * np.std(log_fills) / np.std(log_prices)
    else:
        elasticity = -1.0

    return max(-3.0, min(-0.3, elasticity))  # bound to reasonable range


def _calculate_demand_score(features: PricingFeatures) -> float:
    """
    scores demand on a 0-1 scale — higher means more demand, more room to raise price.
    """
    scores = {
        "fill_rate": features.fill_rate,
        "urgency": max(0, 1 - features.days_to_start / 60),  # closer to start = higher urgency signal
        "coach_quality": features.coach_rating / 5.0,
        "seasonality": (features.seasonality_factor - 0.7) / 0.6,  # normalize to 0-1
        "competition": 1 - (features.competition_proxy / 10),  # low competition = higher demand
        "event_premium": (features.event_type_weight - 0.8) / 0.5,  # private > camp > clinic
    }

    weights = {
        "fill_rate": 0.30,
        "urgency": 0.15,
        "coach_quality": 0.15,
        "seasonality": 0.20,
        "competition": 0.10,
        "event_premium": 0.10,
    }

    demand = sum(scores[k] * weights[k] for k in scores)
    return max(0, min(1, demand))


def _calculate_price_multiplier(features: PricingFeatures, demand_score: float) -> float:
    """converts demand score to a price multiplier using a sigmoid curve"""
    # sigmoid centered at 0.5 so score=0.5 means no change
    # score=0.8 → ~15% increase, score=0.2 → ~12% decrease
    x = (demand_score - 0.5) * 4  # scale to [-2, 2]
    multiplier = 1 + 0.2 * (2 / (1 + math.exp(-x)) - 1)  # sigmoid between 0.8 and 1.2

    # nudge price up/down based on current utilization
    current_util = features.booked_count / max(features.capacity, 1)
    if current_util > 0.85:
        multiplier *= 1.05
    elif current_util < 0.3:
        multiplier *= 0.95

    return multiplier


def _estimate_demand_change(price_change_pct: float, elasticity: float) -> float:
    """estimates % change in demand given a price change and the elasticity coefficient"""
    return price_change_pct * elasticity


def _estimate_revenue_change(price_change_pct: float, demand_change: float) -> float:
    """estimates % change in revenue — price change times demand change, compounded"""
    return (1 + price_change_pct / 100) * (1 + demand_change / 100) * 100 - 100


def _calculate_confidence(features: PricingFeatures, db) -> int:
    """scores how confident we are in the recommendation — more data = more confidence"""
    score = 50  # start at 50

    # we have historical fill data
    if features.fill_rate > 0:
        score += 15

    # coach rating is available
    if features.coach_rating > 0:
        score += 10

    # closer events are more predictable
    if features.days_to_start < 30:
        score += 10
    elif features.days_to_start > 90:
        score -= 10

    # bigger events have more data points to learn from
    if features.capacity >= 15:
        score += 5

    # existing bookings give us a real demand signal
    if features.booked_count > 0:
        score += 10

    return max(10, min(95, score))


def _identify_top_drivers(features: PricingFeatures, demand_score: float, multiplier: float) -> dict:
    """figures out which factors are driving the recommendation and ranks them by impact"""
    drivers = {}

    # fill rate contribution
    fill_impact = (features.fill_rate - 0.5) * 0.30
    if abs(fill_impact) > 0.02:
        direction = "upward" if fill_impact > 0 else "downward"
        drivers["Historical Fill Rate"] = {
            "value": f"{features.fill_rate:.0%}",
            "impact": direction,
            "weight": round(abs(fill_impact), 3),
            "description": f"Similar events fill at {features.fill_rate:.0%} capacity",
        }

    # seasonality contribution
    season_impact = (features.seasonality_factor - 1.0) * 0.20
    if abs(season_impact) > 0.02:
        direction = "upward" if season_impact > 0 else "downward"
        drivers["Seasonality"] = {
            "value": f"{features.seasonality_factor:.2f}x",
            "impact": direction,
            "weight": round(abs(season_impact), 3),
            "description": f"Month {features.days_to_start} demand factor: {features.seasonality_factor:.2f}x",
        }

    # coach rating contribution
    coach_impact = (features.coach_rating - 3.0) / 5.0 * 0.15
    if abs(coach_impact) > 0.01:
        direction = "upward" if coach_impact > 0 else "downward"
        drivers["Coach Rating"] = {
            "value": f"{features.coach_rating:.1f}/5.0",
            "impact": direction,
            "weight": round(abs(coach_impact), 3),
            "description": f"Coach rated {features.coach_rating:.1f} out of 5.0",
        }

    # urgency — event starting soon creates demand pressure
    if features.days_to_start < 14:
        drivers["Time Urgency"] = {
            "value": f"{features.days_to_start} days",
            "impact": "upward",
            "weight": 0.08,
            "description": f"Only {features.days_to_start} days until event",
        }

    # competition level in the local market
    if features.competition_proxy != 5.0:
        direction = "downward" if features.competition_proxy > 5 else "upward"
        drivers["Market Competition"] = {
            "value": f"{features.competition_proxy}/10",
            "impact": direction,
            "weight": 0.05,
            "description": f"Competition level: {features.competition_proxy}/10",
        }

    # sort by weight so the biggest drivers come first
    drivers = dict(sorted(drivers.items(), key=lambda x: x[1]["weight"], reverse=True))
    return drivers


def _generate_explanation(features: PricingFeatures, suggested: float, drivers: dict) -> str:
    """writes a plain-english explanation of the recommendation"""
    if suggested > features.current_price:
        direction = "increase"
        reason_parts = []
        for name, info in list(drivers.items())[:3]:
            if info["impact"] == "upward":
                reason_parts.append(f"{name.lower()} ({info['value']})")
        reasons = ", ".join(reason_parts) if reason_parts else "overall demand signals"
        return (
            f"Recommend {direction} from ${features.current_price:.0f} to ${suggested:.0f}. "
            f"Key drivers: {reasons}. "
            f"Current utilization at {features.booked_count}/{features.capacity} "
            f"({features.fill_rate:.0%} historical fill rate for similar events)."
        )
    elif suggested < features.current_price:
        return (
            f"Recommend decrease from ${features.current_price:.0f} to ${suggested:.0f}. "
            f"Current fill rate ({features.fill_rate:.0%}) suggests price may be limiting demand. "
            f"Lowering price could increase bookings and total revenue."
        )
    else:
        return (
            f"Current price of ${features.current_price:.0f} appears well-calibrated. "
            f"Demand signals are balanced — no change recommended at this time."
        )


def _rule_based_no_show_score(
    historical_rate: float,
    total_bookings: int,
    days_since_last: int,
) -> float:
    """simple rule-based no-show risk score when we don't have enough data for ml"""
    score = 0.0

    # historical rate is the strongest signal we have
    score += historical_rate * 0.6

    # infrequent bookers are slightly riskier
    if total_bookings < 3:
        score += 0.15
    elif total_bookings > 10:
        score -= 0.05

    # long inactive periods tend to correlate with no-shows
    if days_since_last > 90:
        score += 0.1
    elif days_since_last > 180:
        score += 0.2

    return max(0, min(1, score))


class PricingEngine:
    """
    synchronous pricing engine for use in celery workers and unit tests.
    computes recommendations without db — accepts pre-fetched data.
    """

    def generate_recommendation(
        self, event, bookings: list, competition_proxy: float = 5.0,
        coach_rating: float = 4.0,
    ) -> dict:
        capacity = event.capacity or 20
        booked = event.booked_count if hasattr(event, 'booked_count') else len(bookings)
        fill_rate = booked / max(capacity, 1)

        start = event.start_date
        days_to_start = max(0, (start - date.today()).days) if start else 30

        et = event.event_type
        et_key = et.value if hasattr(et, 'value') else et
        event_type_weight = EVENT_TYPE_WEIGHTS.get(et, EVENT_TYPE_WEIGHTS.get(et_key, 1.0))
        month = start.month if start else date.today().month
        seasonality = SEASONALITY.get(month, 1.0)

        features = PricingFeatures(
            fill_rate=fill_rate,
            days_to_start=days_to_start,
            coach_rating=coach_rating,
            event_type_weight=event_type_weight,
            seasonality_factor=seasonality,
            competition_proxy=competition_proxy,
            current_price=event.current_price,
            base_price=event.base_price,
            capacity=capacity,
            booked_count=booked,
        )

        demand_score = _calculate_demand_score(features)
        multiplier = _calculate_price_multiplier(features, demand_score)
        suggested = round(features.base_price * multiplier, 2)
        suggested = max(features.base_price * 0.5, min(suggested, features.base_price * 2.0))
        suggested = round(suggested / 5) * 5

        price_change_pct = round((suggested - features.current_price) / max(features.current_price, 1) * 100, 1)

        # default elasticity by event type when we have no historical data
        defaults = {"camp": -1.2, "clinic": -1.0, "private": -0.8}
        elasticity = defaults.get(et_key, -1.0)
        demand_change = _estimate_demand_change(price_change_pct, elasticity)
        revenue_change = _estimate_revenue_change(price_change_pct, demand_change)
        confidence = _calculate_confidence(features, None)
        drivers = _identify_top_drivers(features, demand_score, multiplier)
        explanation = _generate_explanation(features, suggested, drivers)

        return {
            "suggested_price": suggested,
            "confidence": confidence,
            "price_change_pct": price_change_pct,
            "expected_demand_change": round(demand_change, 1),
            "expected_revenue_change": round(revenue_change, 1),
            "explanation": explanation,
            "drivers": drivers,
        }

    def what_if_simulate(
        self, event, bookings: list, competition_proxy: float = 5.0,
        test_prices: list[float] | None = None,
    ) -> list[dict]:
        capacity = event.capacity or 20
        booked = event.booked_count if hasattr(event, 'booked_count') else len(bookings)
        fill_rate = booked / max(capacity, 1)
        base_demand = booked if booked > 0 else capacity * fill_rate

        et = event.event_type
        et_key = et.value if hasattr(et, 'value') else et
        defaults = {"camp": -1.2, "clinic": -1.0, "private": -0.8}
        elasticity = defaults.get(et_key, -1.0)

        if not test_prices:
            base = event.current_price
            test_prices = [round(base * m) for m in [0.7, 0.85, 1.0, 1.15, 1.3]]

        results = []
        for price in test_prices:
            pct = (price - event.current_price) / max(event.current_price, 1) * 100
            demand_change = _estimate_demand_change(pct, elasticity)
            projected = max(0, min(base_demand * (1 + demand_change / 100), capacity))
            results.append({
                "price": price,
                "projected_demand": round(projected, 1),
                "projected_revenue": round(projected * price, 2),
                "projected_utilization": round(projected / max(capacity, 1) * 100, 1),
            })
        return results


async def _ml_no_show_score(db: AsyncSession, athlete: Athlete) -> float | None:
    """
    trains a quick logistic regression on booking history to predict no-show probability.
    returns none if there isn't enough data to bother.
    """
    # grab attendance records across the org to train on
    result = await db.execute(
        select(
            Attendance.no_show,
            Booking.price_paid,
            Event.event_type,
            Event.capacity,
            Event.booked_count,
        )
        .join(Booking, Booking.id == Attendance.booking_id)
        .join(Event, Event.id == Booking.event_id)
        .where(Booking.organization_id == athlete.organization_id)
        .limit(500)
    )
    rows = result.all()

    if len(rows) < 20:
        return None

    try:
        # build the feature matrix
        X = []
        y = []
        for no_show, price, etype, capacity, booked in rows:
            et_val = {"camp": 0, "clinic": 1, "private": 2}.get(
                etype.value if hasattr(etype, 'value') else etype, 0
            )
            X.append([price, et_val, capacity, booked])
            y.append(1 if no_show else 0)

        X = np.array(X, dtype=float)
        y = np.array(y, dtype=float)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = LogisticRegression(max_iter=200, random_state=42)
        model.fit(X_scaled, y)

        # predict using this athlete's typical booking profile
        athlete_features = np.array([[
            athlete.ltv / max(athlete.total_bookings, 1),  # avg price paid
            0,  # default event type
            20,  # default capacity
            10,  # default booked
        ]])
        athlete_scaled = scaler.transform(athlete_features)
        proba = model.predict_proba(athlete_scaled)[0][1]
        return float(proba)
    except Exception as e:
        logger.warning(f"ML no-show prediction failed: {e}")
        return None

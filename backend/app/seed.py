"""
seed script — generates realistic multi-organization academy data.

usage:
    python -m app.seed                # from backend/
    docker compose exec backend python -m app.seed
"""

import uuid
import random
import logging
from datetime import date, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.organization import Organization
from app.models.user import User, OrgUserRole, RoleEnum
from app.models.coach import Coach
from app.models.athlete import Athlete
from app.models.event import Event, EventType, EventStatus
from app.models.booking import Booking, BookingStatus, BookingSource
from app.models.attendance import Attendance
from app.models.payment import Payment, PaymentStatus
from app.models.rating import Rating
from app.models.metrics import MetricsDaily
from app.models.feature_flag import FeatureFlag
from app.models.pricing import PricingRecommendation
from app.models.experiment import Experiment as ExperimentModel, ExperimentStatus
from app.models.insight import InsightReport
from app.services.auth import hash_password
from app.models.evaluation import (
    EvaluationTemplate, Evaluation, EvaluationCategory, EvaluationNarrative,
    EvaluationType, EvaluationStatus,
)
from app.services.evaluation_ai import generate_narrative

logger = logging.getLogger("erebys.seed")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")

settings = get_settings()
engine = create_engine(settings.database_url_sync)

# org configs with sport type and rough competition level
ORGS = [
    {"name": "Elite Soccer Academy", "slug": "elite-soccer", "sport_type": "soccer", "region": "US-East", "competition_proxy": 7.5},
    {"name": "Bay Area Tennis Club", "slug": "bay-tennis", "sport_type": "tennis", "region": "US-West", "competition_proxy": 6.0},
    {"name": "Northside Basketball Training", "slug": "northside-bball", "sport_type": "basketball", "region": "US-Midwest", "competition_proxy": 4.5},
    {"name": "Coastal Swim Academy", "slug": "coastal-swim", "sport_type": "swimming", "region": "US-West", "competition_proxy": 5.5},
    {"name": "Mountain Volleyball Club", "slug": "mountain-vball", "sport_type": "volleyball", "region": "US-Mountain", "competition_proxy": 3.5},
]

COACH_NAMES = [
    "Marcus Rivera", "Sophia Chen", "David Kim", "Olivia Johnson", "James O'Brien",
    "Emily Watson", "Carlos Mendez", "Aisha Patel", "Ryan Thompson", "Jessica Lee",
    "Alex Kowalski", "Natalie Brooks", "Daniel Park", "Maria Santos", "Chris Williams",
]

ATHLETE_FIRST = ["Liam", "Emma", "Noah", "Ava", "Oliver", "Isabella", "Elijah", "Mia", "Lucas", "Charlotte",
                 "Mason", "Amelia", "Ethan", "Harper", "Aiden", "Evelyn", "Jackson", "Abigail", "Sebastian", "Ella",
                 "James", "Scarlett", "Benjamin", "Grace", "Henry", "Chloe", "Alexander", "Zoey", "William", "Riley",
                 "Daniel", "Nora", "Michael", "Lily", "Owen", "Eleanor", "Jack", "Hannah", "Leo", "Layla"]
ATHLETE_LAST = ["Smith", "Johnson", "Brown", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
                "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen"]

CAMP_NAMES = {
    "soccer": ["Summer Striker Camp", "Elite Defense Clinic", "Goalkeeper Intensive", "U12 Skills Bootcamp",
               "Weekend Finishing School", "Pre-Season Fitness Camp", "Technical Mastery Week", "1v1 Private Session"],
    "tennis": ["Serve & Volley Camp", "Junior Development Clinic", "Adult Beginner Workshop", "Match Play Intensive",
               "Doubles Strategy Camp", "Private Lesson Block", "Tournament Prep Week", "Footwork Clinic"],
    "basketball": ["Shooting Stars Camp", "Point Guard Academy", "Big Man Clinic", "Youth Skills Development",
                   "Summer Hoops Week", "3-on-3 Tournament Camp", "Private Skills Training", "Defensive Fundamentals"],
    "swimming": ["Stroke Technique Intensive", "Competitive Swim Camp", "Open Water Clinic", "Speed Development Week",
                 "Junior Swim Academy", "Adult Masters Camp", "Private Swim Lesson", "Race Strategy Clinic"],
    "volleyball": ["Serve & Pass Camp", "Attack Fundamentals Clinic", "Setter Training Camp", "Beach Volleyball Week",
                   "Junior Development Camp", "Private Skills Session", "Tournament Prep Camp", "Defense Mastery Clinic"],
}

EVAL_TEMPLATES = {
    "soccer": {
        "name": "Soccer Performance Evaluation",
        "categories": [
            {"name": "Technical Skills", "weight": 1.5},
            {"name": "Tactical Awareness", "weight": 1.2},
            {"name": "Physical Attributes", "weight": 1.0},
            {"name": "Mental Game", "weight": 0.8},
            {"name": "Teamwork", "weight": 1.0},
        ]
    },
    "tennis": {
        "name": "Tennis Player Assessment",
        "categories": [
            {"name": "Stroke Mechanics", "weight": 1.5},
            {"name": "Court Awareness", "weight": 1.2},
            {"name": "Physical Attributes", "weight": 1.0},
            {"name": "Mental Game", "weight": 1.3},
            {"name": "Match Play & Strategy", "weight": 1.0},
        ]
    },
    "basketball": {
        "name": "Basketball Skills Evaluation",
        "categories": [
            {"name": "Ball Handling", "weight": 1.2},
            {"name": "Shooting", "weight": 1.3},
            {"name": "Defense", "weight": 1.0},
            {"name": "Basketball IQ", "weight": 1.2},
            {"name": "Physical Attributes", "weight": 0.8},
            {"name": "Teamwork", "weight": 1.0},
        ]
    },
    "swimming": {
        "name": "Swim Performance Review",
        "categories": [
            {"name": "Stroke Mechanics", "weight": 1.5},
            {"name": "Physical Attributes", "weight": 1.2},
            {"name": "Mental Game", "weight": 1.0},
            {"name": "Technical Skills", "weight": 1.2},
        ]
    },
    "volleyball": {
        "name": "Volleyball Skills Assessment",
        "categories": [
            {"name": "Technical Skills", "weight": 1.3},
            {"name": "Tactical Awareness", "weight": 1.1},
            {"name": "Physical Attributes", "weight": 1.0},
            {"name": "Teamwork", "weight": 1.2},
            {"name": "Mental Game", "weight": 0.9},
        ]
    },
}

SKILL_LEVELS = ["beginner", "intermediate", "advanced", "elite"]
SPECIALTIES = {
    "soccer": ["forward", "midfielder", "defender", "goalkeeper", "general"],
    "tennis": ["serve", "baseline", "net play", "all-court", "general"],
    "basketball": ["shooting", "ball handling", "post play", "defense", "general"],
    "swimming": ["freestyle", "butterfly", "breaststroke", "backstroke", "general"],
    "volleyball": ["setting", "hitting", "libero", "serving", "general"],
}


def _uid() -> str:
    return str(uuid.uuid4())


def _random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(0, delta)))


def _random_time() -> str:
    hours = random.choice([8, 9, 10, 13, 14, 15, 16, 17, 18])
    return f"{hours:02d}:00"


def seed():
    session = Session(engine)
    logger.info("🌱 Starting seed…")

    try:
        # create the superadmin user first
        superadmin = User(
            id=_uid(), email="admin@erebys.io", hashed_password=hash_password("admin123"),
            full_name="Erebys Admin", is_active=True, is_superadmin=True,
        )
        session.add(superadmin)
        logger.info("  👤 Created superadmin: admin@erebys.io / admin123")

        all_orgs = []
        all_events = []

        # global eval templates (org_id = None = available to all)
        sport_templates = {}
        for sport, tmpl_data in EVAL_TEMPLATES.items():
            tmpl = EvaluationTemplate(
                id=_uid(),
                organization_id=None,
                sport_type=sport,
                name=tmpl_data["name"],
                categories=tmpl_data["categories"],
                is_default=True,
            )
            session.add(tmpl)
            sport_templates[sport] = tmpl
        session.flush()

        for org_data in ORGS:
            org_id = _uid()
            org = Organization(id=org_id, **org_data)
            session.add(org)
            session.flush()  # persist org before dependent FK inserts
            all_orgs.append(org)

            # turn on all feature flags for this org
            for key in ["pricing_engine", "experiments", "exports", "insights"]:
                session.add(FeatureFlag(id=_uid(), organization_id=org_id, feature_key=key, enabled=True))

            # create owner and manager users for this org
            owner = User(
                id=_uid(), email=f"owner@{org_data['slug']}.com", hashed_password=hash_password("password123"),
                full_name=f"{org_data['name']} Owner", is_active=True,
            )
            session.add(owner)
            session.add(OrgUserRole(id=_uid(), user_id=owner.id, organization_id=org_id, role=RoleEnum.ADMIN))

            manager = User(
                id=_uid(), email=f"coach@{org_data['slug']}.com", hashed_password=hash_password("password123"),
                full_name=f"{org_data['name']} Coach", is_active=True,
            )
            session.add(manager)
            session.add(OrgUserRole(id=_uid(), user_id=manager.id, organization_id=org_id, role=RoleEnum.MANAGER))
            session.flush()  # flush users so experiment created_by fk resolves correctly

            # spin up a few coaches per org
            sport = org_data["sport_type"]
            num_coaches = random.randint(3, 5)
            coaches = []
            coach_pool = random.sample(COACH_NAMES, num_coaches)

            for cname in coach_pool:
                coach = Coach(
                    id=_uid(), organization_id=org_id, full_name=cname,
                    email=f"{cname.lower().replace(' ', '.')}@{org_data['slug']}.com",
                    specialty=random.choice(SPECIALTIES.get(sport, ["general"])),
                    hourly_rate=round(random.uniform(40, 120), 2),
                    avg_rating=round(random.uniform(3.5, 5.0), 1),
                )
                session.add(coach)
                coaches.append(coach)

            # generate a bunch of athletes for this org
            num_athletes = random.randint(80, 120)
            athletes = []
            for _ in range(num_athletes):
                fname = random.choice(ATHLETE_FIRST)
                lname = random.choice(ATHLETE_LAST)
                first_booking = _random_date(date.today() - timedelta(days=365), date.today() - timedelta(days=30))
                athlete = Athlete(
                    id=_uid(), organization_id=org_id,
                    full_name=f"{fname} {lname}",
                    email=f"{fname.lower()}.{lname.lower()}{random.randint(1,99)}@email.com",
                    date_of_birth=_random_date(date(2005, 1, 1), date(2018, 12, 31)),
                    skill_level=random.choice(SKILL_LEVELS),
                    first_booking_date=first_booking,
                )
                session.add(athlete)
                athletes.append(athlete)

            # create events — mix of camps, clinics, and privates
            event_names = CAMP_NAMES.get(sport, CAMP_NAMES["soccer"])
            today = date.today()

            for i in range(random.randint(12, 20)):
                etype = random.choices(
                    [EventType.CAMP, EventType.CLINIC, EventType.PRIVATE],
                    weights=[0.4, 0.35, 0.25],
                )[0]

                if etype == EventType.PRIVATE:
                    capacity = random.choice([1, 2, 3])
                    base_price = round(random.uniform(60, 180), 0)
                    title = f"Private Session – {random.choice(coaches).full_name}"
                elif etype == EventType.CLINIC:
                    capacity = random.randint(8, 20)
                    base_price = round(random.uniform(35, 80), 0)
                    title = random.choice([n for n in event_names if "Clinic" in n or "Workshop" in n] or event_names)
                else:
                    capacity = random.randint(15, 40)
                    base_price = round(random.uniform(80, 250), 0)
                    title = random.choice([n for n in event_names if "Camp" in n or "Week" in n or "Bootcamp" in n] or event_names)

                start = _random_date(today - timedelta(days=120), today + timedelta(days=60))
                is_past = start < today
                booked_count = random.randint(int(capacity * 0.3), capacity) if is_past else random.randint(0, int(capacity * 0.8))

                event = Event(
                    id=_uid(), organization_id=org_id,
                    coach_id=random.choice(coaches).id,
                    title=title, event_type=etype,
                    status=EventStatus.COMPLETED if is_past else EventStatus.PUBLISHED,
                    capacity=capacity, booked_count=min(booked_count, capacity),
                    base_price=base_price, current_price=base_price,
                    start_date=start,
                    end_date=start + timedelta(days=random.choice([0, 1, 3, 5])) if etype != EventType.PRIVATE else start,
                    start_time=_random_time(),
                    end_time=f"{int(_random_time()[:2]) + random.choice([2, 3]):02d}:00",
                    location=f"Field {random.randint(1, 5)}" if sport == "soccer" else f"Court {random.randint(1, 8)}",
                    skill_level=random.choice(SKILL_LEVELS[:3]),
                )
                session.add(event)
                all_events.append(event)

                # create bookings, payments, and attendance for this event
                booked_athletes = random.sample(athletes, min(event.booked_count, len(athletes)))
                for athlete in booked_athletes:
                    booked_at = datetime.combine(
                        _random_date(start - timedelta(days=30), start - timedelta(days=1)),
                        datetime.min.time()
                    ) + timedelta(hours=random.randint(8, 20))

                    is_cancelled = random.random() < 0.08
                    discount = round(random.choice([0, 0, 0, 5, 10, 15, 20]), 2) if random.random() < 0.3 else 0
                    price_paid = max(base_price - discount, 0)

                    booking = Booking(
                        id=_uid(), event_id=event.id, athlete_id=athlete.id, organization_id=org_id,
                        status=BookingStatus.CANCELLED if is_cancelled else BookingStatus.CONFIRMED,
                        source=random.choices(
                            [BookingSource.PLATFORM, BookingSource.DIRECT, BookingSource.REFERRAL],
                            weights=[0.6, 0.25, 0.15],
                        )[0],
                        price_paid=price_paid, discount_applied=discount,
                        booked_at=booked_at,
                        cancelled_at=booked_at + timedelta(days=random.randint(1, 5)) if is_cancelled else None,
                    )
                    session.add(booking)

                    # payment record for confirmed bookings
                    if not is_cancelled:
                        session.add(Payment(
                            id=_uid(), booking_id=booking.id, organization_id=org_id,
                            amount=price_paid, status=PaymentStatus.COMPLETED,
                            paid_at=booked_at + timedelta(minutes=random.randint(1, 30)),
                        ))

                    # attendance for past events only
                    if is_past and not is_cancelled:
                        no_show = random.random() < 0.12
                        late_cancel = not no_show and random.random() < 0.05
                        attended = not no_show and not late_cancel
                        session.add(Attendance(
                            id=_uid(), booking_id=booking.id,
                            attended=attended, no_show=no_show, late_cancel=late_cancel,
                            check_in_time=datetime.combine(start, datetime.min.time()) + timedelta(hours=random.randint(8, 10)) if attended else None,
                        ))

                    # keep athlete aggregate fields up to date
                    athlete.total_bookings = (athlete.total_bookings or 0) + 1
                    athlete.ltv = (athlete.ltv or 0) + price_paid
                    if not athlete.last_booking_date or start > athlete.last_booking_date:
                        athlete.last_booking_date = start

                # ratings for past events — not everyone leaves one
                if is_past and booked_athletes:
                    num_ratings = random.randint(1, max(1, min(5, len(booked_athletes))))
                    for athlete in random.sample(booked_athletes, num_ratings):
                        session.add(Rating(
                            id=_uid(), event_id=event.id, coach_id=event.coach_id,
                            athlete_id=athlete.id, organization_id=org_id,
                            score=round(random.uniform(3.0, 5.0), 1),
                            comment=random.choice([
                                "Great session!", "Very helpful coach.", "Learned a lot.",
                                "Would recommend.", "Good intensity.", "Excellent drills.",
                                "Need more advanced content.", None, None,
                            ]),
                        ))

            # fill in 180 days of historical metrics so the dashboard has data
            for day_offset in range(180):
                d = today - timedelta(days=day_offset)
                base_rev = random.uniform(200, 2000) * (1 + 0.3 * (d.weekday() >= 5))  # weekends higher
                session.add(MetricsDaily(
                    id=_uid(), organization_id=org_id, metric_date=d,
                    total_revenue=round(base_rev, 2),
                    booking_count=random.randint(3, 25),
                    cancellation_count=random.randint(0, 3),
                    total_capacity=random.randint(40, 120),
                    total_booked=random.randint(20, 100),
                    utilization_rate=round(random.uniform(40, 95), 1),
                    no_show_count=random.randint(0, 4),
                    no_show_rate=round(random.uniform(2, 18), 1),
                    late_cancel_count=random.randint(0, 2),
                    active_athletes=random.randint(15, 60),
                    new_athletes=random.randint(0, 5),
                    avg_ltv=round(random.uniform(150, 800), 2),
                ))

            # create a completed experiment with results for demo purposes
            exp_a_price = round(random.uniform(60, 120), 0)
            exp_b_price = round(exp_a_price * random.uniform(1.05, 1.25), 0)
            exp = ExperimentModel(
                id=_uid(),
                organization_id=org_id,
                name=f"Price Test: {org_data['name']} {random.choice(['Camp', 'Clinic'])}",
                description="Testing a 15% price increase against the control price",
                status=ExperimentStatus.COMPLETED,
                variant_a_price=exp_a_price,
                variant_b_price=exp_b_price,
                traffic_split=0.5,
                start_date=date.today() - timedelta(days=45),
                end_date=date.today() - timedelta(days=15),
                results={
                    "variant_a": {
                        "bookings": random.randint(20, 45),
                        "revenue": round(exp_a_price * random.randint(20, 45), 2),
                        "conversion_rate": round(random.uniform(0.35, 0.65), 3),
                    },
                    "variant_b": {
                        "bookings": random.randint(18, 40),
                        "revenue": round(exp_b_price * random.randint(18, 40), 2),
                        "conversion_rate": round(random.uniform(0.30, 0.55), 3),
                    },
                    "winner": random.choice(["A", "B"]),
                    "lift_pct": round(random.uniform(5.0, 22.0), 1),
                },
                created_by=owner.id,
            )
            session.add(exp)

            # create 2-3 insight reports per org with realistic narrative text
            insight_templates = [
                {
                    "report_type": "weekly",
                    "period_days": 7,
                    "narrative": (
                        f"{org_data['name']} had a strong week with bookings tracking above the 30-day average. "
                        f"Utilization across all events reached a seasonal high, driven primarily by weekend camp sessions. "
                        f"No-show rate held steady at under 10%, which is within acceptable range. "
                        f"Three athletes booked their first event this week — consider a welcome outreach sequence to improve early retention."
                    ),
                    "highlights": {
                        "top_event": random.choice(CAMP_NAMES.get(sport, CAMP_NAMES["soccer"])),
                        "utilization_pct": round(random.uniform(72, 92), 1),
                        "new_athletes": random.randint(2, 6),
                        "revenue_vs_prior_week_pct": round(random.uniform(-5, 18), 1),
                    },
                    "alerts": None,
                },
                {
                    "report_type": "monthly",
                    "period_days": 30,
                    "narrative": (
                        f"Monthly review for {org_data['name']}: Revenue is up compared to the prior 30-day period, "
                        f"largely driven by strong performance in the {sport} camp segment. "
                        f"Cancellation rate nudged upward slightly — review refund policy messaging on the booking flow. "
                        f"Athlete LTV continues to grow month-over-month, suggesting good retention among returning bookers. "
                        f"Pricing engine flagged 4 events as candidates for a price increase based on fill-rate trajectory."
                    ),
                    "highlights": {
                        "revenue_growth_pct": round(random.uniform(3, 22), 1),
                        "top_coach": random.choice(coaches).full_name if coaches else "N/A",
                        "avg_ltv": round(random.uniform(200, 900), 2),
                        "pricing_opportunities": random.randint(2, 6),
                    },
                    "alerts": {
                        "cancellation_rate_flag": round(random.uniform(8, 18), 1),
                        "message": "Cancellation rate above 10% — consider reviewing cancellation policy or sending reminder emails 48h before events.",
                    },
                },
                {
                    "report_type": "weekly",
                    "period_days": 7,
                    "narrative": (
                        f"Slower week for {org_data['name']} — booking volume dipped relative to the prior period. "
                        f"This is consistent with seasonal patterns for {sport} in this region. "
                        f"Two high-rated coaches drove above-average ratings this week. "
                        f"Recommend promoting upcoming camps via email to athletes who haven't booked in 30+ days."
                    ),
                    "highlights": {
                        "bookings": random.randint(8, 25),
                        "avg_rating": round(random.uniform(4.0, 4.9), 1),
                        "inactive_athletes_flagged": random.randint(5, 20),
                    },
                    "alerts": {
                        "low_bookings_flag": True,
                        "message": "Booking volume is 15% below the 4-week average. Consider a limited-time promotion.",
                    },
                },
            ]

            today = date.today()
            for tmpl in random.sample(insight_templates, random.randint(2, 3)):
                period_end = today - timedelta(days=random.randint(1, 7))
                period_start = period_end - timedelta(days=tmpl["period_days"] - 1)
                session.add(InsightReport(
                    id=_uid(),
                    organization_id=org_id,
                    report_type=tmpl["report_type"],
                    period_start=period_start,
                    period_end=period_end,
                    narrative=tmpl["narrative"],
                    highlights=tmpl["highlights"],
                    alerts=tmpl["alerts"],
                ))

            # evaluations for this org
            sport = org_data["sport_type"]
            tmpl = sport_templates[sport]
            tmpl_cats = tmpl.categories  # list of {name, weight}
            eval_coach = coaches[0]  # use first coach for all seed evaluations
            eval_athletes = athletes[:8]  # first 8 athletes

            for athlete in eval_athletes:
                # generate 3 monthly evaluations (oldest to newest)
                base_scores = {cat["name"]: round(random.uniform(4.5, 8.0), 1) for cat in tmpl_cats}

                for month_offset in [3, 2, 1]:  # 3 months ago, 2 months ago, last month
                    period_end = date.today().replace(day=1) - timedelta(days=1) - timedelta(days=30 * (month_offset - 1))
                    period_start = period_end - timedelta(days=29)

                    # calculate scores for this period (progressive improvement)
                    period_scores = {}
                    for cat in tmpl_cats:
                        base = base_scores[cat["name"]]
                        # slight improvement each month
                        improvement = round(random.uniform(0.0, 0.4) * (3 - month_offset + 1), 1)
                        score = min(round(base + improvement, 1), 9.5)
                        period_scores[cat["name"]] = score

                    # weighted overall score
                    total_weight = sum(cat["weight"] for cat in tmpl_cats)
                    overall = round(sum(period_scores[cat["name"]] * cat["weight"] for cat in tmpl_cats) / total_weight, 2)

                    eval_obj = Evaluation(
                        id=_uid(),
                        organization_id=org.id,
                        athlete_id=athlete.id,
                        coach_id=eval_coach.id,
                        template_id=tmpl.id,
                        evaluation_type=EvaluationType.MONTHLY,
                        period_start=period_start,
                        period_end=period_end,
                        overall_score=overall,
                        status=EvaluationStatus.PUBLISHED,
                        ai_generated=True,
                        coach_notes=f"Consistent effort shown by {athlete.full_name} this period.",
                    )
                    session.add(eval_obj)
                    session.flush()

                    # add category rows
                    for i, cat in enumerate(tmpl_cats):
                        score = period_scores[cat["name"]]
                        # trend vs older period
                        if month_offset < 3:
                            old_score = base_scores[cat["name"]]
                            trend = "improving" if score > old_score + 0.3 else ("declining" if score < old_score - 0.3 else "stable")
                            prev_sc = old_score
                        else:
                            trend = "stable"
                            prev_sc = None

                        session.add(EvaluationCategory(
                            id=_uid(),
                            evaluation_id=eval_obj.id,
                            category_name=cat["name"],
                            score=score,
                            previous_score=prev_sc,
                            trend=trend,
                            display_order=i,
                            weight=cat["weight"],
                        ))

                    # generate AI narrative for published evaluations
                    cat_dicts = [
                        {
                            "category_name": cat["name"],
                            "score": period_scores[cat["name"]],
                            "previous_score": base_scores[cat["name"]] if month_offset < 3 else None,
                            "trend": "improving" if month_offset < 3 and period_scores[cat["name"]] > base_scores[cat["name"]] + 0.3 else "stable",
                            "notes": None,
                        }
                        for cat in tmpl_cats
                    ]
                    narrative_data = generate_narrative(
                        athlete_name=athlete.full_name,
                        coach_name=eval_coach.full_name,
                        sport_type=sport,
                        categories=cat_dicts,
                        overall_score=overall,
                        evaluation_type="monthly",
                    )
                    session.add(EvaluationNarrative(
                        id=_uid(),
                        evaluation_id=eval_obj.id,
                        summary=narrative_data["summary"],
                        strengths=narrative_data["strengths"],
                        areas_for_improvement=narrative_data["areas_for_improvement"],
                        recommendations=narrative_data["recommendations"],
                        parent_friendly_summary=narrative_data["parent_friendly_summary"],
                    ))

                # add one draft evaluation (current month) for variety
                period_start = date.today().replace(day=1)
                period_end = date.today()
                period_scores_draft = {cat["name"]: round(random.uniform(5.5, 9.0), 1) for cat in tmpl_cats}
                total_weight = sum(cat["weight"] for cat in tmpl_cats)
                overall_draft = round(sum(period_scores_draft[cat["name"]] * cat["weight"] for cat in tmpl_cats) / total_weight, 2)

                draft_eval = Evaluation(
                    id=_uid(),
                    organization_id=org.id,
                    athlete_id=athlete.id,
                    coach_id=eval_coach.id,
                    template_id=tmpl.id,
                    evaluation_type=EvaluationType.MONTHLY,
                    period_start=period_start,
                    period_end=period_end,
                    overall_score=overall_draft,
                    status=EvaluationStatus.DRAFT,
                    ai_generated=False,
                    coach_notes=None,
                )
                session.add(draft_eval)
                session.flush()

                for i, cat in enumerate(tmpl_cats):
                    session.add(EvaluationCategory(
                        id=_uid(),
                        evaluation_id=draft_eval.id,
                        category_name=cat["name"],
                        score=period_scores_draft[cat["name"]],
                        previous_score=None,
                        trend="stable",
                        display_order=i,
                        weight=cat["weight"],
                    ))

            session.flush()
            logger.info(f"  📊 Created evaluations for {len(eval_athletes)} athletes in {org_data['name']}")

            logger.info(f"  🏟️  {org_data['name']}: {len(coaches)} coaches, {len(athletes)} athletes")

        # seed some pricing recommendations across random events
        for event in random.sample(all_events, min(15, len(all_events))):
            pct = round(random.uniform(-20, 25), 1)
            suggested = round(event.current_price * (1 + pct / 100) / 5) * 5  # round to $5
            session.add(PricingRecommendation(
                id=_uid(), event_id=event.id, organization_id=event.organization_id,
                current_price=event.current_price, suggested_price=max(suggested, 10),
                confidence_score=random.randint(40, 95),
                price_change_pct=pct,
                expected_demand_change=round(random.uniform(-15, 20), 1),
                expected_revenue_change=round(random.uniform(-10, 30), 1),
                explanation=random.choice([
                    "High demand detected — historical fill rate above 85%. Consider increasing price.",
                    "Low fill rate with upcoming start date. A modest discount could boost bookings.",
                    "Coach rating above 4.5 supports premium pricing for this event.",
                    "Seasonal demand peak approaching. Similar events fill faster at this price point.",
                    "Competition proxy indicates moderate local supply. Current price is well-positioned.",
                ]),
                drivers={
                    "Historical Fill Rate": {
                        "value": f"{random.randint(60, 95)}%",
                        "impact": random.choice(["upward", "downward"]),
                        "weight": round(random.uniform(0.15, 0.40), 2),
                        "description": "Based on last 60 days of booking data for similar events",
                    },
                    "Days to Start": {
                        "value": f"{random.randint(3, 45)} days",
                        "impact": random.choice(["upward", "downward"]),
                        "weight": round(random.uniform(0.10, 0.25), 2),
                        "description": "Urgency premium increases as the event date approaches",
                    },
                    "Coach Rating": {
                        "value": f"{round(random.uniform(3.5, 5.0), 1)}/5.0",
                        "impact": "upward",
                        "weight": round(random.uniform(0.05, 0.20), 2),
                        "description": "Higher-rated coaches support premium pricing",
                    },
                    "Seasonality": {
                        "value": random.choice(["Peak Season", "Off Season", "Shoulder Season"]),
                        "impact": random.choice(["upward", "downward"]),
                        "weight": round(random.uniform(0.05, 0.15), 2),
                        "description": "Seasonal demand patterns based on historical data",
                    },
                },
            ))

        session.commit()
        logger.info(f"✅ Seed complete! {len(all_orgs)} orgs, {len(all_events)} events")
        logger.info("  📧 Login credentials:")
        logger.info("     Superadmin: admin@erebys.io / admin123")
        for org_data in ORGS:
            logger.info(f"     {org_data['name']} owner: owner@{org_data['slug']}.com / password123")
            logger.info(f"     {org_data['name']} coach: coach@{org_data['slug']}.com / password123")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Seed failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()

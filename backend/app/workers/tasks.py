"""
background tasks for nightly aggregation, weekly insights, and pricing refresh.
uses synchronous sqlalchemy since celery workers are sync.
"""

import logging
import uuid
from datetime import date, datetime, timedelta

from sqlalchemy import create_engine, select, func, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.workers.celery_app import celery_app
from app.models.organization import Organization
from app.models.event import Event
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.models.attendance import Attendance
from app.models.athlete import Athlete
from app.models.metrics import MetricsDaily
from app.models.insight import InsightReport

logger = logging.getLogger("erebys.workers")
settings = get_settings()

# sync engine for celery — can't use async here
_sync_engine = create_engine(settings.database_url_sync, pool_size=5, max_overflow=3)


def _get_sync_session() -> Session:
    return Session(_sync_engine)


@celery_app.task(name="app.workers.tasks.aggregate_daily_metrics", bind=True, max_retries=3)
def aggregate_daily_metrics(self, target_date: str | None = None):
    """
    rolls up daily kpis per org and writes them to metrics_daily.
    runs nightly at 1 am utc for the previous day.
    """
    metric_date = (
        date.fromisoformat(target_date) if target_date
        else date.today() - timedelta(days=1)
    )
    logger.info(f"📊 Aggregating metrics for {metric_date}")

    session = _get_sync_session()
    try:
        orgs = session.execute(select(Organization)).scalars().all()

        for org in orgs:
            org_id = org.id

            # booking and cancellation counts for the day
            bookings_q = (
                session.execute(
                    select(
                        func.count(Booking.id).label("booking_count"),
                        func.count().filter(Booking.status == BookingStatus.CANCELLED).label("cancel_count"),
                    )
                    .where(
                        Booking.organization_id == org_id,
                        func.date(Booking.booked_at) == metric_date,
                    )
                ).one()
            )
            booking_count = bookings_q.booking_count or 0
            cancel_count = bookings_q.cancel_count or 0

            # total revenue from completed payments on this day
            revenue_row = session.execute(
                select(func.coalesce(func.sum(Payment.amount), 0.0))
                .where(
                    Payment.organization_id == org_id,
                    Payment.status == PaymentStatus.COMPLETED,
                    func.date(Payment.paid_at) == metric_date,
                )
            ).scalar()
            total_revenue = float(revenue_row or 0)

            # events running on this date — used for capacity and utilization
            events_on_date = session.execute(
                select(Event)
                .where(
                    Event.organization_id == org_id,
                    Event.start_date <= metric_date,
                    func.coalesce(Event.end_date, Event.start_date) >= metric_date,
                )
            ).scalars().all()

            total_capacity = sum(e.capacity for e in events_on_date)
            total_booked = sum(e.booked_count for e in events_on_date)
            utilization = round(total_booked / total_capacity * 100, 1) if total_capacity > 0 else 0.0

            # no-show and late cancel counts for the day
            no_show_row = session.execute(
                select(
                    func.count().filter(Attendance.no_show.is_(True)).label("ns"),
                    func.count().filter(Attendance.late_cancel.is_(True)).label("lc"),
                    func.count().label("total"),
                )
                .join(Booking, Attendance.booking_id == Booking.id)
                .where(
                    Booking.organization_id == org_id,
                    func.date(Attendance.created_at) == metric_date,
                )
            ).one()
            no_show_count = no_show_row.ns or 0
            late_cancel_count = no_show_row.lc or 0
            att_total = no_show_row.total or 0
            no_show_rate = round(no_show_count / att_total * 100, 1) if att_total > 0 else 0.0

            # active athletes = anyone who booked in the last 30 days
            thirty_ago = metric_date - timedelta(days=30)
            active_athletes = session.execute(
                select(func.count(func.distinct(Booking.athlete_id)))
                .where(
                    Booking.organization_id == org_id,
                    func.date(Booking.booked_at).between(thirty_ago, metric_date),
                    Booking.status == BookingStatus.CONFIRMED,
                )
            ).scalar() or 0

            new_athletes = session.execute(
                select(func.count(Athlete.id))
                .where(
                    Athlete.organization_id == org_id,
                    func.date(Athlete.created_at) == metric_date,
                )
            ).scalar() or 0

            avg_ltv = session.execute(
                select(func.coalesce(func.avg(Athlete.ltv), 0.0))
                .where(Athlete.organization_id == org_id)
            ).scalar() or 0.0

            # upsert the daily metric row — update if it exists, insert if not
            existing = session.execute(
                select(MetricsDaily).where(
                    MetricsDaily.organization_id == org_id,
                    MetricsDaily.metric_date == metric_date,
                )
            ).scalar_one_or_none()

            if existing:
                existing.total_revenue = total_revenue
                existing.booking_count = booking_count
                existing.cancellation_count = cancel_count
                existing.total_capacity = total_capacity
                existing.total_booked = total_booked
                existing.utilization_rate = utilization
                existing.no_show_count = no_show_count
                existing.no_show_rate = no_show_rate
                existing.late_cancel_count = late_cancel_count
                existing.active_athletes = active_athletes
                existing.new_athletes = new_athletes
                existing.avg_ltv = round(float(avg_ltv), 2)
            else:
                session.add(MetricsDaily(
                    id=str(uuid.uuid4()),
                    organization_id=org_id,
                    metric_date=metric_date,
                    total_revenue=total_revenue,
                    booking_count=booking_count,
                    cancellation_count=cancel_count,
                    total_capacity=total_capacity,
                    total_booked=total_booked,
                    utilization_rate=utilization,
                    no_show_count=no_show_count,
                    no_show_rate=no_show_rate,
                    late_cancel_count=late_cancel_count,
                    active_athletes=active_athletes,
                    new_athletes=new_athletes,
                    avg_ltv=round(float(avg_ltv), 2),
                ))

        session.commit()
        logger.info(f"✅ Metrics aggregated for {len(orgs)} organizations on {metric_date}")
        return {"status": "ok", "date": str(metric_date), "orgs": len(orgs)}

    except Exception as exc:
        session.rollback()
        logger.error(f"❌ Metrics aggregation failed: {exc}")
        raise self.retry(exc=exc, countdown=60)
    finally:
        session.close()


@celery_app.task(name="app.workers.tasks.generate_weekly_insights", bind=True, max_retries=2)
def generate_weekly_insights(self):
    """
    generates narrative weekly insight reports per org from the metrics_daily table.
    runs monday 6 am utc.
    """
    logger.info("📝 Generating weekly insights…")
    session = _get_sync_session()

    try:
        orgs = session.execute(select(Organization)).scalars().all()
        period_end = date.today() - timedelta(days=1)
        period_start = period_end - timedelta(days=6)

        for org in orgs:
            # grab the daily metrics rows for this period
            metrics = session.execute(
                select(MetricsDaily)
                .where(
                    MetricsDaily.organization_id == org.id,
                    MetricsDaily.metric_date.between(period_start, period_end),
                )
                .order_by(MetricsDaily.metric_date)
            ).scalars().all()

            if not metrics:
                continue

            total_rev = sum(m.total_revenue for m in metrics)
            avg_util = round(sum(m.utilization_rate for m in metrics) / len(metrics), 1)
            avg_noshow = round(sum(m.no_show_rate for m in metrics) / len(metrics), 1)
            total_bookings = sum(m.booking_count for m in metrics)
            total_cancels = sum(m.cancellation_count for m in metrics)

            # summary numbers for the highlights field
            highlights = {
                "total_revenue": total_rev,
                "total_bookings": total_bookings,
                "avg_utilization": avg_util,
                "avg_no_show_rate": avg_noshow,
                "total_cancellations": total_cancels,
            }

            # flag anything that looks off
            alerts = []
            if avg_noshow > 15:
                alerts.append({"type": "high_no_show", "message": f"No-show rate at {avg_noshow}% — consider reminders or deposits"})
            if avg_util < 40:
                alerts.append({"type": "low_utilization", "message": f"Utilization at {avg_util}% — consider price adjustments or marketing"})

            # build the narrative text
            rev_emoji = "📈" if total_rev > 0 else "📉"
            narrative = (
                f"## Weekly Intelligence Report — {org.name}\n"
                f"**{period_start.strftime('%b %d')} – {period_end.strftime('%b %d, %Y')}**\n\n"
                f"{rev_emoji} **Revenue**: ${total_rev:,.0f} from {total_bookings} bookings\n\n"
                f"**Utilization**: {avg_util}% average capacity filled\n\n"
                f"**No-Show Rate**: {avg_noshow}%\n\n"
            )

            if alerts:
                narrative += "### ⚠️ Alerts\n"
                for a in alerts:
                    narrative += f"- {a['message']}\n"

            session.add(InsightReport(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                report_type="weekly",
                period_start=period_start,
                period_end=period_end,
                narrative=narrative,
                highlights=highlights,
                alerts={"items": alerts} if alerts else None,
            ))

        session.commit()
        logger.info(f"✅ Weekly insights generated for {len(orgs)} organizations")
        return {"status": "ok", "orgs": len(orgs)}

    except Exception as exc:
        session.rollback()
        logger.error(f"❌ Weekly insights failed: {exc}")
        raise self.retry(exc=exc, countdown=120)
    finally:
        session.close()


@celery_app.task(name="app.workers.tasks.refresh_pricing_recommendations", bind=True, max_retries=2)
def refresh_pricing_recommendations(self):
    """
    recalculates pricing recommendations for all active/published events.
    runs nightly at 3 am utc.
    """
    from app.services.ml_engine import PricingEngine

    logger.info("💰 Refreshing pricing recommendations…")
    session = _get_sync_session()

    try:
        orgs = session.execute(select(Organization)).scalars().all()
        total_recs = 0

        for org in orgs:
            events = session.execute(
                select(Event).where(
                    Event.organization_id == org.id,
                    Event.status.in_(["published", "full"]),
                    Event.start_date >= date.today(),
                )
            ).scalars().all()

            engine = PricingEngine()

            for event in events:
                bookings = session.execute(
                    select(Booking).where(Booking.event_id == event.id)
                ).scalars().all()

                rec = engine.generate_recommendation(
                    event=event,
                    bookings=bookings,
                    competition_proxy=org.competition_proxy,
                )

                from app.models.pricing import PricingRecommendation
                session.add(PricingRecommendation(
                    id=str(uuid.uuid4()),
                    event_id=event.id,
                    organization_id=org.id,
                    current_price=event.current_price,
                    suggested_price=rec["suggested_price"],
                    confidence_score=rec["confidence"],
                    price_change_pct=rec["price_change_pct"],
                    expected_demand_change=rec.get("expected_demand_change", 0),
                    expected_revenue_change=rec.get("expected_revenue_change", 0),
                    explanation=rec["explanation"],
                    drivers=rec.get("drivers"),
                    model_version="v1.0",
                ))
                total_recs += 1

        session.commit()
        logger.info(f"✅ Generated {total_recs} pricing recommendations")
        return {"status": "ok", "recommendations": total_recs}

    except Exception as exc:
        session.rollback()
        logger.error(f"❌ Pricing refresh failed: {exc}")
        raise self.retry(exc=exc, countdown=120)
    finally:
        session.close()

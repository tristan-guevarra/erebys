"""
insight report generator.
creates weekly narrative summaries of academy performance.
no llm dependency — uses template-based generation with data-driven insights.
"""

from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.payment import Payment, PaymentStatus
from app.models.booking import Booking, BookingStatus
from app.models.event import Event
from app.models.attendance import Attendance
from app.models.athlete import Athlete
from app.models.insight import InsightReport


async def generate_weekly_insight(db: AsyncSession, org_id: str) -> InsightReport:
    """builds a weekly insight report for an org — pulls metrics and writes a narrative"""
    today = date.today()
    week_start = today - timedelta(days=7)

    # pull all the numbers we need for the report
    revenue = await _get_period_revenue(db, org_id, week_start, today)
    prev_revenue = await _get_period_revenue(db, org_id, week_start - timedelta(days=7), week_start)
    bookings = await _get_period_bookings(db, org_id, week_start, today)
    prev_bookings = await _get_period_bookings(db, org_id, week_start - timedelta(days=7), week_start)
    no_show_rate = await _get_period_no_show_rate(db, org_id, week_start, today)
    top_events = await _get_top_events(db, org_id, week_start, today)
    at_risk_events = await _get_underperforming_events(db, org_id)

    # figure out revenue direction for the header
    rev_change = ((revenue - prev_revenue) / max(prev_revenue, 1)) * 100
    rev_direction = "up" if rev_change > 0 else "down"
    rev_emoji = "📈" if rev_change > 0 else "📉"

    # build the narrative text block
    narrative_parts = [
        f"## Weekly Performance Summary ({week_start.strftime('%b %d')} — {today.strftime('%b %d, %Y')})\n",
        f"{rev_emoji} **Revenue**: ${revenue:,.0f} ({rev_direction} {abs(rev_change):.1f}% vs prior week)",
        f"📋 **Bookings**: {bookings} ({'↑' if bookings > prev_bookings else '↓'} from {prev_bookings})",
        f"🚫 **No-Show Rate**: {no_show_rate:.1f}%\n",
    ]

    if top_events:
        narrative_parts.append("### Top Performing Events")
        for i, evt in enumerate(top_events[:3], 1):
            narrative_parts.append(
                f"{i}. **{evt['title']}** — ${evt['revenue']:,.0f} revenue, "
                f"{evt['utilization']:.0f}% filled"
            )

    if at_risk_events:
        narrative_parts.append("\n### ⚠️ Attention Needed")
        for evt in at_risk_events[:3]:
            narrative_parts.append(
                f"- **{evt['title']}** — Only {evt['utilization']:.0f}% booked "
                f"(starts {evt['start_date']}). Consider a price adjustment or promotion."
            )

    # key numbers summary for the highlights field
    highlights = {
        "revenue": revenue,
        "revenue_change_pct": round(rev_change, 1),
        "bookings": bookings,
        "no_show_rate": round(no_show_rate, 1),
        "top_event": top_events[0]["title"] if top_events else None,
    }

    # flag anything that needs attention
    alerts = {}
    if no_show_rate > 15:
        alerts["high_no_show"] = f"No-show rate at {no_show_rate:.1f}% — above 15% threshold"
    if rev_change < -20:
        alerts["revenue_drop"] = f"Revenue dropped {abs(rev_change):.1f}% week-over-week"
    for evt in at_risk_events[:2]:
        alerts[f"low_fill_{evt['id'][:8]}"] = f"{evt['title']} at {evt['utilization']:.0f}% capacity"

    narrative = "\n".join(narrative_parts)

    report = InsightReport(
        organization_id=org_id,
        report_type="weekly",
        period_start=week_start,
        period_end=today,
        narrative=narrative,
        highlights=highlights,
        alerts=alerts if alerts else None,
    )
    db.add(report)
    await db.flush()
    return report


async def _get_period_revenue(db: AsyncSession, org_id: str, start: date, end: date) -> float:
    result = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0))
        .where(
            Payment.organization_id == org_id,
            Payment.status == PaymentStatus.COMPLETED,
            func.date(Payment.paid_at) >= start,
            func.date(Payment.paid_at) < end,
        )
    )
    return float(result.scalar())


async def _get_period_bookings(db: AsyncSession, org_id: str, start: date, end: date) -> int:
    result = await db.execute(
        select(func.count(Booking.id))
        .where(
            Booking.organization_id == org_id,
            Booking.status == BookingStatus.CONFIRMED,
            func.date(Booking.booked_at) >= start,
            func.date(Booking.booked_at) < end,
        )
    )
    return result.scalar() or 0


async def _get_period_no_show_rate(db: AsyncSession, org_id: str, start: date, end: date) -> float:
    result = await db.execute(
        select(
            func.count(Attendance.id),
            func.sum(func.cast(Attendance.no_show, sa.Integer)),
        )
        .join(Booking, Booking.id == Attendance.booking_id)
        .where(
            Booking.organization_id == org_id,
            func.date(Booking.booked_at) >= start,
            func.date(Booking.booked_at) < end,
        )
    )
    total, no_shows = result.one()
    if not total:
        return 0.0
    return (no_shows or 0) / total * 100


async def _get_top_events(db: AsyncSession, org_id: str, start: date, end: date) -> list[dict]:
    result = await db.execute(
        select(
            Event.id, Event.title,
            func.coalesce(func.sum(Payment.amount), 0).label("revenue"),
            Event.booked_count, Event.capacity,
        )
        .join(Booking, Booking.event_id == Event.id)
        .join(Payment, Payment.booking_id == Booking.id)
        .where(
            Event.organization_id == org_id,
            func.date(Payment.paid_at) >= start,
            func.date(Payment.paid_at) < end,
        )
        .group_by(Event.id, Event.title, Event.booked_count, Event.capacity)
        .order_by(func.sum(Payment.amount).desc())
        .limit(5)
    )
    return [
        {
            "id": r.id,
            "title": r.title,
            "revenue": float(r.revenue),
            "utilization": r.booked_count / max(r.capacity, 1) * 100,
        }
        for r in result.all()
    ]


async def _get_underperforming_events(db: AsyncSession, org_id: str) -> list[dict]:
    result = await db.execute(
        select(Event)
        .where(
            Event.organization_id == org_id,
            Event.status == "published",
            Event.start_date > date.today(),
            Event.start_date < date.today() + timedelta(days=14),
        )
    )
    events = result.scalars().all()
    at_risk = []
    for e in events:
        util = e.booked_count / max(e.capacity, 1) * 100
        if util < 50:
            at_risk.append({
                "id": e.id,
                "title": e.title,
                "utilization": util,
                "start_date": e.start_date.strftime("%b %d"),
            })
    return sorted(at_risk, key=lambda x: x["utilization"])


# fix: need to import sa for the cast
import sqlalchemy as sa

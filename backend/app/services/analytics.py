from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, and_, extract
from app.models.booking import Booking, BookingStatus
from app.models.event import Event
from app.models.payment import Payment, PaymentStatus
from app.models.attendance import Attendance
from app.models.athlete import Athlete
from app.models.rating import Rating
from app.models.metrics import MetricsDaily
from app.schemas.analytics import (
    OverviewKPIs,
    RevenueByDay,
    CohortRow,
    AthleteLTVBucket,
    NoShowRisk,
)
from app.schemas.event import EventPerformance


async def get_overview_kpis(db: AsyncSession, org_id: str, days: int = 30) -> OverviewKPIs:
    """crunches the main kpi numbers for the dashboard overview card"""
    now = date.today()
    period_start = now - timedelta(days=days)
    prev_start = period_start - timedelta(days=days)

    # current period revenue
    cur_rev = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0))
        .where(
            Payment.organization_id == org_id,
            Payment.status == PaymentStatus.COMPLETED,
            func.date(Payment.paid_at) >= period_start,
        )
    )
    total_revenue = float(cur_rev.scalar())

    # previous period revenue so we can compute the % change
    prev_rev = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0))
        .where(
            Payment.organization_id == org_id,
            Payment.status == PaymentStatus.COMPLETED,
            func.date(Payment.paid_at) >= prev_start,
            func.date(Payment.paid_at) < period_start,
        )
    )
    prev_revenue = float(prev_rev.scalar())
    revenue_change = _pct_change(total_revenue, prev_revenue)

    # bookings count for current period
    cur_bookings = await db.execute(
        select(func.count(Booking.id))
        .where(
            Booking.organization_id == org_id,
            Booking.status == BookingStatus.CONFIRMED,
            func.date(Booking.booked_at) >= period_start,
        )
    )
    total_bookings = cur_bookings.scalar() or 0

    prev_bookings = await db.execute(
        select(func.count(Booking.id))
        .where(
            Booking.organization_id == org_id,
            Booking.status == BookingStatus.CONFIRMED,
            func.date(Booking.booked_at) >= prev_start,
            func.date(Booking.booked_at) < period_start,
        )
    )
    prev_booking_count = prev_bookings.scalar() or 0
    bookings_change = _pct_change(total_bookings, prev_booking_count)

    # utilization rate across all events in the period
    util_result = await db.execute(
        select(
            func.coalesce(func.sum(Event.booked_count), 0),
            func.coalesce(func.sum(Event.capacity), 1),
        )
        .where(
            Event.organization_id == org_id,
            Event.start_date >= period_start,
        )
    )
    booked_sum, capacity_sum = util_result.one()
    utilization_rate = round(float(booked_sum) / max(float(capacity_sum), 1) * 100, 1)

    # no-show rate from attendance records
    attendance_result = await db.execute(
        select(
            func.count(Attendance.id),
            func.sum(case((Attendance.no_show == True, 1), else_=0)),  # noqa: E712
        )
        .join(Booking, Booking.id == Attendance.booking_id)
        .where(Booking.organization_id == org_id, func.date(Booking.booked_at) >= period_start)
    )
    total_att, no_shows = attendance_result.one()
    no_show_rate = round(float(no_shows or 0) / max(total_att or 1, 1) * 100, 1)

    # count of unique athletes who booked in the period
    active_result = await db.execute(
        select(func.count(func.distinct(Booking.athlete_id)))
        .where(
            Booking.organization_id == org_id,
            Booking.status == BookingStatus.CONFIRMED,
            func.date(Booking.booked_at) >= period_start,
        )
    )
    active_athletes = active_result.scalar() or 0

    # average ltv across all athletes with any spend
    ltv_result = await db.execute(
        select(func.coalesce(func.avg(Athlete.ltv), 0))
        .where(Athlete.organization_id == org_id, Athlete.ltv > 0)
    )
    avg_ltv = round(float(ltv_result.scalar()), 2)

    # cancellation rate as a % of all bookings attempted
    cancel_result = await db.execute(
        select(func.count(Booking.id))
        .where(
            Booking.organization_id == org_id,
            Booking.status == BookingStatus.CANCELLED,
            func.date(Booking.booked_at) >= period_start,
        )
    )
    cancellations = cancel_result.scalar() or 0
    total_all_bookings = total_bookings + cancellations
    cancellation_rate = round(cancellations / max(total_all_bookings, 1) * 100, 1)

    return OverviewKPIs(
        total_revenue=total_revenue,
        revenue_change=revenue_change,
        total_bookings=total_bookings,
        bookings_change=bookings_change,
        utilization_rate=utilization_rate,
        utilization_change=0.0,
        no_show_rate=no_show_rate,
        no_show_change=0.0,
        active_athletes=active_athletes,
        athletes_change=0.0,
        avg_ltv=avg_ltv,
        ltv_change=0.0,
        cancellation_rate=cancellation_rate,
        cancellation_change=0.0,
    )


async def get_revenue_by_day(db: AsyncSession, org_id: str, days: int = 30) -> list[RevenueByDay]:
    """breaks down revenue day by day so you can see trends on the chart"""
    period_start = date.today() - timedelta(days=days)
    result = await db.execute(
        select(
            func.date(Payment.paid_at).label("day"),
            func.coalesce(func.sum(Payment.amount), 0).label("revenue"),
            func.count(Payment.id).label("bookings"),
        )
        .where(
            Payment.organization_id == org_id,
            Payment.status == PaymentStatus.COMPLETED,
            func.date(Payment.paid_at) >= period_start,
        )
        .group_by(func.date(Payment.paid_at))
        .order_by(func.date(Payment.paid_at))
    )
    rows = result.all()
    return [RevenueByDay(date=r.day, revenue=float(r.revenue), bookings=r.bookings) for r in rows]


async def get_event_performance(db: AsyncSession, org_id: str) -> list[EventPerformance]:
    """computes revenue, bookings, and attendance stats for each recent event"""
    events_result = await db.execute(
        select(Event).where(Event.organization_id == org_id).order_by(Event.start_date.desc()).limit(50)
    )
    events = events_result.scalars().all()
    performances = []

    for event in events:
        # revenue from completed payments for this event
        rev_result = await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0))
            .join(Booking, Booking.id == Payment.booking_id)
            .where(Booking.event_id == event.id, Payment.status == PaymentStatus.COMPLETED)
        )
        revenue = float(rev_result.scalar())

        # confirmed booking count
        book_result = await db.execute(
            select(func.count(Booking.id))
            .where(Booking.event_id == event.id, Booking.status == BookingStatus.CONFIRMED)
        )
        booking_count = book_result.scalar() or 0

        # no-show rate from attendance records
        att_result = await db.execute(
            select(
                func.count(Attendance.id),
                func.sum(case((Attendance.no_show == True, 1), else_=0)),  # noqa: E712
            )
            .join(Booking, Booking.id == Attendance.booking_id)
            .where(Booking.event_id == event.id)
        )
        total_att, no_shows = att_result.one()
        no_show_rate = round(float(no_shows or 0) / max(total_att or 1, 1) * 100, 1)

        # average rating for this event
        rating_result = await db.execute(
            select(func.coalesce(func.avg(Rating.score), 0))
            .where(Rating.event_id == event.id)
        )
        avg_rating = round(float(rating_result.scalar()), 1)

        # cancellation rate
        cancel_result = await db.execute(
            select(func.count(Booking.id))
            .where(Booking.event_id == event.id, Booking.status == BookingStatus.CANCELLED)
        )
        cancellations = cancel_result.scalar() or 0
        total_all = booking_count + cancellations
        cancellation_rate = round(cancellations / max(total_all, 1) * 100, 1)

        performances.append(EventPerformance(
            event_id=event.id,
            title=event.title,
            event_type=event.event_type.value if hasattr(event.event_type, 'value') else event.event_type,
            revenue=revenue,
            bookings=booking_count,
            capacity=event.capacity,
            utilization_rate=round(booking_count / max(event.capacity, 1) * 100, 1),
            no_show_rate=no_show_rate,
            avg_rating=avg_rating,
            cancellation_rate=cancellation_rate,
        ))

    return performances


async def get_cohort_retention(db: AsyncSession, org_id: str, months: int = 6) -> list[CohortRow]:
    """groups athletes by their first booking month and tracks how many keep coming back"""
    # get each athlete's first booking month to define their cohort
    result = await db.execute(
        select(
            Athlete.id,
            func.date_trunc("month", func.min(Booking.booked_at)).label("cohort_month"),
        )
        .join(Booking, and_(Booking.athlete_id == Athlete.id, Booking.organization_id == org_id))
        .where(Athlete.organization_id == org_id, Booking.status == BookingStatus.CONFIRMED)
        .group_by(Athlete.id)
    )
    athlete_cohorts = result.all()

    if not athlete_cohorts:
        return []

    # map each cohort month to its set of athlete ids
    cohort_map: dict[str, set[str]] = {}
    for athlete_id, cohort_month in athlete_cohorts:
        key = cohort_month.strftime("%Y-%m") if cohort_month else "unknown"
        if key not in cohort_map:
            cohort_map[key] = set()
        cohort_map[key].add(athlete_id)

    # for each cohort, check how many athletes came back in subsequent months
    cohort_rows = []
    for cohort_key in sorted(cohort_map.keys())[-months:]:
        cohort_athletes = cohort_map[cohort_key]
        cohort_size = len(cohort_athletes)
        retention = [100.0]  # month 0 is always 100%

        for m in range(1, months):
            # check how many from this cohort booked in month m
            target_month = _add_months(cohort_key, m)
            active_in_month = await db.execute(
                select(func.count(func.distinct(Booking.athlete_id)))
                .where(
                    Booking.organization_id == org_id,
                    Booking.athlete_id.in_(cohort_athletes),
                    func.to_char(Booking.booked_at, "YYYY-MM") == target_month,
                    Booking.status == BookingStatus.CONFIRMED,
                )
            )
            active = active_in_month.scalar() or 0
            retention.append(round(active / max(cohort_size, 1) * 100, 1))

        cohort_rows.append(CohortRow(
            cohort_month=cohort_key,
            cohort_size=cohort_size,
            retention=retention,
        ))

    return cohort_rows


async def get_athlete_ltv_distribution(db: AsyncSession, org_id: str) -> list[AthleteLTVBucket]:
    """buckets athletes by lifetime value so you can see how spend is distributed"""
    result = await db.execute(
        select(Athlete.ltv).where(Athlete.organization_id == org_id, Athlete.ltv > 0)
    )
    ltvs = [float(r[0]) for r in result.all()]

    buckets = [
        ("$0-100", 0, 100),
        ("$100-250", 100, 250),
        ("$250-500", 250, 500),
        ("$500-1000", 500, 1000),
        ("$1000+", 1000, float("inf")),
    ]

    distribution = []
    for label, low, high in buckets:
        in_bucket = [v for v in ltvs if low <= v < high]
        distribution.append(AthleteLTVBucket(
            bucket=label,
            count=len(in_bucket),
            total_ltv=round(sum(in_bucket), 2),
            avg_ltv=round(sum(in_bucket) / len(in_bucket), 2) if in_bucket else 0.0,
        ))

    return distribution


async def get_no_show_risks(db: AsyncSession, org_id: str, limit: int = 20) -> list[NoShowRisk]:
    """returns athletes most likely to no-show, ranked by their historical rate"""
    result = await db.execute(
        select(Athlete)
        .where(Athlete.organization_id == org_id, Athlete.total_bookings > 0)
        .order_by(Athlete.no_show_rate.desc())
        .limit(limit)
    )
    athletes = result.scalars().all()

    risks = []
    for athlete in athletes:
        risk_score = min(athlete.no_show_rate / 100.0, 1.0)
        if risk_score > 0.3:
            level = "high"
        elif risk_score > 0.15:
            level = "medium"
        else:
            level = "low"

        factors = []
        if athlete.no_show_rate > 20:
            factors.append(f"Historical no-show rate: {athlete.no_show_rate:.0f}%")
        if athlete.total_bookings < 3:
            factors.append("Low booking history (less reliable prediction)")
        if athlete.last_booking_date and (date.today() - athlete.last_booking_date).days > 60:
            factors.append("Inactive for 60+ days")

        risks.append(NoShowRisk(
            athlete_id=athlete.id,
            athlete_name=athlete.full_name,
            risk_score=round(risk_score, 3),
            risk_level=level,
            total_bookings=athlete.total_bookings or 0,
            no_show_rate=athlete.no_show_rate or 0.0,
            top_factors=factors if factors else ["Within normal range"],
        ))

    return risks


def _pct_change(current: float, previous: float) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round((current - previous) / previous * 100, 1)


def _add_months(ym: str, months: int) -> str:
    year, month = int(ym[:4]), int(ym[5:7])
    month += months
    while month > 12:
        month -= 12
        year += 1
    return f"{year:04d}-{month:02d}"

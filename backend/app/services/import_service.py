"""csv import service for bulk data ingestion."""

import csv
import io
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.event import Event, EventType, EventStatus
from app.models.booking import Booking, BookingStatus, BookingSource
from app.models.payment import Payment, PaymentStatus
from app.models.audit import AuditLog


async def import_events_csv(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    csv_content: str,
) -> dict:
    """reads a csv and creates events — expected columns: title, event_type, capacity, base_price, start_date, end_date, start_time, end_time, location"""
    reader = csv.DictReader(io.StringIO(csv_content))
    created = 0
    errors = []

    for i, row in enumerate(reader, 1):
        try:
            event = Event(
                id=str(uuid.uuid4()),
                organization_id=org_id,
                title=row["title"].strip(),
                event_type=EventType(row.get("event_type", "camp").strip().lower()),
                capacity=int(row.get("capacity", 20)),
                base_price=float(row["base_price"]),
                current_price=float(row.get("current_price", row["base_price"])),
                start_date=datetime.strptime(row["start_date"].strip(), "%Y-%m-%d").date(),
                end_date=datetime.strptime(row["end_date"].strip(), "%Y-%m-%d").date() if row.get("end_date") else None,
                start_time=row.get("start_time", "09:00").strip(),
                end_time=row.get("end_time", "12:00").strip(),
                location=row.get("location", "").strip() or None,
                status=EventStatus.PUBLISHED,
            )
            db.add(event)
            created += 1
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")

    # write an audit entry so we know who imported what
    db.add(AuditLog(
        organization_id=org_id,
        user_id=user_id,
        action="data_import",
        resource_type="events",
        details={"created": created, "errors": len(errors)},
    ))

    await db.flush()
    return {"created": created, "errors": errors}


async def import_bookings_csv(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    csv_content: str,
) -> dict:
    """reads a csv and creates bookings — expected columns: event_id, athlete_id, price_paid, status, booked_at"""
    reader = csv.DictReader(io.StringIO(csv_content))
    created = 0
    errors = []

    for i, row in enumerate(reader, 1):
        try:
            booking = Booking(
                id=str(uuid.uuid4()),
                event_id=row["event_id"].strip(),
                athlete_id=row["athlete_id"].strip(),
                organization_id=org_id,
                price_paid=float(row["price_paid"]),
                status=BookingStatus(row.get("status", "confirmed").strip().lower()),
                source=BookingSource.IMPORT,
                booked_at=datetime.strptime(row.get("booked_at", datetime.utcnow().isoformat()[:19]), "%Y-%m-%dT%H:%M:%S"),
            )
            db.add(booking)

            # auto-create a completed payment for each imported booking
            payment = Payment(
                id=str(uuid.uuid4()),
                booking_id=booking.id,
                organization_id=org_id,
                amount=booking.price_paid,
                status=PaymentStatus.COMPLETED,
            )
            db.add(payment)
            created += 1
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")

    db.add(AuditLog(
        organization_id=org_id,
        user_id=user_id,
        action="data_import",
        resource_type="bookings",
        details={"created": created, "errors": len(errors)},
    ))

    await db.flush()
    return {"created": created, "errors": errors}

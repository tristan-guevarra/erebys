import io
import csv
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.api.deps import get_org_id, require_admin, require_manager_or_above
from app.services.import_service import import_events_csv, import_bookings_csv
from app.services.analytics import get_event_performance, get_cohort_retention

router = APIRouter(tags=["Imports & Exports"])


@router.post("/imports/events")
async def import_events(
    file: UploadFile = File(...),
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    content = (await file.read()).decode("utf-8")
    result = await import_events_csv(db, org_id, user.id, content)
    return result


@router.post("/imports/bookings")
async def import_bookings(
    file: UploadFile = File(...),
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    content = (await file.read()).decode("utf-8")
    result = await import_bookings_csv(db, org_id, user.id, content)
    return result


@router.get("/exports/events")
async def export_events(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    db: AsyncSession = Depends(get_db),
):
    """dumps event performance data to a csv file for download"""
    performances = await get_event_performance(db, org_id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Event", "Type", "Revenue", "Bookings", "Capacity", "Utilization %", "No-Show %", "Avg Rating", "Cancellation %"])
    for p in performances:
        writer.writerow([p.title, p.event_type, p.revenue, p.bookings, p.capacity, p.utilization_rate, p.no_show_rate, p.avg_rating, p.cancellation_rate])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=event_performance.csv"},
    )


@router.get("/exports/cohorts")
async def export_cohorts(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    db: AsyncSession = Depends(get_db),
):
    """dumps cohort retention data to a csv file for download"""
    cohorts = await get_cohort_retention(db, org_id)

    output = io.StringIO()
    writer = csv.writer(output)

    max_months = max((len(c.retention) for c in cohorts), default=0)
    header = ["Cohort", "Size"] + [f"Month {i}" for i in range(max_months)]
    writer.writerow(header)
    for c in cohorts:
        writer.writerow([c.cohort_month, c.cohort_size] + c.retention)

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cohort_retention.csv"},
    )

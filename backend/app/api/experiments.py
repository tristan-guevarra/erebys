from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.experiment import Experiment, ExperimentAssignment, ExperimentStatus
from app.models.user import User
from app.schemas.pricing import ExperimentCreate, ExperimentResponse
from app.api.deps import get_org_id, require_admin

router = APIRouter(prefix="/experiments", tags=["Experiments"])


@router.get("", response_model=list[ExperimentResponse])
async def list_experiments(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Experiment)
        .where(Experiment.organization_id == org_id)
        .order_by(Experiment.created_at.desc())
    )
    return [ExperimentResponse.model_validate(e) for e in result.scalars().all()]


@router.post("", response_model=ExperimentResponse, status_code=201)
async def create_experiment(
    body: ExperimentCreate,
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    exp = Experiment(
        organization_id=org_id,
        name=body.name,
        description=body.description,
        event_id=body.event_id,
        variant_a_price=body.variant_a_price,
        variant_b_price=body.variant_b_price,
        traffic_split=body.traffic_split,
        created_by=user.id,
    )
    db.add(exp)
    await db.flush()
    return ExperimentResponse.model_validate(exp)


@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(
    experiment_id: str,
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Experiment).where(
            Experiment.id == experiment_id,
            Experiment.organization_id == org_id,
        )
    )
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return ExperimentResponse.model_validate(exp)


@router.post("/{experiment_id}/start", response_model=ExperimentResponse)
async def start_experiment(
    experiment_id: str,
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Experiment).where(
            Experiment.id == experiment_id,
            Experiment.organization_id == org_id,
        )
    )
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    exp.status = ExperimentStatus.RUNNING
    await db.flush()
    return ExperimentResponse.model_validate(exp)


@router.get("/{experiment_id}/results")
async def experiment_results(
    experiment_id: str,
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """pulls the a/b test results and tallies conversions per variant"""
    result = await db.execute(
        select(Experiment).where(
            Experiment.id == experiment_id,
            Experiment.organization_id == org_id,
        )
    )
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    # aggregate per variant so we can compare them
    for variant in ["A", "B"]:
        agg = await db.execute(
            select(
                func.count(ExperimentAssignment.id).label("total"),
                func.sum(func.cast(ExperimentAssignment.converted, db.bind.dialect.name == "postgresql" and "integer" or "int")).label("conversions"),
                func.sum(ExperimentAssignment.revenue).label("total_revenue"),
            )
            .where(
                ExperimentAssignment.experiment_id == experiment_id,
                ExperimentAssignment.variant == variant,
            )
        )
        row = agg.one()

    # grab all assignments and split by variant for the response
    assignments = await db.execute(
        select(ExperimentAssignment).where(ExperimentAssignment.experiment_id == experiment_id)
    )
    all_assignments = assignments.scalars().all()

    variant_a = [a for a in all_assignments if a.variant == "A"]
    variant_b = [a for a in all_assignments if a.variant == "B"]

    return {
        "experiment_id": experiment_id,
        "variant_a": {
            "price": exp.variant_a_price,
            "sample_size": len(variant_a),
            "conversions": sum(1 for a in variant_a if a.converted),
            "conversion_rate": round(sum(1 for a in variant_a if a.converted) / max(len(variant_a), 1) * 100, 1),
            "total_revenue": round(sum(a.revenue for a in variant_a), 2),
        },
        "variant_b": {
            "price": exp.variant_b_price,
            "sample_size": len(variant_b),
            "conversions": sum(1 for a in variant_b if a.converted),
            "conversion_rate": round(sum(1 for a in variant_b if a.converted) / max(len(variant_b), 1) * 100, 1),
            "total_revenue": round(sum(a.revenue for a in variant_b), 2),
        },
        "status": exp.status.value if hasattr(exp.status, "value") else exp.status,
    }

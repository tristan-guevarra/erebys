from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.api.deps import get_org_id, get_current_user
from app.schemas.evaluation import EvaluationCreate, EvaluationUpdate
import app.services.evaluation as svc

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.get("")
async def list_evaluations(
    status: str | None = None,
    athlete_id: str | None = None,
    org_id: str = Depends(get_org_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await svc.list_evaluations(db, org_id, status=status, athlete_id=athlete_id)


@router.get("/stats")
async def get_stats(
    org_id: str = Depends(get_org_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await svc.get_eval_stats(db, org_id)


@router.get("/templates")
async def list_templates(
    org_id: str = Depends(get_org_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    templates = await svc.get_evaluation_templates(db, org_id)
    return [
        {
            "id": t.id,
            "organization_id": t.organization_id,
            "sport_type": t.sport_type,
            "name": t.name,
            "categories": t.categories,
            "is_default": t.is_default,
        }
        for t in templates
    ]


@router.get("/athlete/{athlete_id}")
async def athlete_evaluations(
    athlete_id: str,
    org_id: str = Depends(get_org_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await svc.get_athlete_evaluations(db, athlete_id, org_id)


@router.get("/{eval_id}")
async def get_evaluation(
    eval_id: str,
    org_id: str = Depends(get_org_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await svc.get_evaluation(db, eval_id, org_id)
    if not result:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return result


@router.post("", status_code=201)
async def create_evaluation(
    body: EvaluationCreate,
    org_id: str = Depends(get_org_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await svc.create_evaluation(db, org_id, body)


@router.patch("/{eval_id}")
async def update_evaluation(
    eval_id: str,
    body: EvaluationUpdate,
    org_id: str = Depends(get_org_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await svc.update_evaluation(db, eval_id, org_id, body)
    if not result:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return result


@router.post("/{eval_id}/generate-narrative")
async def generate_narrative(
    eval_id: str,
    org_id: str = Depends(get_org_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await svc.generate_ai_narrative(db, eval_id, org_id)
    if not result:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return result


@router.post("/{eval_id}/publish")
async def publish_evaluation(
    eval_id: str,
    org_id: str = Depends(get_org_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await svc.publish_evaluation(db, eval_id, org_id)
    if not result:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return result

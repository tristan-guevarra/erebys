import uuid
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.evaluation import Evaluation, EvaluationCategory, EvaluationNarrative, EvaluationTemplate, EvaluationStatus
from app.models.athlete import Athlete
from app.models.coach import Coach
from app.schemas.evaluation import EvaluationCreate, EvaluationUpdate, EvalStatsResponse
from app.services.evaluation_ai import generate_narrative


async def list_evaluations(db: AsyncSession, org_id: str, status: str | None = None, athlete_id: str | None = None) -> list[dict]:
    q = select(Evaluation).where(Evaluation.organization_id == org_id)
    if status:
        q = q.where(Evaluation.status == status)
    if athlete_id:
        q = q.where(Evaluation.athlete_id == athlete_id)
    q = q.order_by(Evaluation.created_at.desc()).limit(100)
    result = await db.execute(q)
    evals = result.scalars().all()

    items = []
    for ev in evals:
        athlete = await db.get(Athlete, ev.athlete_id)
        coach = await db.get(Coach, ev.coach_id) if ev.coach_id else None
        items.append({
            "id": ev.id,
            "athlete_id": ev.athlete_id,
            "athlete_name": athlete.full_name if athlete else "Unknown",
            "coach_id": ev.coach_id,
            "coach_name": coach.full_name if coach else None,
            "evaluation_type": ev.evaluation_type.value if hasattr(ev.evaluation_type, "value") else ev.evaluation_type,
            "period_start": ev.period_start,
            "period_end": ev.period_end,
            "overall_score": ev.overall_score,
            "status": ev.status.value if hasattr(ev.status, "value") else ev.status,
            "ai_generated": ev.ai_generated,
            "created_at": ev.created_at,
            "category_count": len(ev.categories),
        })
    return items


async def get_evaluation(db: AsyncSession, eval_id: str, org_id: str) -> dict | None:
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == eval_id, Evaluation.organization_id == org_id)
    )
    ev = result.scalar_one_or_none()
    if not ev:
        return None

    athlete = await db.get(Athlete, ev.athlete_id)
    coach = await db.get(Coach, ev.coach_id) if ev.coach_id else None

    return {
        "id": ev.id,
        "organization_id": ev.organization_id,
        "athlete_id": ev.athlete_id,
        "athlete_name": athlete.full_name if athlete else "Unknown",
        "coach_id": ev.coach_id,
        "coach_name": coach.full_name if coach else None,
        "event_id": ev.event_id,
        "template_id": ev.template_id,
        "evaluation_type": ev.evaluation_type.value if hasattr(ev.evaluation_type, "value") else ev.evaluation_type,
        "period_start": ev.period_start,
        "period_end": ev.period_end,
        "overall_score": ev.overall_score,
        "status": ev.status.value if hasattr(ev.status, "value") else ev.status,
        "ai_generated": ev.ai_generated,
        "coach_notes": ev.coach_notes,
        "created_at": ev.created_at,
        "updated_at": ev.updated_at,
        "categories": [
            {
                "id": c.id,
                "category_name": c.category_name,
                "score": c.score,
                "previous_score": c.previous_score,
                "trend": c.trend,
                "notes": c.notes,
                "display_order": c.display_order,
                "weight": c.weight,
            }
            for c in sorted(ev.categories, key=lambda x: x.display_order)
        ],
        "narrative": {
            "id": ev.narrative.id,
            "summary": ev.narrative.summary,
            "strengths": ev.narrative.strengths,
            "areas_for_improvement": ev.narrative.areas_for_improvement,
            "recommendations": ev.narrative.recommendations,
            "parent_friendly_summary": ev.narrative.parent_friendly_summary,
        } if ev.narrative else None,
    }


async def create_evaluation(db: AsyncSession, org_id: str, data: EvaluationCreate) -> dict:
    # get previous scores for this athlete if they exist
    prev_result = await db.execute(
        select(Evaluation)
        .where(Evaluation.athlete_id == data.athlete_id, Evaluation.organization_id == org_id, Evaluation.status == EvaluationStatus.PUBLISHED)
        .order_by(Evaluation.created_at.desc())
        .limit(1)
    )
    prev_eval = prev_result.scalar_one_or_none()
    prev_scores = {}
    if prev_eval:
        for cat in prev_eval.categories:
            prev_scores[cat.category_name] = cat.score

    ev = Evaluation(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        athlete_id=data.athlete_id,
        coach_id=data.coach_id,
        event_id=data.event_id,
        template_id=data.template_id,
        evaluation_type=data.evaluation_type,
        period_start=data.period_start,
        period_end=data.period_end,
        coach_notes=data.coach_notes,
        status=EvaluationStatus.DRAFT,
    )
    db.add(ev)
    await db.flush()

    total_weight = 0.0
    weighted_sum = 0.0
    for i, cs in enumerate(data.category_scores):
        prev = prev_scores.get(cs.category_name)
        if prev is not None:
            trend = "improving" if cs.score > prev + 0.3 else ("declining" if cs.score < prev - 0.3 else "stable")
        else:
            trend = "stable"

        cat = EvaluationCategory(
            id=str(uuid.uuid4()),
            evaluation_id=ev.id,
            category_name=cs.category_name,
            score=cs.score,
            previous_score=prev,
            trend=trend,
            notes=cs.notes,
            display_order=i,
            weight=1.0,
        )
        db.add(cat)
        total_weight += 1.0
        weighted_sum += cs.score

    ev.overall_score = round(weighted_sum / max(total_weight, 1), 2)
    await db.flush()
    return await get_evaluation(db, ev.id, org_id)


async def update_evaluation(db: AsyncSession, eval_id: str, org_id: str, data: EvaluationUpdate) -> dict | None:
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == eval_id, Evaluation.organization_id == org_id)
    )
    ev = result.scalar_one_or_none()
    if not ev:
        return None

    if data.coach_notes is not None:
        ev.coach_notes = data.coach_notes

    if data.category_scores is not None:
        # delete existing categories and recreate
        for cat in ev.categories:
            await db.delete(cat)
        await db.flush()

        # get previous scores
        prev_result = await db.execute(
            select(Evaluation)
            .where(Evaluation.athlete_id == ev.athlete_id, Evaluation.organization_id == org_id,
                   Evaluation.status == EvaluationStatus.PUBLISHED, Evaluation.id != eval_id)
            .order_by(Evaluation.created_at.desc()).limit(1)
        )
        prev_eval = prev_result.scalar_one_or_none()
        prev_scores = {c.category_name: c.score for c in prev_eval.categories} if prev_eval else {}

        total_weight = 0.0
        weighted_sum = 0.0
        for i, cs in enumerate(data.category_scores):
            prev = prev_scores.get(cs.category_name)
            trend = "stable"
            if prev is not None:
                trend = "improving" if cs.score > prev + 0.3 else ("declining" if cs.score < prev - 0.3 else "stable")

            cat = EvaluationCategory(
                id=str(uuid.uuid4()),
                evaluation_id=ev.id,
                category_name=cs.category_name,
                score=cs.score,
                previous_score=prev,
                trend=trend,
                notes=cs.notes,
                display_order=i,
                weight=1.0,
            )
            db.add(cat)
            total_weight += 1.0
            weighted_sum += cs.score

        ev.overall_score = round(weighted_sum / max(total_weight, 1), 2)

    if data.overall_score is not None:
        ev.overall_score = data.overall_score

    await db.flush()
    return await get_evaluation(db, eval_id, org_id)


async def generate_ai_narrative(db: AsyncSession, eval_id: str, org_id: str) -> dict | None:
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == eval_id, Evaluation.organization_id == org_id)
    )
    ev = result.scalar_one_or_none()
    if not ev:
        return None

    athlete = await db.get(Athlete, ev.athlete_id)
    coach = await db.get(Coach, ev.coach_id) if ev.coach_id else None

    # get org sport type
    from app.models.organization import Organization
    org = await db.get(Organization, org_id)
    sport_type = org.sport_type if org else "multi"

    cats_data = [
        {
            "category_name": c.category_name,
            "score": c.score,
            "previous_score": c.previous_score,
            "trend": c.trend,
            "notes": c.notes,
        }
        for c in ev.categories
    ]

    narrative_data = generate_narrative(
        athlete_name=athlete.full_name if athlete else "the athlete",
        coach_name=coach.full_name if coach else "Coach",
        sport_type=sport_type,
        categories=cats_data,
        overall_score=ev.overall_score,
        evaluation_type=ev.evaluation_type.value if hasattr(ev.evaluation_type, "value") else ev.evaluation_type,
    )

    # upsert narrative
    if ev.narrative:
        ev.narrative.summary = narrative_data["summary"]
        ev.narrative.strengths = narrative_data["strengths"]
        ev.narrative.areas_for_improvement = narrative_data["areas_for_improvement"]
        ev.narrative.recommendations = narrative_data["recommendations"]
        ev.narrative.parent_friendly_summary = narrative_data["parent_friendly_summary"]
    else:
        narr = EvaluationNarrative(
            id=str(uuid.uuid4()),
            evaluation_id=ev.id,
            **narrative_data,
        )
        db.add(narr)

    ev.ai_generated = True
    await db.flush()
    return await get_evaluation(db, eval_id, org_id)


async def publish_evaluation(db: AsyncSession, eval_id: str, org_id: str) -> dict | None:
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == eval_id, Evaluation.organization_id == org_id)
    )
    ev = result.scalar_one_or_none()
    if not ev:
        return None
    ev.status = EvaluationStatus.PUBLISHED
    await db.flush()
    return await get_evaluation(db, eval_id, org_id)


async def get_athlete_evaluations(db: AsyncSession, athlete_id: str, org_id: str) -> list[dict]:
    return await list_evaluations(db, org_id, athlete_id=athlete_id)


async def get_evaluation_templates(db: AsyncSession, org_id: str) -> list:
    result = await db.execute(
        select(EvaluationTemplate).where(
            (EvaluationTemplate.organization_id == org_id) | (EvaluationTemplate.organization_id == None)  # noqa: E711
        ).order_by(EvaluationTemplate.is_default.desc())
    )
    return result.scalars().all()


async def get_eval_stats(db: AsyncSession, org_id: str) -> dict:
    from datetime import datetime
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total = (await db.execute(select(func.count(Evaluation.id)).where(Evaluation.organization_id == org_id))).scalar() or 0
    drafts = (await db.execute(select(func.count(Evaluation.id)).where(Evaluation.organization_id == org_id, Evaluation.status == "draft"))).scalar() or 0
    published = (await db.execute(select(func.count(Evaluation.id)).where(Evaluation.organization_id == org_id, Evaluation.status == "published"))).scalar() or 0
    ai_gen = (await db.execute(select(func.count(Evaluation.id)).where(Evaluation.organization_id == org_id, Evaluation.ai_generated == True))).scalar() or 0  # noqa: E712
    this_month = (await db.execute(select(func.count(Evaluation.id)).where(Evaluation.organization_id == org_id, Evaluation.created_at >= month_start))).scalar() or 0
    athletes_eval = (await db.execute(select(func.count(func.distinct(Evaluation.athlete_id))).where(Evaluation.organization_id == org_id))).scalar() or 0

    return {"total": total, "drafts": drafts, "published": published, "ai_generated": ai_gen, "this_month": this_month, "athletes_evaluated": athletes_eval}

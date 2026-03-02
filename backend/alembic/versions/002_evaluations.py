"""add evaluation models

revision id: 002
revises: 001
create date: 2024-01-16
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # evaluation templates (global defaults have null org_id)
    op.create_table(
        "evaluation_templates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True),
        sa.Column("sport_type", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("categories", sa.JSON, nullable=False),
        sa.Column("is_default", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "evaluations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("athlete_id", sa.String(36), sa.ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("coach_id", sa.String(36), sa.ForeignKey("coaches.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_id", sa.String(36), sa.ForeignKey("events.id", ondelete="SET NULL"), nullable=True),
        sa.Column("template_id", sa.String(36), sa.ForeignKey("evaluation_templates.id", ondelete="SET NULL"), nullable=True),
        sa.Column("evaluation_type", sa.String(20), server_default="session", nullable=False),
        sa.Column("period_start", sa.Date, nullable=False),
        sa.Column("period_end", sa.Date, nullable=False),
        sa.Column("overall_score", sa.Float, server_default="0.0"),
        sa.Column("status", sa.String(20), server_default="draft", nullable=False),
        sa.Column("ai_generated", sa.Boolean, server_default="false"),
        sa.Column("coach_notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_evaluations_org_id", "evaluations", ["organization_id"])
    op.create_index("ix_evaluations_athlete_id", "evaluations", ["athlete_id"])

    op.create_table(
        "evaluation_categories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("evaluation_id", sa.String(36), sa.ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_name", sa.String(255), nullable=False),
        sa.Column("score", sa.Float, server_default="5.0"),
        sa.Column("previous_score", sa.Float, nullable=True),
        sa.Column("trend", sa.String(20), server_default="stable"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("display_order", sa.Integer, server_default="0"),
        sa.Column("weight", sa.Float, server_default="1.0"),
    )

    op.create_table(
        "evaluation_narratives",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("evaluation_id", sa.String(36), sa.ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("strengths", sa.JSON, nullable=False),
        sa.Column("areas_for_improvement", sa.JSON, nullable=False),
        sa.Column("recommendations", sa.JSON, nullable=False),
        sa.Column("parent_friendly_summary", sa.Text, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("evaluation_narratives")
    op.drop_table("evaluation_categories")
    op.drop_index("ix_evaluations_athlete_id", "evaluations")
    op.drop_index("ix_evaluations_org_id", "evaluations")
    op.drop_table("evaluations")
    op.drop_table("evaluation_templates")

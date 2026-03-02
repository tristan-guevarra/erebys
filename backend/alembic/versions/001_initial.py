"""initial schema

revision id: 001
revises:
create date: 2024-01-15
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # organizations
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("sport_type", sa.String(100), server_default="multi"),
        sa.Column("region", sa.String(100), server_default="US-East"),
        sa.Column("competition_proxy", sa.Float, server_default="5.0"),
        sa.Column("logo_url", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("is_superadmin", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # org user roles
    op.create_table(
        "org_user_roles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("role", sa.Enum("superadmin", "admin", "manager", name="roleenum"), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # coaches
    op.create_table(
        "coaches",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("specialty", sa.String(100), server_default="general"),
        sa.Column("hourly_rate", sa.Float, server_default="0"),
        sa.Column("avg_rating", sa.Float, server_default="0"),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # athletes
    op.create_table(
        "athletes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("date_of_birth", sa.Date, nullable=True),
        sa.Column("skill_level", sa.String(50), server_default="intermediate"),
        sa.Column("ltv", sa.Float, server_default="0"),
        sa.Column("no_show_rate", sa.Float, server_default="0"),
        sa.Column("total_bookings", sa.Integer, server_default="0"),
        sa.Column("first_booking_date", sa.Date, nullable=True),
        sa.Column("last_booking_date", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # events
    op.create_table(
        "events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("coach_id", sa.String(36), sa.ForeignKey("coaches.id"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("event_type", sa.Enum("camp", "clinic", "private", name="eventtype"), nullable=False),
        sa.Column("status", sa.Enum("draft", "published", "full", "completed", "cancelled", name="eventstatus"), server_default="published"),
        sa.Column("capacity", sa.Integer, server_default="20"),
        sa.Column("booked_count", sa.Integer, server_default="0"),
        sa.Column("base_price", sa.Float, nullable=False),
        sa.Column("current_price", sa.Float, nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("start_time", sa.String(10), server_default="09:00"),
        sa.Column("end_time", sa.String(10), server_default="12:00"),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("skill_level", sa.String(50), server_default="all"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # bookings
    op.create_table(
        "bookings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_id", sa.String(36), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("athlete_id", sa.String(36), sa.ForeignKey("athletes.id"), nullable=False),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("status", sa.Enum("confirmed", "cancelled", "waitlisted", "pending", name="bookingstatus"), server_default="confirmed"),
        sa.Column("source", sa.Enum("platform", "direct", "referral", "import", name="bookingsource"), server_default="platform"),
        sa.Column("price_paid", sa.Float, nullable=False),
        sa.Column("discount_applied", sa.Float, server_default="0"),
        sa.Column("experiment_variant", sa.String(50), nullable=True),
        sa.Column("booked_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("cancelled_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # attendance
    op.create_table(
        "attendance",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("booking_id", sa.String(36), sa.ForeignKey("bookings.id"), nullable=False, unique=True),
        sa.Column("attended", sa.Boolean, server_default="false"),
        sa.Column("no_show", sa.Boolean, server_default="false"),
        sa.Column("late_cancel", sa.Boolean, server_default="false"),
        sa.Column("check_in_time", sa.DateTime, nullable=True),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # payments
    op.create_table(
        "payments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("booking_id", sa.String(36), sa.ForeignKey("bookings.id"), nullable=False, unique=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("currency", sa.String(3), server_default="USD"),
        sa.Column("status", sa.Enum("completed", "pending", "refunded", "failed", name="paymentstatus"), server_default="completed"),
        sa.Column("stripe_payment_id", sa.String(255), nullable=True),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column("paid_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("refunded_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # ratings
    op.create_table(
        "ratings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_id", sa.String(36), sa.ForeignKey("events.id"), nullable=True),
        sa.Column("coach_id", sa.String(36), sa.ForeignKey("coaches.id"), nullable=True),
        sa.Column("athlete_id", sa.String(36), sa.ForeignKey("athletes.id"), nullable=False),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # metrics daily
    op.create_table(
        "metrics_daily",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("metric_date", sa.Date, nullable=False),
        sa.Column("total_revenue", sa.Float, server_default="0"),
        sa.Column("booking_count", sa.Integer, server_default="0"),
        sa.Column("cancellation_count", sa.Integer, server_default="0"),
        sa.Column("total_capacity", sa.Integer, server_default="0"),
        sa.Column("total_booked", sa.Integer, server_default="0"),
        sa.Column("utilization_rate", sa.Float, server_default="0"),
        sa.Column("no_show_count", sa.Integer, server_default="0"),
        sa.Column("no_show_rate", sa.Float, server_default="0"),
        sa.Column("late_cancel_count", sa.Integer, server_default="0"),
        sa.Column("active_athletes", sa.Integer, server_default="0"),
        sa.Column("new_athletes", sa.Integer, server_default="0"),
        sa.Column("avg_ltv", sa.Float, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_metrics_daily_org_date", "metrics_daily", ["organization_id", "metric_date"])

    # pricing recommendations
    op.create_table(
        "pricing_recommendations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_id", sa.String(36), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("current_price", sa.Float, nullable=False),
        sa.Column("suggested_price", sa.Float, nullable=False),
        sa.Column("confidence_score", sa.Integer, server_default="50"),
        sa.Column("price_change_pct", sa.Float, server_default="0"),
        sa.Column("expected_demand_change", sa.Float, server_default="0"),
        sa.Column("expected_revenue_change", sa.Float, server_default="0"),
        sa.Column("explanation", sa.Text, nullable=True),
        sa.Column("drivers", sa.JSON, nullable=True),
        sa.Column("model_version", sa.String(50), server_default="v1.0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # price change requests
    op.create_table(
        "price_change_requests",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_id", sa.String(36), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("recommendation_id", sa.String(36), sa.ForeignKey("pricing_recommendations.id"), nullable=True),
        sa.Column("requested_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reviewed_by", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("old_price", sa.Float, nullable=False),
        sa.Column("new_price", sa.Float, nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("status", sa.Enum("pending", "approved", "rejected", "applied", name="changerequststatus"), server_default="pending"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("reviewed_at", sa.DateTime, nullable=True),
    )

    # experiments
    op.create_table(
        "experiments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("event_id", sa.String(36), sa.ForeignKey("events.id"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.Enum("draft", "running", "paused", "completed", name="experimentstatus"), server_default="draft"),
        sa.Column("variant_a_price", sa.Float, nullable=False),
        sa.Column("variant_b_price", sa.Float, nullable=False),
        sa.Column("traffic_split", sa.Float, server_default="0.5"),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("results", sa.JSON, nullable=True),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # experiment assignments
    op.create_table(
        "experiment_assignments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("experiment_id", sa.String(36), sa.ForeignKey("experiments.id"), nullable=False),
        sa.Column("athlete_id", sa.String(36), sa.ForeignKey("athletes.id"), nullable=False),
        sa.Column("variant", sa.String(1), nullable=False),
        sa.Column("booking_id", sa.String(36), sa.ForeignKey("bookings.id"), nullable=True),
        sa.Column("converted", sa.Boolean, server_default="false"),
        sa.Column("revenue", sa.Float, server_default="0"),
        sa.Column("assigned_at", sa.DateTime, server_default=sa.func.now()),
    )

    # audit logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(36), nullable=True),
        sa.Column("details", sa.JSON, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_org", "audit_logs", ["organization_id", "created_at"])

    # feature flags
    op.create_table(
        "feature_flags",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("feature_key", sa.String(100), nullable=False),
        sa.Column("enabled", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # insight reports
    op.create_table(
        "insight_reports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("report_type", sa.String(50), server_default="weekly"),
        sa.Column("period_start", sa.Date, nullable=False),
        sa.Column("period_end", sa.Date, nullable=False),
        sa.Column("narrative", sa.Text, nullable=False),
        sa.Column("highlights", sa.JSON, nullable=True),
        sa.Column("alerts", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("insight_reports")
    op.drop_table("feature_flags")
    op.drop_table("audit_logs")
    op.drop_table("experiment_assignments")
    op.drop_table("experiments")
    op.drop_table("price_change_requests")
    op.drop_table("pricing_recommendations")
    op.drop_table("metrics_daily")
    op.drop_table("ratings")
    op.drop_table("payments")
    op.drop_table("attendance")
    op.drop_table("bookings")
    op.drop_table("events")
    op.drop_table("athletes")
    op.drop_table("coaches")
    op.drop_table("org_user_roles")
    op.drop_table("users")
    op.drop_table("organizations")

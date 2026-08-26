"""initial persistence schema

Revision ID: 0001_initial
Revises:
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("skills", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("target_roles", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("preferred_locations", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("remote_preference", sa.Boolean(), nullable=True),
        sa.Column("experience_level", sa.String(100), nullable=True),
        sa.Column("industries", postgresql.ARRAY(sa.String()), nullable=False),
    )
    op.create_table(
        "opportunities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("organization", sa.String(300), nullable=False),
        sa.Column("opportunity_type", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source", sa.String(200), nullable=False),
        sa.Column("source_id", sa.String(300), nullable=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("location", sa.String(300), nullable=True),
        sa.Column("remote", sa.Boolean(), nullable=True),
        sa.Column("required_skills", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.UniqueConstraint("source", "fingerprint", name="uq_opportunity_source_fingerprint"),
    )
    op.create_index("ix_opportunities_fingerprint", "opportunities", ["fingerprint"])
    op.create_table(
        "match_results",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("fit", sa.String(50), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("policy_version", sa.String(50), nullable=False),
    )
    op.create_index("ix_match_results_user_id", "match_results", ["user_id"])
    op.create_index("ix_match_results_opportunity_id", "match_results", ["opportunity_id"])


def downgrade() -> None:
    op.drop_index("ix_match_results_opportunity_id", table_name="match_results")
    op.drop_index("ix_match_results_user_id", table_name="match_results")
    op.drop_table("match_results")
    op.drop_index("ix_opportunities_fingerprint", table_name="opportunities")
    op.drop_table("opportunities")
    op.drop_table("user_profiles")

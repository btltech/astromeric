"""Add free_ai_claims for the website's one free AI answer a day

Revision ID: add_free_ai_claims
Revises: add_time_confidence_data_quality
Create Date: 2026-09-30
"""
from alembic import op

revision = "add_free_ai_claims"
down_revision = "add_time_confidence_data_quality"
branch_labels = None
depends_on = None


def upgrade():
    # IF NOT EXISTS keeps this idempotent, like the migrations before it.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS free_ai_claims (
            id SERIAL PRIMARY KEY,
            day VARCHAR(10) NOT NULL,
            key VARCHAR(80) NOT NULL,
            claim_id VARCHAR(32) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_free_ai_claims_day_key "
        "ON free_ai_claims (day, key)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_free_ai_claims_claim "
        "ON free_ai_claims (claim_id)"
    )


def downgrade():
    op.execute("DROP TABLE IF EXISTS free_ai_claims")

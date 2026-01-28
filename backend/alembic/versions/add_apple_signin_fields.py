"""Add Apple Sign-In fields to User

Revision ID: add_apple_signin_fields
Revises: add_notification_prefs
Create Date: 2026-01-26 22:40:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_apple_signin_fields'
down_revision = 'add_notification_prefs'
branch_labels = None
depends_on = None


def upgrade():
    # Add Apple Sign-In columns to users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('external_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('auth_provider', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('full_name', sa.String(255), nullable=True))
        batch_op.create_index('ix_users_external_id', ['external_id'], unique=True)
    
    # Make hashed_password nullable for Apple users
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('hashed_password',
                              existing_type=sa.String(),
                              nullable=True)


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('hashed_password',
                              existing_type=sa.String(),
                              nullable=False)
        batch_op.drop_index('ix_users_external_id')
        batch_op.drop_column('full_name')
        batch_op.drop_column('auth_provider')
        batch_op.drop_column('external_id')

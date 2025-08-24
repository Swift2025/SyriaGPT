"""users_reset_token_expire_last_password_change

Revision ID: ad91366937b5
Revises: 
Create Date: 2025-08-24 12:30:49.130202

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import UUID
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', UUID(as_uuid=True), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('full_name', sa.String(length=200), nullable=True),
    sa.Column('profile_picture', sa.String(length=500), nullable=True),
    sa.Column('oauth_provider', sa.String(length=50), nullable=True),
    sa.Column('oauth_provider_id', sa.String(length=100), nullable=True),
    sa.Column('oauth_data', sa.Text(), nullable=True),
    sa.Column('is_email_verified', sa.Boolean(), nullable=True),
    sa.Column('is_phone_verified', sa.Boolean(), nullable=True),
    sa.Column('two_factor_enabled', sa.Boolean(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('token', sa.String(), nullable=True),
    sa.Column('token_expiry', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('reset_token', sa.String(), nullable=True),
    sa.Column('reset_token_expiry', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_password_change', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_unique_constraint(None, 'users', ['email'])
    op.create_unique_constraint(None, 'users', ['phone_number'])


def downgrade() -> None:
    op.drop_table('users')

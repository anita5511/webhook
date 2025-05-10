"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2025-05-09
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('target_url', sa.String, nullable=False),
        sa.Column('secret', sa.String),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_table(
        'deliveries',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('subscription_id', sa.Integer, sa.ForeignKey('subscriptions.id'), nullable=False),
        sa.Column('payload', sa.Text, nullable=False),
        sa.Column('status', sa.String, server_default='pending'),
        sa.Column('attempts', sa.Integer, server_default='0'),
        sa.Column('last_error', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )

def downgrade():
    op.drop_table('deliveries')
    op.drop_table('subscriptions')
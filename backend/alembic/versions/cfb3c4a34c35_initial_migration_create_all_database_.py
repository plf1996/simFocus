"""Initial migration: Create all database tables

Revision ID: cfb3c4a34c35
Revises:
Create Date: 2026-01-13 09:51:56.597292

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'cfb3c4a34c35'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('auth_provider', sa.String(length=50), nullable=False, server_default='email'),
        sa.Column('provider_id', sa.String(length=255), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('provider_id')
    )
    op.create_index('idx_users_email_verified', 'users', ['email_verified'])
    op.create_index('idx_users_auth_provider', 'users', ['auth_provider'])
    op.create_index('idx_users_deleted_at', 'users', ['deleted_at'])
    op.create_index('ix_users_id', 'users', ['id'])

    # Create user_api_keys table
    op.create_table(
        'user_api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('key_name', sa.String(length=100), nullable=False),
        sa.Column('encrypted_key', sa.Text(), nullable=False),
        sa.Column('api_base_url', sa.Text(), nullable=True),
        sa.Column('default_model', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_api_keys_user_provider', 'user_api_keys', ['user_id', 'provider'])
    op.create_index('idx_api_keys_is_active', 'user_api_keys', ['is_active'])
    op.create_index('ix_user_api_keys_id', 'user_api_keys', ['id'])

    # Create topics table
    op.create_table(
        'topics',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('context', sa.Text(), nullable=True),
        sa.Column('attachments', postgresql.JSONB(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['template_id'], ['topics.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_topics_user_status', 'topics', ['user_id', 'status'])
    op.create_index('idx_topics_status', 'topics', ['status'])
    op.create_index('ix_topics_id', 'topics', ['id'])

    # Create characters table
    op.create_table(
        'characters',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('is_template', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('config', postgresql.JSONB(), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rating_avg', postgresql.NUMERIC(precision=3, scale=2), nullable=True),
        sa.Column('rating_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_characters_user_template', 'characters', ['user_id', 'is_template'])
    op.create_index('idx_characters_is_template', 'characters', ['is_template'])
    op.create_index('ix_characters_id', 'characters', ['id'])

    # Create discussions table
    op.create_table(
        'discussions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('topic_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('discussion_mode', sa.String(length=20), nullable=False, server_default='free'),
        sa.Column('max_rounds', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='initialized'),
        sa.Column('current_round', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_phase', sa.String(length=20), nullable=False, server_default='opening'),
        sa.Column('llm_provider', sa.String(length=50), nullable=False),
        sa.Column('llm_model', sa.String(length=100), nullable=False),
        sa.Column('total_tokens_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('estimated_cost_usd', postgresql.NUMERIC(precision=10, scale=4), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_discussions_user_status', 'discussions', ['user_id', 'status'])
    op.create_index('idx_discussions_status', 'discussions', ['status'])
    op.create_index('ix_discussions_id', 'discussions', ['id'])

    # Create discussion_participants table
    op.create_table(
        'discussion_participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('discussion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('position', sa.Integer(), nullable=True),
        sa.Column('stance', sa.String(length=20), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['discussion_id'], ['discussions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_discussion_participants_id', 'discussion_participants', ['id'])

    # Create discussion_messages table
    op.create_table(
        'discussion_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('discussion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('participant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('round', sa.Integer(), nullable=False),
        sa.Column('phase', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=False),
        sa.Column('is_injected_question', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('parent_message_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('tsv', postgresql.TSVECTOR(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['discussion_id'], ['discussions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_message_id'], ['discussion_messages.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['participant_id'], ['discussion_participants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_messages_discussion_round', 'discussion_messages', ['discussion_id', 'round'])
    op.create_index('idx_messages_tsv', 'discussion_messages', ['tsv'], postgresql_using='gin')
    op.create_index('ix_discussion_messages_id', 'discussion_messages', ['id'])

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('discussion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('overview', postgresql.JSONB(), nullable=False),
        sa.Column('viewpoints_summary', postgresql.JSONB(), nullable=False),
        sa.Column('consensus', postgresql.JSONB(), nullable=False),
        sa.Column('controversies', postgresql.JSONB(), nullable=False),
        sa.Column('insights', postgresql.JSONB(), nullable=False),
        sa.Column('recommendations', postgresql.JSONB(), nullable=False),
        sa.Column('full_transcript_citation', sa.Text(), nullable=True),
        sa.Column('quality_scores', postgresql.JSONB(), nullable=False),
        sa.Column('generation_time_ms', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['discussion_id'], ['discussions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('discussion_id')
    )
    op.create_index('ix_reports_id', 'reports', ['id'])

    # Create share_links table
    op.create_table(
        'share_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('discussion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('slug', sa.String(length=20), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('access_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['discussion_id'], ['discussions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('idx_share_links_slug', 'share_links', ['slug'])
    op.create_index('idx_share_links_discussion', 'share_links', ['discussion_id'])
    op.create_index('ix_share_links_id', 'share_links', ['id'])


def downgrade() -> None:
    """Downgrade schema."""

    # Drop tables in reverse order of creation (due to foreign key constraints)
    op.drop_index('ix_share_links_id', table_name='share_links')
    op.drop_index('idx_share_links_discussion', table_name='share_links')
    op.drop_index('idx_share_links_slug', table_name='share_links')
    op.drop_table('share_links')

    op.drop_index('ix_reports_id', table_name='reports')
    op.drop_table('reports')

    op.drop_index('ix_discussion_messages_id', table_name='discussion_messages')
    op.drop_index('idx_messages_tsv', table_name='discussion_messages')
    op.drop_index('idx_messages_discussion_round', table_name='discussion_messages')
    op.drop_table('discussion_messages')

    op.drop_index('ix_discussion_participants_id', table_name='discussion_participants')
    op.drop_table('discussion_participants')

    op.drop_index('ix_discussions_id', table_name='discussions')
    op.drop_index('idx_discussions_status', table_name='discussions')
    op.drop_index('idx_discussions_user_status', table_name='discussions')
    op.drop_table('discussions')

    op.drop_index('ix_characters_id', table_name='characters')
    op.drop_index('idx_characters_is_template', table_name='characters')
    op.drop_index('idx_characters_user_template', table_name='characters')
    op.drop_table('characters')

    op.drop_index('ix_topics_id', table_name='topics')
    op.drop_index('idx_topics_status', table_name='topics')
    op.drop_index('idx_topics_user_status', table_name='topics')
    op.drop_table('topics')

    op.drop_index('ix_user_api_keys_id', table_name='user_api_keys')
    op.drop_index('idx_api_keys_is_active', table_name='user_api_keys')
    op.drop_index('idx_api_keys_user_provider', table_name='user_api_keys')
    op.drop_table('user_api_keys')

    op.drop_index('ix_users_id', table_name='users')
    op.drop_index('idx_users_deleted_at', table_name='users')
    op.drop_index('idx_users_auth_provider', table_name='users')
    op.drop_index('idx_users_email_verified', table_name='users')
    op.drop_table('users')

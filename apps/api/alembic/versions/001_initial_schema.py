"""initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Research runs
    op.create_table('research_runs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('question', sa.String(length=2000), nullable=False),
        sa.Column('status', sa.Enum('pending', 'planning', 'researching', 'extracting', 'verifying', 'synthesizing', 'completed', 'failed', name='research_status'), nullable=False),
        sa.Column('depth', sa.Enum('quick', 'standard', 'deep', name='research_depth'), nullable=False),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('stats', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_research_runs_question'), 'research_runs', ['question'], unique=False)
    
    # Research tasks
    op.create_table('research_tasks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('research_run_id', sa.UUID(), nullable=False),
        sa.Column('task_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['research_run_id'], ['research_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_research_tasks_research_run_id'), 'research_tasks', ['research_run_id'], unique=False)

    # Sources
    op.create_table('sources',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('research_run_id', sa.UUID(), nullable=False),
        sa.Column('url', sa.String(length=2048), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('author', sa.String(length=200), nullable=True),
        sa.Column('source_type', sa.String(length=50), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['research_run_id'], ['research_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sources_research_run_id'), 'sources', ['research_run_id'], unique=False)

    # Document chunks
    op.create_table('document_chunks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('source_id', sa.UUID(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(dim=768), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_chunks_source_id'), 'document_chunks', ['source_id'], unique=False)
    op.execute('CREATE INDEX ix_document_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)')

    # Claims
    op.create_table('claims',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('research_run_id', sa.UUID(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('verdict', sa.String(length=30), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('evidence_span', sa.Text(), nullable=True),
        sa.Column('source_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['research_run_id'], ['research_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_claims_research_run_id'), 'claims', ['research_run_id'], unique=False)

    # Citations
    op.create_table('citations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('research_run_id', sa.UUID(), nullable=False),
        sa.Column('claim_id', sa.UUID(), nullable=False),
        sa.Column('source_id', sa.UUID(), nullable=False),
        sa.Column('passage', sa.Text(), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['research_run_id'], ['research_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['claim_id'], ['claims.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_citations_research_run_id'), 'citations', ['research_run_id'], unique=False)
    op.create_index(op.f('ix_citations_claim_id'), 'citations', ['claim_id'], unique=False)
    op.create_index(op.f('ix_citations_source_id'), 'citations', ['source_id'], unique=False)

    # Agent events
    op.create_table('agent_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('research_run_id', sa.UUID(), nullable=False),
        sa.Column('agent_name', sa.String(length=100), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('latency_ms', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['research_run_id'], ['research_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_events_research_run_id'), 'agent_events', ['research_run_id'], unique=False)


def downgrade() -> None:
    op.drop_table('agent_events')
    op.drop_table('citations')
    op.drop_table('claims')
    op.drop_table('document_chunks')
    op.drop_table('sources')
    op.drop_table('research_tasks')
    op.drop_table('research_runs')
    op.execute('DROP TYPE IF EXISTS research_status')
    op.execute('DROP TYPE IF EXISTS research_depth')

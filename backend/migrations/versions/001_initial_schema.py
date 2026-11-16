"""Initial migration: all 13 core entities

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-16 02:30:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Enable extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"vector\";")

    # 2. Users Table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # 3. Faculty & Departments
    op.create_table(
        'departments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('code', sa.String(length=32), nullable=False, unique=True),
        sa.Column('head_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'faculty',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('faculty_id', sa.String(length=64), nullable=False, unique=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True),
        sa.Column('orcid', sa.String(length=32), nullable=True, unique=True),
        sa.Column('google_scholar_id', sa.String(length=64), nullable=True),
        sa.Column('scopus_author_id', sa.String(length=64), nullable=True),
        sa.Column('wos_researcher_id', sa.String(length=64), nullable=True),
        sa.Column('designation', sa.String(length=128), nullable=False, server_default='Assistant Professor'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_faculty_orcid', 'faculty', ['orcid'])
    op.create_index('ix_faculty_faculty_id', 'faculty', ['faculty_id'])

    # 4. Publications
    op.create_table(
        'publications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(length=1000), nullable=False),
        sa.Column('doi', sa.String(length=255), nullable=True, unique=True),
        sa.Column('abstract', sa.Text(), nullable=True),
        sa.Column('publication_year', sa.Integer(), nullable=True),
        sa.Column('publication_type', sa.String(length=32), nullable=False, server_default='journal'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='unverified'),
        sa.Column('total_citations', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('title_embedding', Vector(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_publications_doi', 'publications', ['doi'])
    op.create_index('ix_publications_year', 'publications', ['publication_year'])

    # 5. Publication Authors
    op.create_table(
        'publication_authors',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('publication_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('publications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('faculty_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('faculty.id', ondelete='SET NULL'), nullable=True),
        sa.Column('author_name', sa.String(length=255), nullable=False),
        sa.Column('author_order', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_corresponding', sa.Boolean(), nullable=False, server_default='false'),
    )

    # 6. Publication Sources
    op.create_table(
        'publication_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('publication_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('publications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_name', sa.String(length=32), nullable=False),
        sa.Column('source_id', sa.String(length=255), nullable=True),
        sa.Column('source_url', sa.String(length=1000), nullable=True),
        sa.Column('raw_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('retrieved_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
    )

    # 7. Publication Verification
    op.create_table(
        'publication_verification',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('publication_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('publications.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('scopus_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('wos_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('crossref_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('openalex_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('scopus_eid', sa.String(length=64), nullable=True),
        sa.Column('wos_uid', sa.String(length=64), nullable=True),
        sa.Column('crossref_doi_valid', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verification_evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by_agent', sa.String(length=64), nullable=True),
    )

    # 8. Duplicate Candidates
    op.create_table(
        'duplicate_candidates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('publication_a_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('publications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('publication_b_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('publications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('similarity_score', sa.Float(), nullable=False),
        sa.Column('match_type', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='pending'),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 9. Citation Snapshots
    op.create_table(
        'citation_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('publication_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('publications.id', ondelete='CASCADE'), nullable=True),
        sa.Column('faculty_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('faculty.id', ondelete='CASCADE'), nullable=True),
        sa.Column('citation_count', sa.Integer(), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('source', sa.String(length=32), nullable=False),
        sa.Column('h_index', sa.Integer(), nullable=True),
        sa.Column('i10_index', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 10. Agent Executions
    op.create_table(
        'agent_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('agent_name', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='pending'),
        sa.Column('triggered_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('input_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('output_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
    )

    # 11. Agent Logs
    op.create_table(
        'agent_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('execution_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agent_executions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('level', sa.String(length=16), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('logged_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 12. Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('resource_type', sa.String(length=64), nullable=False),
        sa.Column('resource_id', sa.String(length=64), nullable=True),
        sa.Column('old_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 13. Reports
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('report_type', sa.String(length=32), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('generated_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='generating'),
        sa.Column('generated_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('academic_year', sa.String(length=16), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_table('reports')
    op.drop_table('audit_logs')
    op.drop_table('agent_logs')
    op.drop_table('agent_executions')
    op.drop_table('citation_snapshots')
    op.drop_table('duplicate_candidates')
    op.drop_table('publication_verification')
    op.drop_table('publication_sources')
    op.drop_table('publication_authors')
    op.drop_table('publications')
    op.drop_table('faculty')
    op.drop_table('departments')
    op.drop_table('users')

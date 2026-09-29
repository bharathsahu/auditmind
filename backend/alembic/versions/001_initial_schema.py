"""Initial Enterprise AuditMind Database Schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-29 21:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Organizations
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('code', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=True)

    # Departments
    op.create_table(
        'departments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_departments_id'), 'departments', ['id'], unique=False)

    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Audits
    op.create_table(
        'audits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('audit_code', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('department', sa.String(), nullable=True),
        sa.Column('audit_type', sa.String(), nullable=True),
        sa.Column('risk_level', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('start_date', sa.String(), nullable=True),
        sa.Column('end_date', sa.String(), nullable=True),
        sa.Column('auditor', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('fiscal_year', sa.Integer(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audits_audit_code'), 'audits', ['audit_code'], unique=True)

    # Findings
    op.create_table(
        'findings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('finding_code', sa.String(), nullable=True),
        sa.Column('audit_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(), nullable=True),
        sa.Column('control_involved', sa.String(), nullable=True),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('business_impact', sa.Text(), nullable=True),
        sa.Column('recommendation', sa.Text(), nullable=True),
        sa.Column('management_response', sa.Text(), nullable=True),
        sa.Column('remediation_owner', sa.String(), nullable=True),
        sa.Column('due_date', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('created_date', sa.String(), nullable=True),
        sa.Column('resolved_date', sa.String(), nullable=True),
        sa.Column('fiscal_year', sa.Integer(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['audit_id'], ['audits.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_findings_finding_code'), 'findings', ['finding_code'], unique=True)

    # Remediations
    op.create_table(
        'remediations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('finding_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.Text(), nullable=True),
        sa.Column('owner', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('due_date', sa.String(), nullable=True),
        sa.Column('completion_date', sa.String(), nullable=True),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['finding_id'], ['findings.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Documents
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('file_type', sa.String(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('audit_id', sa.Integer(), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=True),
        sa.Column('facts_extracted', sa.Integer(), nullable=True),
        sa.Column('document_hash', sa.String(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['audit_id'], ['audits.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Memory Nodes
    op.create_table(
        'memory_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bank_id', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('reference_type', sa.String(), nullable=True),
        sa.Column('reference_code', sa.String(), nullable=True),
        sa.Column('tags', sa.String(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('action_type', sa.String(), nullable=True),
        sa.Column('entity_name', sa.String(), nullable=True),
        sa.Column('entity_id', sa.String(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('memory_nodes')
    op.drop_table('documents')
    op.drop_table('remediations')
    op.drop_table('findings')
    op.drop_table('audits')
    op.drop_table('users')
    op.drop_table('departments')
    op.drop_table('organizations')

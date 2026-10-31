"""Add study tracking and stored AI study guides."""
from alembic import op
from app.main import StudyGuidance, StudySession
revision='0002_study_tracking_ai_guidance'; down_revision='0001_initial'; branch_labels=None; depends_on=None
def upgrade():
    bind=op.get_bind()
    StudySession.__table__.create(bind=bind,checkfirst=True)
    StudyGuidance.__table__.create(bind=bind,checkfirst=True)
def downgrade():
    bind=op.get_bind()
    StudyGuidance.__table__.drop(bind=bind,checkfirst=True)
    StudySession.__table__.drop(bind=bind,checkfirst=True)

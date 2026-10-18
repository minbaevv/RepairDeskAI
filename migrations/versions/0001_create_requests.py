from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "repair_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_name", sa.String(100), nullable=False),
        sa.Column("device", sa.String(150), nullable=False),
        sa.Column("problem", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("repair_requests")

"""create_todos

Revision ID: 131f324266cc
Revises:
Create Date: 2025-02-01 07:04:35.275237

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "131f324266cc"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "todos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column(
            "severity",
            sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="severityenum"),
            server_default="LOW",
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("TODO", "IN_PROGRESS", "DONE", "CANCELLED", name="statusenum"),
            server_default="TODO",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_todos_id"), "todos", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_todos_id"), table_name="todos")
    op.drop_table("todos")
    # ### end Alembic commands ###

"""create new column

Revision ID: 19016294103d
Revises: 
Create Date: 2026-07-20 17:10:10.206918

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19016294103d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.add_column("posts", sa.Column("phone_number", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("posts", "phone")
    

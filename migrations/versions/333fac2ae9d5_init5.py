"""'init5'

Revision ID: 333fac2ae9d5
Revises: 36982af37e29
Create Date: 2017-12-23 23:10:52.416000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '333fac2ae9d5'
down_revision = '36982af37e29'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('catalog', sa.Column('catalog_eng', sa.String(length=30), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('catalog', 'catalog_eng')
    # ### end Alembic commands ###

"""'init0'

Revision ID: dd4d873464de
Revises: 333fac2ae9d5
Create Date: 2018-01-04 22:16:10.728000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd4d873464de'
down_revision = '333fac2ae9d5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('article', sa.Column('img_url', sa.String(length=100), nullable=True))
    op.add_column('comment', sa.Column('email', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('comment', 'email')
    op.drop_column('article', 'img_url')
    # ### end Alembic commands ###

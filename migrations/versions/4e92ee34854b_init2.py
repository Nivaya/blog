"""'init2'

Revision ID: 4e92ee34854b
Revises: 9fab7d1c06fc
Create Date: 2017-12-20 22:31:44.910000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e92ee34854b'
down_revision = '9fab7d1c06fc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag', sa.String(length=30), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column(u'article', sa.Column('tag_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'article', 'tag', ['tag_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'article', type_='foreignkey')
    op.drop_column(u'article', 'tag_id')
    op.drop_table('tag')
    # ### end Alembic commands ###

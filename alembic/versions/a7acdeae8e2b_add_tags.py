"""Add tags

Revision ID: a7acdeae8e2b
Revises: a851caf3a626
Create Date: 2016-07-14 21:44:23.010805

"""

# revision identifiers, used by Alembic.
revision = 'a7acdeae8e2b'
down_revision = 'a851caf3a626'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('tag', sa.Column('name', sa.String()), )
    pass


def downgrade():
    op.drop_table('tag')
    pass

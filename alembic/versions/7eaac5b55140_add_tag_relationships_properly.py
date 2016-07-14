"""Add tag relationships properly

Revision ID: 7eaac5b55140
Revises: a7acdeae8e2b
Create Date: 2016-07-14 22:03:56.912959

"""

# revision identifiers, used by Alembic.
revision = '7eaac5b55140'
down_revision = 'a7acdeae8e2b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('mod_tags',
        sa.Column(
            'mod_id', sa.Integer, sa.ForeignKey('mod.id')
        ),
        sa.Column(
            'tag_id', sa.Integer, sa.ForeignKey('tag.id')
        )
    )
    pass


def downgrade():
    op.drop_table('mod_tags')
    pass

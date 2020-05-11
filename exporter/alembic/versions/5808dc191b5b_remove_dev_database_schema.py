"""Remove dev database schema

Revision ID: 5808dc191b5b
Revises: aa7bb1ca567b
Create Date: 2020-04-27 20:00:58.851520

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5808dc191b5b'
down_revision = 'aa7bb1ca567b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('movies')
    op.drop_table('movies_actors')
    op.drop_table('stuntmen')
    op.drop_table('contact_details')
    op.drop_table('actors')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('actors',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('actors_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('birthday', sa.DATE(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='actors_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('contact_details',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('phone_number', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('address', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('actor_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['actor_id'], ['actors.id'], name='contact_details_actor_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='contact_details_pkey')
    )
    op.create_table('stuntmen',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('active', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('actor_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['actor_id'], ['actors.id'], name='stuntmen_actor_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='stuntmen_pkey')
    )
    op.create_table('movies_actors',
    sa.Column('movie_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('actor_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['actor_id'], ['actors.id'], name='movies_actors_actor_id_fkey'),
    sa.ForeignKeyConstraint(['movie_id'], ['movies.id'], name='movies_actors_movie_id_fkey')
    )
    op.create_table('movies',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('release_date', sa.DATE(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='movies_pkey')
    )
    # ### end Alembic commands ###
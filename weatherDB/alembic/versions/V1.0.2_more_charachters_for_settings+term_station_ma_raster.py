"""more characters for settings and term column in station_ma_raster

Revision ID: V1.0.2
Revises: V1.0.0
Create Date: 2024-11-06 14:33:30.129005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'V1.0.2'
down_revision: Union[str, None] = 'V1.0.0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('settings', 'value',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.String(length=60),
               existing_comment='The value of the setting',
               existing_nullable=False)
    op.execute(sa.text("DROP VIEW IF EXISTS station_ma_quotient_view CASCADE;"))
    op.add_column(
        'station_ma_raster',
        sa.Column('term',
                  sa.VARCHAR(length=4),
                  nullable=False,
                  comment="The term of the raster. e.g. 'year', 'wihy', 'suhy'"))

    op.execute(sa.text(
        """
        UPDATE TABLE public."station_ma_raster"
            SET
                term= split_part("parameter", '_', 2),
                parameter= split_part("parameter", '_', 1)
        WHERE parameter LIKE '%_%';
        """))
    op.alter_column('station_ma_raster', 'parameter',
        existing_type=sa.VARCHAR(length=7),
        type_=sa.VARCHAR(length=3),
        comment="The parameter of the raster. e.g. 'p', 't', 'et'",
        existing_comment="The parameter of the raster. e.g. 'p_wihj', 'p_sohj', 'p_year', 't_year', 'et_year'",
        existing_nullable=False)


def downgrade() -> None:
    op.alter_column('settings', 'value',
               existing_type=sa.String(length=60),
               type_=sa.VARCHAR(length=20),
               existing_comment='The value of the setting',
               existing_nullable=False)

    op.alter_column('station_ma_raster', 'parameter',
               existing_type=sa.VARCHAR(length=3),
               type_=sa.VARCHAR(length=7),
               comment="The parameter of the raster. e.g. 'p_wihj', 'p_sohj', 'p_year', 't_year', 'et_year'",
               existing_comment="The parameter of the raster. e.g. 'p', 't', 'et'",
               existing_nullable=False)
    op.execute(sa.text(
        """
        UPDATE TABLE public."station_ma_raster"
            SET parameter= "parameter"||'_'||"term"
        WHERE parameter NOT LIKE '%_%';
        """))
    op.drop_column('station_ma_raster', 'term')

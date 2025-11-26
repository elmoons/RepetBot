"""Add new column

Revision ID: 72cd83c197fc
Revises: d322ec588001
Create Date: 2025-11-21 16:40:27.418957

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "72cd83c197fc"
down_revision: Union[str, Sequence[str], None] = "d322ec588001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Добавляем колонку как NULLABLE
    op.add_column('students_data',
                  sa.Column('type_of_exam', sa.String(), nullable=True)
                  )

    # 2. Заполняем существующие записи
    op.execute(
        "UPDATE students_data SET type_of_exam = 'ЕГЭ Математика Профильная'"
    )

    # 3. Меняем на NOT NULL
    op.alter_column('students_data', 'type_of_exam',
                    nullable=False,
                    server_default='ЕГЭ Математика Профильная')


def downgrade():
    op.drop_column('students_data', 'type_of_exam')
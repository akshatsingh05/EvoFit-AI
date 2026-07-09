"""sprint 4 personalization preferences

Revision ID: a1f4c9d2e7b1
Revises: 6b852efc7163
Create Date: 2026-07-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1f4c9d2e7b1'
down_revision: Union[str, Sequence[str], None] = '6b852efc7163'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'workout_preferences',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('workout_style', sa.String(), nullable=True),
        sa.Column('workout_location', sa.String(), nullable=True),
        sa.Column('equipment_available', sa.JSON(), nullable=False),
        sa.Column('preferred_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('workout_intensity', sa.String(), nullable=True),
        sa.Column('preferred_workout_time', sa.String(), nullable=True),
        sa.Column('favorite_muscle_groups', sa.JSON(), nullable=False),
        sa.Column('liked_exercises', sa.JSON(), nullable=False),
        sa.Column('disliked_exercises', sa.JSON(), nullable=False),
        sa.Column('avoid_movements', sa.JSON(), nullable=False),
        sa.Column('exercise_replacement_memory', sa.JSON(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )

    op.create_table(
        'nutrition_preferences',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('diet_type', sa.String(), nullable=True),
        sa.Column('cuisine_preference', sa.String(), nullable=True),
        sa.Column('budget', sa.String(), nullable=True),
        sa.Column('meals_per_day', sa.Integer(), nullable=True),
        sa.Column('favorite_foods', sa.JSON(), nullable=False),
        sa.Column('disliked_foods', sa.JSON(), nullable=False),
        sa.Column('allergies', sa.JSON(), nullable=False),
        sa.Column('water_goal_ml', sa.Integer(), nullable=True),
        sa.Column('preferred_snacks', sa.JSON(), nullable=False),
        sa.Column('cooking_time_preference', sa.String(), nullable=True),
        sa.Column('meal_replacement_memory', sa.JSON(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('nutrition_preferences')
    op.drop_table('workout_preferences')

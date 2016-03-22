"""create account table

Revision ID: 60a7a4a41e1c
Revises: 
Create Date: 2016-03-15 22:56:48.624160

"""

# revision identifiers, used by Alembic.
revision = '60a7a4a41e1c'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func

def upgrade():
    op.create_table(
        'Suggestion',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('text', sa.String(255), nullable=False),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('score', sa.Integer, nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP, server_default=func.now())
    )
    op.create_table(
        'SuggestionVote',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('value', sa.Integer, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('User.ID') ),
        sa.Column('suggestion_id', sa.Integer, sa.ForeignKey('Suggestion.id')),
        sa.Column('timestamp', sa.TIMESTAMP, server_default=func.now())
    )
    
def downgrade():
    op.drop_table('SuggestionVote')
    op.drop_table('Suggestion')
    
    
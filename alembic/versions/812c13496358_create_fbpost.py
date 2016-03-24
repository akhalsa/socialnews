"""create FBPost

Revision ID: 812c13496358
Revises: 60a7a4a41e1c
Create Date: 2016-03-23 22:28:13.470430

"""

# revision identifiers, used by Alembic.
revision = '812c13496358'
down_revision = '60a7a4a41e1c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func

def upgrade():
    op.create_table(
        'FBPost',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('tweet_id', sa.String(255), sa.ForeignKey('Tweet.twitter_id'))
    )
    
    op.create_unique_constraint("unique_fb_post", "FBPost", ["tweet_id"])


def downgrade():
    op.drop_table('FBPost')

"""Initial migration with all tables

Revision ID: 001
Revises: 
Create Date: 2025-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """データベーステーブルの作成"""
    
    # users テーブル
    op.create_table('users',
        sa.Column('management_code', sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('name', sa.String(50), nullable=True),
        sa.Column('nickname', sa.String(50), nullable=False),
        sa.Column('postal_code', sa.String(10), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('phone_number', sa.String(15), nullable=True),
        sa.Column('university', sa.String(100), nullable=True),
        sa.Column('birthdate', sa.Date(), nullable=True),
        sa.Column('profile_image_url', sa.String(255), nullable=False),
        sa.Column('student_id_image_url', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('register_type', sa.String(20), nullable=True),
        sa.Column('is_student_id_editable', sa.TINYINT(), nullable=True),
        sa.Column('is_banned', sa.TINYINT(), nullable=True),
        sa.PrimaryKeyConstraint('management_code'),
        sa.Index('idx_user_id', 'user_id')
    )
    
    # registration_itemdata テーブル
    op.create_table('registration_itemdata',
        sa.Column('management_code', sa.BIGINT(), nullable=False),
        sa.Column('subnum', sa.Integer(), nullable=False),
        sa.Column('itemtype', sa.TINYINT(), nullable=False),
        sa.Column('itemid', sa.String(128), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['management_code'], ['users.management_code'], ),
        sa.PrimaryKeyConstraint('management_code', 'subnum'),
        sa.Index('idx_registration_itemdata_itemid', 'itemid')
    )
    
    # user_stats テーブル
    op.create_table('user_stats',
        sa.Column('management_code', sa.BIGINT(), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('total_wins', sa.Integer(), nullable=True),
        sa.Column('current_win_streak', sa.Integer(), nullable=True),
        sa.Column('max_win_streak', sa.Integer(), nullable=True),
        sa.Column('hand_stats_rock', sa.Integer(), nullable=True),
        sa.Column('hand_stats_scissors', sa.Integer(), nullable=True),
        sa.Column('hand_stats_paper', sa.Integer(), nullable=True),
        sa.Column('favorite_hand', sa.String(10), nullable=True),
        sa.Column('recent_hand_results_str', sa.String(255), nullable=True),
        sa.Column('daily_wins', sa.Integer(), nullable=True),
        sa.Column('daily_losses', sa.Integer(), nullable=True),
        sa.Column('daily_draws', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(50), nullable=True),
        sa.Column('available_titles', sa.String(255), nullable=True),
        sa.Column('alias', sa.String(50), nullable=True),
        sa.Column('show_title', sa.Boolean(), nullable=True),
        sa.Column('show_alias', sa.Boolean(), nullable=True),
        sa.Column('user_rank', sa.String(20), nullable=True),
        sa.Column('last_reset_at', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['management_code'], ['users.management_code'], ),
        sa.PrimaryKeyConstraint('management_code')
    )
    
    # sessions テーブル
    op.create_table('sessions',
        sa.Column('session_id', sa.String(128), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('access_token', sa.String(512), nullable=False),
        sa.Column('refresh_token', sa.String(512), nullable=False),
        sa.Column('device_id', sa.String(128), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('last_activity', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['registration_itemdata.itemid'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('session_id'),
        sa.Index('idx_sessions_device_id', 'device_id'),
        sa.Index('idx_sessions_user_id', 'user_id')
    )
    
    # refresh_tokens テーブル
    op.create_table('refresh_tokens',
        sa.Column('token_id', sa.String(128), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('refresh_token_hash', sa.String(512), nullable=False),
        sa.Column('device_id', sa.String(128), nullable=False),
        sa.Column('issued_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False),
        sa.Column('revoked_reason', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['registration_itemdata.itemid'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('token_id'),
        sa.Index('idx_refresh_tokens_user_id', 'user_id')
    )
    
    # security_events テーブル
    op.create_table('security_events',
        sa.Column('event_id', sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('device_info', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('event_id'),
        sa.Index('idx_security_events_created_at', 'created_at'),
        sa.Index('idx_security_events_user_id', 'user_id')
    )
    
    # login_attempts テーブル
    op.create_table('login_attempts',
        sa.Column('attempt_id', sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('attempt_time', sa.DateTime(), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('failure_reason', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('attempt_id'),
        sa.Index('idx_login_attempts_ip', 'ip_address'),
        sa.Index('idx_login_attempts_time', 'attempt_time'),
        sa.Index('idx_login_attempts_user_id', 'user_id')
    )
    
    # two_factor_auth テーブル
    op.create_table('two_factor_auth',
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('secret_key', sa.String(32), nullable=False),
        sa.Column('backup_codes', sa.JSON(), nullable=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('user_id')
    )
    
    # oauth_accounts テーブル
    op.create_table('oauth_accounts',
        sa.Column('oauth_id', sa.String(128), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('provider', sa.String(20), nullable=False),
        sa.Column('provider_user_id', sa.String(255), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('profile_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('oauth_id')
    )
    
    # daily_ranking テーブル
    op.create_table('daily_ranking',
        sa.Column('ranking_position', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('wins', sa.Integer(), nullable=True),
        sa.Column('last_win_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('ranking_position')
    )
    
    # match_history テーブル
    op.create_table('match_history',
        sa.Column('fight_no', sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('player1_id', sa.String(36), nullable=False),
        sa.Column('player2_id', sa.String(36), nullable=False),
        sa.Column('player1_nickname', sa.String(50), nullable=True),
        sa.Column('player2_nickname', sa.String(50), nullable=True),
        sa.Column('player1_hand', sa.Enum('rock', 'paper', 'scissors', name='handtype'), nullable=False),
        sa.Column('player2_hand', sa.Enum('rock', 'paper', 'scissors', name='handtype'), nullable=False),
        sa.Column('player1_result', sa.Enum('win', 'lose', 'draw', name='gameresult'), nullable=False),
        sa.Column('player2_result', sa.Enum('win', 'lose', 'draw', name='gameresult'), nullable=False),
        sa.Column('winner', sa.Integer(), nullable=False),
        sa.Column('draw_count', sa.Integer(), nullable=False),
        sa.Column('match_type', sa.Enum('random', 'friend', name='matchtype'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('fight_no'),
        sa.Index('idx_p1', 'player1_id'),
        sa.Index('idx_p1_result', 'player1_id', 'player1_result'),
        sa.Index('idx_p2', 'player2_id'),
        sa.Index('idx_p2_result', 'player2_id', 'player2_result')
    )
    
    # admin_logs テーブル
    op.create_table('admin_logs',
        sa.Column('log_id', sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('admin_user', sa.String(50), nullable=False),
        sa.Column('operation', sa.String(100), nullable=False),
        sa.Column('target_id', sa.String(36), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('operated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('log_id')
    )
    
    # user_logs テーブル
    op.create_table('user_logs',
        sa.Column('log_id', sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('operation_code', sa.String(10), nullable=True),
        sa.Column('operation', sa.String(100), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('operated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('log_id'),
        sa.Index('idx_user_logs_uid', 'user_id')
    )


def downgrade():
    """データベーステーブルの削除"""
    op.drop_table('user_logs')
    op.drop_table('admin_logs')
    op.drop_table('match_history')
    op.drop_table('daily_ranking')
    op.drop_table('oauth_accounts')
    op.drop_table('two_factor_auth')
    op.drop_table('login_attempts')
    op.drop_table('security_events')
    op.drop_table('refresh_tokens')
    op.drop_table('sessions')
    op.drop_table('user_stats')
    op.drop_table('registration_itemdata')
    op.drop_table('users')
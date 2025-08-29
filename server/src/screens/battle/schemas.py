"""
バトル画面専用Pydanticスキーマ

WebSocketメッセージとレスポンスの型定義（Redis対応版）
"""

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class HandType(str, Enum):
    """じゃんけんの手"""
    rock = "rock"
    scissors = "scissors" 
    paper = "paper"


class BattleStatus(str, Enum):
    """バトル状態"""
    waiting = "waiting"           # マッチング待機中
    matched = "matched"           # マッチング成立（準備待ち）
    preparing = "preparing"       # 対戦準備中
    ready = "ready"              # 対戦準備完了（手選択待ち）
    hand_submitted = "hand_submitted"  # 手送信済み（相手待ち）
    judging = "judging"          # 結果判定中
    draw = "draw"                # 引き分け状態
    finished = "finished"        # 対戦終了
    cancelled = "cancelled"      # キャンセル・辞退


class PlayerResult(str, Enum):
    """プレイヤー個別結果"""
    win = "win"
    lose = "lose"
    draw = "draw"


class ErrorCode(str, Enum):
    """エラーコード"""
    INVALID_MESSAGE = "INVALID_MESSAGE"
    INVALID_STATE = "INVALID_STATE"
    BATTLE_NOT_FOUND = "BATTLE_NOT_FOUND"
    PLAYER_NOT_IN_BATTLE = "PLAYER_NOT_IN_BATTLE"
    INVALID_HAND = "INVALID_HAND"
    ALREADY_SUBMITTED = "ALREADY_SUBMITTED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    USER_NOT_FOUND = "USER_NOT_FOUND"


# WebSocketメッセージ基底クラス
class WebSocketMessage(BaseModel):
    """WebSocketメッセージ基底クラス"""
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    messageId: Optional[str] = None


class WebSocketResponse(BaseModel):
    """WebSocketレスポンス基底クラス"""
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    success: bool = True
    error: Optional[Dict[str, str]] = None


# インバウンドメッセージ（クライアント→サーバー）
class MatchingStartMessage(WebSocketMessage):
    """マッチング開始メッセージ"""
    type: Literal["matching_start"] = "matching_start"


class BattleReadyMessage(WebSocketMessage):
    """対戦準備完了メッセージ"""
    type: Literal["battle_ready"] = "battle_ready"


class SubmitHandMessage(WebSocketMessage):
    """手送信メッセージ"""
    type: Literal["submit_hand"] = "submit_hand"


class BattleQuitMessage(WebSocketMessage):
    """対戦辞退メッセージ"""
    type: Literal["battle_quit"] = "battle_quit"


class PingMessage(WebSocketMessage):
    """ハートビートメッセージ"""
    type: Literal["ping"] = "ping"


class GetStatsMessage(WebSocketMessage):
    """統計取得メッセージ"""
    type: Literal["get_stats"] = "get_stats"


# アウトバウンドメッセージ（サーバー→クライアント）
class ConnectionEstablishedResponse(WebSocketResponse):
    """接続確立レスポンス"""
    type: Literal["connection_established"] = "connection_established"


class MatchingStartedResponse(WebSocketResponse):
    """マッチング開始レスポンス"""
    type: Literal["matching_started"] = "matching_started"


class MatchFoundResponse(WebSocketResponse):
    """マッチング成立レスポンス"""
    type: Literal["match_found"] = "match_found"


class BattleReadyStatusResponse(WebSocketResponse):
    """対戦準備状態レスポンス"""
    type: Literal["battle_ready_status"] = "battle_ready_status"


class BattleStartResponse(WebSocketResponse):
    """バトル開始レスポンス"""
    type: Literal["battle_start"] = "battle_start"


class HandSubmittedResponse(WebSocketResponse):
    """手送信確認レスポンス"""
    type: Literal["hand_submitted"] = "hand_submitted"


class BattleResultResponse(WebSocketResponse):
    """バトル結果レスポンス"""
    type: Literal["battle_result"] = "battle_result"


class BattleDrawResponse(WebSocketResponse):
    """引き分けレスポンス"""
    type: Literal["battle_draw"] = "battle_draw"


class BattleQuitConfirmedResponse(WebSocketResponse):
    """対戦辞退確認レスポンス"""
    type: Literal["battle_quit_confirmed"] = "battle_quit_confirmed"


class OpponentQuitResponse(WebSocketResponse):
    """相手辞退通知レスポンス"""
    type: Literal["opponent_quit"] = "opponent_quit"


class HandsResetResponse(WebSocketResponse):
    """手リセット完了レスポンス"""
    type: Literal["hands_reset"] = "hands_reset"


class PongResponse(WebSocketResponse):
    """ハートビート応答レスポンス"""
    type: Literal["pong"] = "pong"


class StatsResponse(WebSocketResponse):
    """統計情報レスポンス"""
    type: Literal["stats_response"] = "stats_response"


class ErrorResponse(WebSocketResponse):
    """エラーレスポンス"""
    type: Literal["error"] = "error"
    success: bool = False
    error: Dict[str, Any] = Field(..., description="エラー詳細")


# データ構造
class PlayerInfo(BaseModel):
    """プレイヤー情報"""
    userId: str
    nickname: str
    profileImageUrl: Optional[str] = None
    isReady: bool = False
    hand: Optional[str] = None


# バトル画面専用ユーザー情報API用スキーマ
class BattleUserInfo(BaseModel):
    """バトル画面用ユーザー基本情報"""
    userId: str
    nickname: str
    profileImageUrl: Optional[str] = None
    level: int = 1
    experience: int = 0
    rank: str = "bronze"


class BattleUserStats(BaseModel):
    """バトル画面用ユーザー統計情報"""
    userId: str
    totalBattles: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    winRate: float = 0.0
    currentStreak: int = 0
    bestStreak: int = 0
    rank: str = "bronze"
    level: int = 1
    experience: int = 0
    nextLevelExp: int = 200


class BattleUserPreferences(BaseModel):
    """バトル画面用ユーザー設定"""
    autoMatching: bool = True
    soundEnabled: bool = True
    vibrationEnabled: bool = False
    theme: str = "dark"


class BattleUserInfoResponse(BaseModel):
    """バトル画面用ユーザー情報レスポンス"""
    success: bool = True
    data: Dict[str, Any] = Field(..., description="ユーザー情報データ")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class BattleUserStatsResponse(BaseModel):
    """バトル画面用ユーザー統計レスポンス"""
    success: bool = True
    data: Dict[str, Any] = Field(..., description="ユーザー統計データ")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class BattleErrorResponse(BaseModel):
    """バトル画面用エラーレスポンス"""
    success: bool = False
    error: Dict[str, str] = Field(..., description="エラー詳細")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class BattleResult(BaseModel):
    """バトル結果"""
    player1: PlayerInfo
    player2: PlayerInfo
    winner: int  # 1=player1, 2=player2, 3=draw
    isDraw: bool
    drawCount: int
    isFinished: bool


class MatchingInfo(BaseModel):
    """マッチング情報"""
    matchingId: str
    status: str
    queuePosition: Optional[int] = None
    estimatedWaitTime: Optional[int] = None


class BattleStatusInfo(BaseModel):
    """バトル状態情報"""
    battleId: str
    status: str
    player1Ready: bool
    player2Ready: bool
    message: str


# Redis用データ構造
class RedisConnectionState(BaseModel):
    """Redis接続状態"""
    user_id: str
    nickname: str
    connected_at: str
    status: str


class RedisMatchingState(BaseModel):
    """Redisマッチング状態"""
    matching_id: str
    joined_at: str
    status: str


class RedisBattleState(BaseModel):
    """Redisバトル状態"""
    battle_id: str
    status: str
    player1: Optional[Dict[str, Any]] = None
    player2: Optional[Dict[str, Any]] = None
    created_at: str
    started_at: Optional[str] = None
    draw_count: int = 0


class RedisBattleStats(BaseModel):
    """Redisバトル統計"""
    total_battles: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    win_rate: float = 0.0
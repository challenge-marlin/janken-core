"""
バトル画面専用Pydanticスキーマ

WebSocketメッセージとレスポンスの型定義
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


class ResetHandsMessage(WebSocketMessage):
    """手リセットメッセージ"""
    type: Literal["reset_hands"] = "reset_hands"


class BattleQuitMessage(WebSocketMessage):
    """対戦辞退メッセージ"""
    type: Literal["battle_quit"] = "battle_quit"


# アウトバウンドメッセージ（サーバー→クライアント）
class ConnectionEstablishedResponse(WebSocketResponse):
    """接続確立レスポンス"""
    type: Literal["connection_established"] = "connection_established"


class MatchingStartedResponse(WebSocketResponse):
    """マッチング開始レスポンス"""
    type: Literal["matching_started"] = "matching_started"


class MatchingStatusResponse(WebSocketResponse):
    """マッチング状態更新レスポンス"""
    type: Literal["matching_status"] = "matching_status"


class MatchFoundResponse(WebSocketResponse):
    """マッチング成立レスポンス"""
    type: Literal["match_found"] = "match_found"


class BattleReadyStatusResponse(WebSocketResponse):
    """対戦準備状態レスポンス"""
    type: Literal["battle_ready_status"] = "battle_ready_status"


class BattleStartResponse(WebSocketResponse):
    """対戦開始レスポンス"""
    type: Literal["battle_start"] = "battle_start"


class HandSubmittedResponse(WebSocketResponse):
    """手送信確認レスポンス"""
    type: Literal["hand_submitted"] = "hand_submitted"


class BattleResultResponse(WebSocketResponse):
    """対戦結果レスポンス"""
    type: Literal["battle_result"] = "battle_result"


class BattleDrawResponse(WebSocketResponse):
    """引き分けレスポンス"""
    type: Literal["battle_draw"] = "battle_draw"


class HandsResetResponse(WebSocketResponse):
    """手リセット完了レスポンス"""
    type: Literal["hands_reset"] = "hands_reset"


class BattleQuitConfirmedResponse(WebSocketResponse):
    """対戦辞退確認レスポンス"""
    type: Literal["battle_quit_confirmed"] = "battle_quit_confirmed"


class OpponentQuitResponse(WebSocketResponse):
    """相手辞退通知レスポンス"""
    type: Literal["opponent_quit"] = "opponent_quit"


class ErrorResponse(WebSocketResponse):
    """エラーレスポンス"""
    type: Literal["error"] = "error"
    success: bool = False


# データ構造
class OpponentInfo(BaseModel):
    """対戦相手情報"""
    userId: str
    nickname: str
    profileImageUrl: Optional[str] = None


class PlayerInfo(BaseModel):
    """プレイヤー情報"""
    userId: str
    hand: Optional[HandType] = None
    result: Optional[PlayerResult] = None


class BattleResult(BaseModel):
    """対戦結果"""
    player1: PlayerInfo
    player2: PlayerInfo
    winner: int  # 1: player1, 2: player2, 3: draw
    isDraw: bool
    drawCount: int = 0
    isFinished: bool


# エラーコード
class ErrorCode(str, Enum):
    """エラーコード"""
    INVALID_MESSAGE = "INVALID_MESSAGE"
    BATTLE_NOT_FOUND = "BATTLE_NOT_FOUND"
    PLAYER_NOT_IN_BATTLE = "PLAYER_NOT_IN_BATTLE"
    INVALID_HAND = "INVALID_HAND"
    INVALID_STATE = "INVALID_STATE"
    ALREADY_SUBMITTED = "ALREADY_SUBMITTED"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    TIMEOUT = "TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
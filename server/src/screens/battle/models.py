"""
バトル画面専用データモデル

WebSocketバトルセッション管理用のデータ構造
"""

from typing import Optional, Dict, Set
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from .schemas import HandType, BattleStatus, PlayerResult


@dataclass
class BattlePlayer:
    """バトルプレイヤー情報"""
    user_id: str
    nickname: str
    profile_image_url: Optional[str] = None
    hand: Optional[HandType] = None
    is_ready: bool = False
    connection_id: Optional[str] = None
    connected_at: Optional[datetime] = None


@dataclass
class BattleSession:
    """バトルセッション"""
    battle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: BattleStatus = BattleStatus.waiting
    player1: Optional[BattlePlayer] = None
    player2: Optional[BattlePlayer] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    draw_count: int = 0
    
    def is_full(self) -> bool:
        """セッションが満員かどうか"""
        return self.player1 is not None and self.player2 is not None
    
    def add_player(self, player: BattlePlayer) -> bool:
        """プレイヤーを追加"""
        if self.player1 is None:
            self.player1 = player
            return True
        elif self.player2 is None:
            self.player2 = player
            return True
        return False
    
    def get_player(self, user_id: str) -> Optional[BattlePlayer]:
        """ユーザーIDでプレイヤーを取得"""
        if self.player1 and self.player1.user_id == user_id:
            return self.player1
        elif self.player2 and self.player2.user_id == user_id:
            return self.player2
        return None
    
    def get_opponent(self, user_id: str) -> Optional[BattlePlayer]:
        """相手プレイヤーを取得"""
        if self.player1 and self.player1.user_id == user_id:
            return self.player2
        elif self.player2 and self.player2.user_id == user_id:
            return self.player1
        return None
    
    def get_player_number(self, user_id: str) -> Optional[int]:
        """プレイヤー番号を取得（1 or 2）"""
        if self.player1 and self.player1.user_id == user_id:
            return 1
        elif self.player2 and self.player2.user_id == user_id:
            return 2
        return None
    
    def both_ready(self) -> bool:
        """両プレイヤーが準備完了かどうか"""
        return (self.player1 and self.player1.is_ready and 
                self.player2 and self.player2.is_ready)
    
    def both_submitted_hands(self) -> bool:
        """両プレイヤーが手を送信済みかどうか"""
        return (self.player1 and self.player1.hand is not None and
                self.player2 and self.player2.hand is not None)
    
    def reset_hands(self):
        """手をリセット"""
        if self.player1:
            self.player1.hand = None
        if self.player2:
            self.player2.hand = None
    
    def judge_battle(self) -> tuple[PlayerResult, PlayerResult, int]:
        """バトル結果を判定
        
        Returns:
            tuple: (player1_result, player2_result, winner)
                  winner: 1=player1, 2=player2, 3=draw
        """
        if not self.both_submitted_hands():
            raise ValueError("Both players must submit hands before judging")
        
        hand1 = self.player1.hand
        hand2 = self.player2.hand
        
        # 引き分け
        if hand1 == hand2:
            return PlayerResult.draw, PlayerResult.draw, 3
        
        # 勝敗判定
        winning_combinations = {
            (HandType.rock, HandType.scissors): (PlayerResult.win, PlayerResult.lose, 1),
            (HandType.scissors, HandType.paper): (PlayerResult.win, PlayerResult.lose, 1),
            (HandType.paper, HandType.rock): (PlayerResult.win, PlayerResult.lose, 1),
            (HandType.scissors, HandType.rock): (PlayerResult.lose, PlayerResult.win, 2),
            (HandType.paper, HandType.scissors): (PlayerResult.lose, PlayerResult.win, 2),
            (HandType.rock, HandType.paper): (PlayerResult.lose, PlayerResult.win, 2),
        }
        
        return winning_combinations.get((hand1, hand2), (PlayerResult.draw, PlayerResult.draw, 3))


@dataclass
class MatchingQueue:
    """マッチングキュー"""
    user_id: str
    matching_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    joined_at: datetime = field(default_factory=datetime.now)
    player_info: Optional[BattlePlayer] = None


class BattleManager:
    """バトル管理クラス"""
    
    def __init__(self):
        # アクティブな接続管理
        self.active_connections: Dict[str, any] = {}  # user_id -> WebSocket
        
        # マッチングキュー
        self.matching_queue: Dict[str, MatchingQueue] = {}  # user_id -> MatchingQueue
        
        # アクティブなバトルセッション
        self.active_battles: Dict[str, BattleSession] = {}  # battle_id -> BattleSession
        
        # ユーザーのバトルマッピング
        self.user_battles: Dict[str, str] = {}  # user_id -> battle_id
    
    def add_connection(self, user_id: str, websocket):
        """WebSocket接続を追加"""
        self.active_connections[user_id] = websocket
    
    def remove_connection(self, user_id: str):
        """WebSocket接続を削除"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # マッチングキューから削除
        if user_id in self.matching_queue:
            del self.matching_queue[user_id]
        
        # バトルセッションからも削除（辞退として処理）
        if user_id in self.user_battles:
            battle_id = self.user_battles[user_id]
            if battle_id in self.active_battles:
                battle = self.active_battles[battle_id]
                battle.status = BattleStatus.cancelled
    
    def add_to_matching_queue(self, user_id: str, player_info: BattlePlayer) -> MatchingQueue:
        """マッチングキューに追加"""
        matching = MatchingQueue(user_id=user_id, player_info=player_info)
        self.matching_queue[user_id] = matching
        return matching
    
    def find_match(self, user_id: str) -> Optional[tuple[BattleSession, BattlePlayer]]:
        """マッチング相手を探す"""
        # 自分以外のキューイング中ユーザーを探す
        for other_user_id, other_matching in self.matching_queue.items():
            if other_user_id != user_id:
                # マッチング成立
                current_matching = self.matching_queue[user_id]
                
                # バトルセッション作成
                battle = BattleSession()
                battle.add_player(other_matching.player_info)
                battle.add_player(current_matching.player_info)
                battle.status = BattleStatus.matched
                
                # セッション管理に追加
                self.active_battles[battle.battle_id] = battle
                self.user_battles[user_id] = battle.battle_id
                self.user_battles[other_user_id] = battle.battle_id
                
                # マッチングキューから削除
                del self.matching_queue[user_id]
                del self.matching_queue[other_user_id]
                
                return battle, other_matching.player_info
        
        return None
    
    def get_battle(self, battle_id: str) -> Optional[BattleSession]:
        """バトルセッションを取得"""
        return self.active_battles.get(battle_id)
    
    def get_user_battle(self, user_id: str) -> Optional[BattleSession]:
        """ユーザーのバトルセッションを取得"""
        battle_id = self.user_battles.get(user_id)
        if battle_id:
            return self.active_battles.get(battle_id)
        return None
    
    def finish_battle(self, battle_id: str):
        """バトルを終了"""
        if battle_id in self.active_battles:
            battle = self.active_battles[battle_id]
            battle.status = BattleStatus.finished
            battle.finished_at = datetime.now()
            
            # ユーザーマッピングから削除
            if battle.player1:
                self.user_battles.pop(battle.player1.user_id, None)
            if battle.player2:
                self.user_battles.pop(battle.player2.user_id, None)
            
            # セッションから削除
            del self.active_battles[battle_id]
    
    def get_queue_position(self, user_id: str) -> int:
        """キュー内の位置を取得"""
        queue_users = sorted(
            self.matching_queue.keys(),
            key=lambda uid: self.matching_queue[uid].joined_at
        )
        try:
            return queue_users.index(user_id) + 1
        except ValueError:
            return 0
    
    def get_active_connections_count(self) -> int:
        """アクティブ接続数を取得"""
        return len(self.active_connections)
    
    def get_active_battles_count(self) -> int:
        """アクティブバトル数を取得"""
        return len(self.active_battles)
    
    def get_queue_count(self) -> int:
        """マッチングキュー数を取得"""
        return len(self.matching_queue)


# グローバルバトルマネージャーインスタンス
battle_manager = BattleManager()
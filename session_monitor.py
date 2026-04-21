# services/session_monitor.py
"""
📊 SESSION MONITOR v2.0 — мониторинг активных сессий
✅ Отслеживание действий в сессии
✅ Система усталости и настроения
✅ Real-time статистика
✅ Профили поведения
"""

from __future__ import annotations

from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from services.logger import Logger
from services.notifier import TelegramNotifier


class ActionType(Enum):
    """Типы действий"""
    
    SEARCH = "search"
    VIEW_ITEM = "view_item"
    ADD_FAVORITE = "add_favorite"
    VIEW_SELLER = "view_seller"
    READ_REVIEW = "read_review"
    LOGIN = "login"
    WARMUP = "warmup"
    ALIVE_MODE = "alive_mode"


class SessionStatus:
    """Статус сессии"""
    
    def __init__(self, acc_id: str, phone: str):
        """Инициализация"""
        
        self.acc_id = acc_id
        self.phone = phone
        self.start_time = datetime.now()
        
        # Счётчики
        self.actions_count = 0
        self.errors_count = 0
        self.search_count = 0
        self.view_count = 0
        self.favorites_count = 0
        
        # Система усталости
        self.tiredness = 0.1  # 0-1
        self.mood = "happy"  # happy, neutral, tired, bored
        
        # Поведение
        self.last_action_time = datetime.now()
        self.action_history: list = []
    
    @property
    def elapsed_time(self) -> float:
        """Прошедшее время (секунды)"""
        return (datetime.now() - self.start_time).total_seconds()
    
    @property
    def actions_per_minute(self) -> float:
        """Действий в минуту"""
        elapsed_minutes = self.elapsed_time / 60
        if elapsed_minutes < 1:
            return 0
        return self.actions_count / elapsed_minutes
    
    def update_tiredness(self) -> None:
        """Обновить усталость"""
        
        self.tiredness = min(1.0, self.tiredness + 0.05)
        
        # Обновляем mood
        if self.tiredness > 0.8:
            self.mood = "tired"
        elif self.tiredness > 0.6:
            self.mood = "neutral"
        else:
            self.mood = "happy"
    
    def record_action(self, action_type: ActionType, success: bool = True) -> None:
        """Записать действие"""
        
        self.actions_count += 1
        self.last_action_time = datetime.now()
        
        if action_type == ActionType.SEARCH:
            self.search_count += 1
        elif action_type == ActionType.VIEW_ITEM:
            self.view_count += 1
        elif action_type == ActionType.ADD_FAVORITE:
            self.favorites_count += 1
        
        if not success:
            self.errors_count += 1
        
        self.action_history.append({
            "action": action_type.value,
            "timestamp": datetime.now(),
            "success": success,
        })
        
        # Обновляем усталость каждые 10 действий
        if self.actions_count % 10 == 0:
            self.update_tiredness()
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        
        return {
            "acc_id": self.acc_id,
            "phone": self.phone,
            "elapsed_time": self.elapsed_time,
            "actions_count": self.actions_count,
            "errors_count": self.errors_count,
            "search_count": self.search_count,
            "view_count": self.view_count,
            "favorites_count": self.favorites_count,
            "actions_per_minute": round(self.actions_per_minute, 2),
            "tiredness": round(self.tiredness, 2),
            "mood": self.mood,
        }


class SessionMonitor:
    """
    📊 SESSION MONITOR — мониторинг активных сессий
    """
    
    def __init__(
        self,
        logger: Logger,
        notifier: Optional[TelegramNotifier] = None
    ):
        """Инициализация"""
        
        self.logger = logger
        self.notifier = notifier
        
        # Активные сессии
        self.sessions: Dict[str, SessionStatus] = {}
    
    def init_session(self, acc_id: str, phone: str) -> None:
        """Инициализировать сессию"""
        
        self.sessions[acc_id] = SessionStatus(acc_id, phone)
        self.logger.info(acc_id, f"📊 Session started")
    
    def get_session_status(self, acc_id: str) -> Optional[Dict[str, Any]]:
        """Получить статус сессии"""
        
        if acc_id in self.sessions:
            return self.sessions[acc_id].to_dict()
        
        return None
    
    def record_action(
        self,
        acc_id: str,
        action_type: ActionType,
        success: bool = True
    ) -> None:
        """Записать действие"""
        
        if acc_id not in self.sessions:
            return
        
        self.sessions[acc_id].record_action(action_type, success)
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Получить глобальную статистику"""
        
        total_actions = sum(s.actions_count for s in self.sessions.values())
        total_errors = sum(s.errors_count for s in self.sessions.values())
        
        if not self.sessions:
            return {
                "total_actions": 0,
                "total_errors": 0,
                "total_accounts": 0,
                "elapsed_time": 0,
            }
        
        first_session_start = min(s.start_time for s in self.sessions.values())
        elapsed_time = (datetime.now() - first_session_start).total_seconds()
        
        return {
            "total_actions": total_actions,
            "total_errors": total_errors,
            "total_accounts": len(self.sessions),
            "elapsed_time": elapsed_time,
        }
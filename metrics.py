# services/metrics.py
"""
📊 METRICS v2.0 — сбор метрик и статистики
✅ Отслеживание действий по аккаунтам
✅ Отслеживание ошибок
✅ Отслеживание времени
✅ Итоговая статистика
"""

from __future__ import annotations

from typing import Dict, Any, Optional
from datetime import datetime
from services.logger import Logger


class MetricsCollector:
    """
    📊 METRICS COLLECTOR — сбор метрик
    """
    
    def __init__(self, logger: Logger):
        """Инициализация"""
        
        self.logger = logger
        self.start_time = datetime.now()
        
        # Счётчики по аккаунтам
        self.actions_by_account: Dict[str, int] = {}
        self.errors_by_account: Dict[str, int] = {}
        self.logins_by_account: Dict[str, int] = {}
        self.warmups_by_account: Dict[str, int] = {}
        
        # Глобальные счётчики
        self.total_actions = 0
        self.total_errors = 0
        self.total_logins = 0
        self.total_warmups = 0
    
    def record_action(self, acc_id: str) -> None:
        """Записать действие"""
        
        self.total_actions += 1
        self.actions_by_account[acc_id] = self.actions_by_account.get(acc_id, 0) + 1
    
    def record_error(self, acc_id: str) -> None:
        """Записать ошибку"""
        
        self.total_errors += 1
        self.errors_by_account[acc_id] = self.errors_by_account.get(acc_id, 0) + 1
    
    def record_login(self, acc_id: str) -> None:
        """Записать логин"""
        
        self.total_logins += 1
        self.logins_by_account[acc_id] = self.logins_by_account.get(acc_id, 0) + 1
    
    def record_warmup(self, acc_id: str) -> None:
        """Записать прогрев"""
        
        self.total_warmups += 1
        self.warmups_by_account[acc_id] = self.warmups_by_account.get(acc_id, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику"""
        
        uptime = (datetime.now() - self.start_time).total_seconds() / 3600
        
        return {
            "uptime_hours": round(uptime, 2),
            "total_actions": self.total_actions,
            "total_errors": self.total_errors,
            "total_logins": self.total_logins,
            "total_warmups": self.total_warmups,
            "actions_by_account": self.actions_by_account,
            "errors_by_account": self.errors_by_account,
            "logins_by_account": self.logins_by_account,
            "warmups_by_account": self.warmups_by_account,
        }
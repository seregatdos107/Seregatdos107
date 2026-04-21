# services/action_logger.py
"""
📝 ACTION LOGGER v2.0 — логирование действий в сессии
✅ Логирование всех действий
✅ Info, Warning, Error уровни
✅ Специальные логи для warmup и alive mode
"""

from __future__ import annotations

from typing import Optional
from datetime import datetime
from services.session_monitor import SessionMonitor, ActionType


class ActionLogger:
    """
    📝 ACTION LOGGER — логирование действий
    """
    
    def __init__(self, session_monitor: SessionMonitor):
        """Инициализация"""
        
        self.session_monitor = session_monitor
    
    async def log_info(self, acc_id: str, message: str) -> None:
        """ℹ️ Информационное логирование"""
        print(f"  {message}")
    
    async def log_warning(self, acc_id: str, message: str) -> None:
        """⚠️ Предупреждение"""
        print(f"  ⚠️ {message}")
    
    async def log_error(
        self,
        acc_id: str,
        message: str,
        severity: str = "MEDIUM"
    ) -> None:
        """❌ Ошибка"""
        print(f"  ❌ [{severity}] {message}")
        self.session_monitor.record_action(acc_id, ActionType.VIEW_ITEM, success=False)
    
    async def log_warmup_phase(
        self,
        acc_id: str,
        phase: int,
        total_phases: int,
        duration_minutes: float
    ) -> None:
        """🔥 Логирование фазы прогрева"""
        print(f"  ✅ Фаза {phase}/{total_phases} завершена ({duration_minutes:.1f} мин)")
        self.session_monitor.record_action(acc_id, ActionType.WARMUP)
    
    async def log_alive_mode_start(self, acc_id: str, phone: str) -> None:
        """🤖 Начало Alive Mode"""
        print(f"  🤖 Alive Mode запущен")
    
    async def log_alive_mode_stop(self, acc_id: str, iterations: int) -> None:
        """🤖 Остановка Alive Mode"""
        print(f"  ⏹️ Alive Mode остановлен ({iterations} итераций)")
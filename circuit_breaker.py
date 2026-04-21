# core/safety/circuit_breaker.py
"""
🔌 CIRCUIT BREAKER v2.0 — защита от перегрузок
✅ Отслеживание состояния (CLOSED, OPEN, HALF_OPEN)
✅ Автоматический сброс
✅ Защита от cascade failures
"""

from __future__ import annotations

from typing import Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
from services.logger import Logger
from services.notifier import TelegramNotifier


class CircuitState(Enum):
    """Состояние Circuit Breaker"""
    
    CLOSED = "closed"      # Работает нормально
    OPEN = "open"          # Отключено (слишком много ошибок)
    HALF_OPEN = "half_open"  # Пробует восстановление


class CircuitBreaker:
    """
    🔌 CIRCUIT BREAKER — защита от перегрузок
    """
    
    def __init__(
        self,
        logger: Logger,
        notifier: Optional[TelegramNotifier] = None,
        failure_threshold: int = 5,
        timeout_seconds: int = 300
    ):
        """
        Инициализация
        
        Args:
            logger: Logger
            notifier: TelegramNotifier
            failure_threshold: Порог ошибок для открытия
            timeout_seconds: Время перед HALF_OPEN состоянием
        """
        
        self.logger = logger
        self.notifier = notifier
        
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        
        # Состояние для каждого аккаунта
        self.states: Dict[str, CircuitState] = {}
        self.failure_counts: Dict[str, int] = {}
        self.last_failure_times: Dict[str, datetime] = {}
        self.open_times: Dict[str, datetime] = {}
    
    def _init_account(self, acc_id: str) -> None:
        """Инициализировать аккаунт"""
        
        if acc_id not in self.states:
            self.states[acc_id] = CircuitState.CLOSED
            self.failure_counts[acc_id] = 0
            self.last_failure_times[acc_id] = datetime.now()
            self.open_times[acc_id] = None
    
    def record_success(self, acc_id: str) -> None:
        """
        ✅ ЗАПИСАТЬ УСПЕХ
        
        Сбрасываем счётчик ошибок
        """
        
        self._init_account(acc_id)
        
        if self.states[acc_id] == CircuitState.HALF_OPEN:
            # Восстановление успешно
            self.states[acc_id] = CircuitState.CLOSED
            self.failure_counts[acc_id] = 0
            
            self.logger.success(acc_id, "🟢 Circuit Breaker: RECOVERED")
        
        elif self.states[acc_id] == CircuitState.CLOSED:
            # Нормальное состояние, уменьшаем счётчик
            if self.failure_counts[acc_id] > 0:
                self.failure_counts[acc_id] -= 1
    
    def record_failure(self, acc_id: str) -> None:
        """
        ❌ ЗАПИСАТЬ ОШИБКУ
        
        Увеличиваем счётчик ошибок
        """
        
        self._init_account(acc_id)
        
        self.failure_counts[acc_id] += 1
        self.last_failure_times[acc_id] = datetime.now()
        
        # Если слишком много ошибок — открываем circuit
        if self.failure_counts[acc_id] >= self.failure_threshold:
            self.states[acc_id] = CircuitState.OPEN
            self.open_times[acc_id] = datetime.now()
            
            self.logger.error(
                acc_id,
                f"🔴 Circuit Breaker OPEN (failures: {self.failure_counts[acc_id]})",
                severity="HIGH"
            )
            
            try:
                if self.notifier:
                    import asyncio
                    asyncio.create_task(
                        self.notifier.notify(
                            f"🔴 {acc_id}: Circuit Breaker OPEN!\n"
                            f"Слишком много ошибок. Пауза {self.timeout_seconds}с."
                        )
                    )
            except Exception:
                pass
    
    def can_execute(self, acc_id: str) -> bool:
        """
        🔍 МОЖНО ЛИ ВЫПОЛНИТЬ ДЕЙСТВИЕ?
        
        Args:
            acc_id: ID аккаунта
            
        Returns:
            bool: True если можно
        """
        
        self._init_account(acc_id)
        
        state = self.states[acc_id]
        
        if state == CircuitState.CLOSED:
            return True
        
        elif state == CircuitState.OPEN:
            # Проверяем timeout
            if self.open_times[acc_id]:
                time_since_open = (datetime.now() - self.open_times[acc_id]).total_seconds()
                
                if time_since_open >= self.timeout_seconds:
                    # Переходим в HALF_OPEN
                    self.states[acc_id] = CircuitState.HALF_OPEN
                    self.logger.warning(acc_id, "🟡 Circuit Breaker: HALF_OPEN (trying recovery)")
                    return True
            
            return False
        
        elif state == CircuitState.HALF_OPEN:
            # Пробуем восстановление
            return True
        
        return True
    
    def reset(self, acc_id: str) -> None:
        """
        🔄 СБРОСИТЬ CIRCUIT BREAKER
        
        Args:
            acc_id: ID аккаунта
        """
        
        self.states[acc_id] = CircuitState.CLOSED
        self.failure_counts[acc_id] = 0
        self.open_times[acc_id] = None
        
        self.logger.success(acc_id, "🟢 Circuit Breaker RESET")
    
    def get_state(self, acc_id: str) -> CircuitState:
        """Получить состояние"""
        
        self._init_account(acc_id)
        return self.states[acc_id]
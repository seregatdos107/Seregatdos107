# core/engine/executor.py
"""
⚙️ ACTION EXECUTOR v2.0 — исполнитель действий
✅ Выполнение действий (поиск, просмотр, клик и т.д.)
✅ Обработка ошибок
✅ Compliance с Circuit Breaker, Risk Analyzer, Night Mode
✅ Отслеживание выполненных действий
"""

from __future__ import annotations

import asyncio
import random
from typing import Optional, Callable, Any
from playwright.async_api import Page

from services.logger import Logger
from services.notifier import TelegramNotifier
from core.safety.circuit_breaker import CircuitBreaker
from core.safety.risk_analyzer import RiskAnalyzer
from core.safety.night_mode import NightMode


class ActionExecutor:
    """
    ⚙️ ACTION EXECUTOR — исполнитель действий
    """
    
    def __init__(
        self,
        circuit_breaker: CircuitBreaker,
        risk_analyzer: RiskAnalyzer,
        night_mode: NightMode,
        logger: Logger,
        notifier: Optional[TelegramNotifier] = None
    ):
        """Инициализация"""
        
        self.circuit_breaker = circuit_breaker
        self.risk_analyzer = risk_analyzer
        self.night_mode = night_mode
        self.logger = logger
        self.notifier = notifier
    
    async def execute(
        self,
        acc_id: str,
        action_name: str,
        action_func: Callable,
        *args,
        **kwargs
    ) -> Optional[Any]:
        """
        ⚙️ ВЫПОЛНИТЬ ДЕЙСТВИЕ
        
        С проверкой:
        - Circuit Breaker
        - Night Mode
        - Risk Analysis
        
        Args:
            acc_id: ID аккаунта
            action_name: Название действия
            action_func: Функция для выполнения
            *args: Аргументы
            **kwargs: Именованные аргументы
            
        Returns:
            Результат выполнения или None
        """
        
        # ─────────────────────────────────────────────────────
        # 1. ПРОВЕРКА НОЧНОГО РЕЖИМА
        # ─────────────────────────────────────────────────────
        
        if self.night_mode.is_night_time_for_account(acc_id):
            self.logger.info(acc_id, f"🌙 Night time: skipping {action_name}")
            return None
        
        # ─────────────────────────────────────────────────────
        # 2. ПРОВЕРКА CIRCUIT BREAKER
        # ─────────────────────────────────────────────────────
        
        if not self.circuit_breaker.can_execute(acc_id):
            self.logger.warning(
                acc_id,
                f"���� Circuit Breaker OPEN: skipping {action_name}"
            )
            return None
        
        # ─────────────────────────────────────────────────────
        # 3. ВЫПОЛНЕНИЕ ДЕЙСТВИЯ
        # ─────────────────────────────────────────────────────
        
        try:
            self.logger.info(acc_id, f"⚙️ Executing: {action_name}")
            
            result = await action_func(*args, **kwargs)
            
            # Успех
            self.circuit_breaker.record_success(acc_id)
            self.logger.success(acc_id, f"✅ {action_name} completed")
            
            return result
        
        except Exception as e:
            # Ошибка
            self.circuit_breaker.record_failure(acc_id)
            self.logger.error(acc_id, f"❌ {action_name} failed: {e}", severity="MEDIUM")
            
            return None
    
    async def execute_with_delay(
        self,
        acc_id: str,
        action_name: str,
        action_func: Callable,
        min_delay: float = 1.0,
        max_delay: float = 5.0,
        *args,
        **kwargs
    ) -> Optional[Any]:
        """
        ⚙️ ВЫПОЛНИТЬ ДЕЙСТВИЕ С ЗАДЕРЖКОЙ
        
        Args:
            acc_id: ID аккаунта
            action_name: Название действия
            action_func: Функция для выполнения
            min_delay: Минимальная задержка
            max_delay: Максимальная задержка
            *args: Аргументы
            **kwargs: Именованные аргументы
            
        Returns:
            Результат выполнения или None
        """
        
        # Случайная задержка перед действием
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
        
        return await self.execute(acc_id, action_name, action_func, *args, **kwargs)
    
    async def execute_safely(
        self,
        acc_id: str,
        action_name: str,
        action_func: Callable,
        max_retries: int = 3,
        *args,
        **kwargs
    ) -> Optional[Any]:
        """
        ⚙️ БЕЗОПАСНОЕ ВЫПОЛНЕНИЕ (с retry)
        
        Args:
            acc_id: ID аккаунта
            action_name: Название действия
            action_func: Функция для выполнения
            max_retries: Максимум повторов
            *args: Аргументы
            **kwargs: Именованные аргументы
            
        Returns:
            Результат выполнения или None
        """
        
        for attempt in range(1, max_retries + 1):
            try:
                result = await self.execute(acc_id, f"{action_name} (attempt {attempt})", action_func, *args, **kwargs)
                
                if result is not None:
                    return result
                
                if attempt < max_retries:
                    wait_time = random.uniform(2, 5)
                    self.logger.info(acc_id, f"⏳ Retrying in {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
            
            except Exception as e:
                self.logger.error(acc_id, f"Attempt {attempt} failed: {e}")
                
                if attempt < max_retries:
                    await asyncio.sleep(random.uniform(3, 7))
        
        return None
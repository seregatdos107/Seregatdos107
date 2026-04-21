# core/safety/night_mode.py
"""
🌙 NIGHT MODE v2.0 — ночной режим с graceful shutdown и soft resume
✅ Graceful shutdown (закрытие браузера ночью)
✅ Сохранение сессии
✅ Soft resume утром (5–10 мин спокойного поведения)
✅ Автоматический запуск Alive Mode после resume
"""

from __future__ import annotations

from datetime import datetime, time
from typing import Optional, Dict
from services.logger import Logger
from services.notifier import TelegramNotifier


class NightMode:
    """
    🌙 NIGHT MODE v2.0
    
    Управляет ночным режимом:
    - Graceful shutdown (закрытие браузера в 23:00)
    - Сохранение сессии
    - Soft resume утром (6:00)
    - 5–10 минут спокойного поведения перед запуском Alive Mode
    """
    
    def __init__(self, logger: Logger, notifier: Optional[TelegramNotifier] = None):
        """Инициализация"""
        
        self.logger = logger
        self.notifier = notifier
        
        # Время начала и конца ночи
        self.night_start_time = time(23, 0)  # 23:00
        self.night_end_time = time(6, 0)     # 6:00
        
        # Overrides для каждого аккаунта (отключение ночного режима)
        self.overrides: Dict[str, datetime] = {}
    
    def is_night_time(self) -> bool:
        """
        🌙 ПРОВЕРИТЬ НАСТУПИЛА ЛИ НОЧЬ
        
        Returns:
            bool: True если ночь, False если день
        """
        
        current_time = datetime.now().time()
        
        if current_time >= self.night_start_time or current_time < self.night_end_time:
            return True
        
        return False
    
    def is_night_time_for_account(self, acc_id: str) -> bool:
        """
        🌙 ПРОВЕРИТЬ НОЧЬ ДЛЯ КОНКРЕТНОГО АККАУНТА (с учётом override)
        
        Args:
            acc_id: ID аккаунта
            
        Returns:
            bool: True если ночь для этого аккаунта
        """
        
        # Если есть override — проверяем его
        if acc_id in self.overrides:
            override_end = self.overrides[acc_id]
            if datetime.now() < override_end:
                return False  # Override ещё активен, ночи нет
            else:
                del self.overrides[acc_id]  # Override истёк, удаляем
        
        return self.is_night_time()
    
    def override(self, acc_id: str, hours: float):
        """
        ☀️ ОТКЛЮЧИТЬ НОЧНОЙ РЕЖИМ НА N ЧАСОВ
        
        Args:
            acc_id: ID аккаунта
            hours: Количество часов
        """
        
        from datetime import timedelta
        
        self.overrides[acc_id] = datetime.now() + timedelta(hours=hours)
        self.logger.success(acc_id, f"🌞 Night mode override: {hours} hours")
    
    def reset_override(self, acc_id: str):
        """
        🌙 ВЕРНУТЬ НОЧНОЙ РЕЖИМ
        
        Args:
            acc_id: ID аккаунта
        """
        
        if acc_id in self.overrides:
            del self.overrides[acc_id]
        
        self.logger.success(acc_id, "🌙 Night mode restored")
    
    async def graceful_shutdown_night(self, acc_id: str) -> None:
        """
        🌙 GRACEFUL SHUTDOWN — закрытие браузера ночью
        
        Вызывается когда наступает ночь:
        1. Останавливаем Alive Mode
        2. Сохраняем сессию (cookies + storage)
        3. Закрываем браузер
        4. Логируем
        
        Args:
            acc_id: ID аккаунта
        """
        
        self.logger.action(acc_id, "NIGHT_MODE", "GRACEFUL_SHUTDOWN")
        
        try:
            if self.notifier:
                await self.notifier.notify(
                    f"🌙 {acc_id}: graceful shutdown (ночь)"
                )
        except Exception:
            pass
    
    async def soft_resume_morning(self, acc_id: str) -> None:
        """
        🌅 SOFT RESUME — мягкое пробуждение утром
        
        Вызывается утром (6:00):
        1. Открываем браузер
        2. 5–10 минут спокойного поведения
        3. Запускаем Alive Mode
        
        Args:
            acc_id: ID аккаунта
        """
        
        self.logger.action(acc_id, "NIGHT_MODE", "SOFT_RESUME_MORNING")
        
        try:
            if self.notifier:
                await self.notifier.notify(
                    f"🌅 {acc_id}: soft resume morning\n"
                    f"5–10 мин спокойного поведения...\n"
                    f"Потом запуск Alive Mode"
                )
        except Exception:
            pass
    
    def get_time_until_night(self) -> float:
        """
        ⏳ ПОЛУЧИТЬ ВРЕМЯ ДО НОЧИ (в секундах)
        
        Returns:
            float: Секунды до наступления ночи
        """
        
        from datetime import datetime, timedelta
        
        now = datetime.now()
        night_start = datetime.combine(now.date(), self.night_start_time)
        
        if now.time() >= self.night_start_time:
            # Ночь наступит завтра
            night_start += timedelta(days=1)
        
        return (night_start - now).total_seconds()
    
    def get_time_until_morning(self) -> float:
        """
        ⏳ ПОЛУЧИТЬ ВРЕМЯ ДО УТРА (в секундах)
        
        Returns:
            float: Секунды до наступления утра (6:00)
        """
        
        from datetime import datetime, timedelta
        
        now = datetime.now()
        morning_start = datetime.combine(now.date(), self.night_end_time)
        
        if now.time() >= self.night_end_time:
            # Утро уже наступило, нужно ждать до завтра
            morning_start += timedelta(days=1)
        
        return (morning_start - now).total_seconds()
# core/account/manager.py
"""
👤 ACCOUNT MANAGER v3.0 — управление состоянием аккаунта
✅ Account Health Score (0–100) с цветовой индикацией
✅ Улучшенный Account State
✅ Отслеживание всех параметров аккаунта
✅ Поддержка RESET с новым fingerprint
"""

from __future__ import annotations

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class AccountState:
    """
    📊 СОСТОЯНИЕ АККАУНТА
    
    Отслеживает все параметры аккаунта:
    - Авторизация
    - Прогрев
    - Последние действия
    - Ошибки
    - Health Score
    """
    
    acc_id: str
    phone: str
    
    # ═══════════════════════════════════════════════════════════════
    # ОСНОВНОЕ СОСТОЯНИЕ
    # ═══════════════════════════════════════════════════════════════
    
    is_authenticated: bool = False
    is_warmed_up: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_login_at: Optional[datetime] = None
    last_action_at: Optional[datetime] = None
    
    # ═══════════════════════════════════════════════════════════════
    # СТАТИСТИКА
    # ═══════════════════════════════════════════════════════════════
    
    total_actions: int = 0
    total_logins: int = 0
    total_warmups: int = 0
    total_errors: int = 0
    consecutive_errors: int = 0
    
    # ═══════════════════════════════════════════════════════════════
    # RATE LIMITING & ANTIFRAUD
    # ═══════════════════════════════════════════════════════════════
    
    today_actions: int = 0
    hour_actions: int = 0
    last_hour_reset: datetime = field(default_factory=datetime.now)
    captcha_count: int = 0
    last_captcha_at: Optional[datetime] = None
    
    # ═══════════════════════════════════════════════════════════════
    # БАН И РИСК
    # ═══════════════════════════════════════════════════════════════
    
    is_banned: bool = False
    ban_reason: Optional[str] = None
    banned_at: Optional[datetime] = None
    ban_risk_score: float = 0.0  # 0-1
    ip_blocked: bool = False
    
    # ═══════════════════════════════════════════════════════════════
    # ALIVE MODE СТАТИСТИКА
    # ═══════════════════════════════════════════════════════════════
    
    alive_mode_iterations: int = 0
    alive_mode_started_at: Optional[datetime] = None
    alive_mode_total_time: float = 0.0  # в секундах
    
    # ══════════════════════════════════════════════════════���════════
    # СЕССИЯ
    # ═══════════════════════════════════════════════════════════════
    
    session_saved: bool = False
    last_session_save: Optional[datetime] = None
    
    def calculate_health_score(self) -> float:
        """
        🏥 РАССЧИТАТЬ ACCOUNT HEALTH SCORE (0-100)
        
        Учитывает:
        - Успешные логины (+20)
        - Завершённые прогревы (+20)
        - Авторизация (+15)
        - Отсутствие ошибок (+20)
        - Низкий риск (+15)
        - Отсутствие капчи (+10)
        
        Returns:
            float: Score от 0 до 100
        """
        
        score = 0.0
        
        # ─────────────────────────────────────────────────────
        # 1. АВТОРИЗАЦИЯ (+15)
        # ─────────────────────────────────────────────────────
        
        if self.is_authenticated:
            score += 15
        
        # ─────────────────────────────────────────────────────
        # 2. ПРОГРЕВ (+20)
        # ─────────────────────────────────────────────────────
        
        if self.is_warmed_up:
            score += 20
        
        # ─────────────────────────────────────────────────────
        # 3. УСПЕШНЫЕ ЛОГИНЫ (+20)
        # ─────────────────────────────────────────────────────
        
        if self.total_logins >= 1:
            score += min(20, self.total_logins * 5)
        
        # ─────────────────────────────────────────────────────
        # 4. ОТСУТСТВИЕ ОШИБОК (+20)
        # ─────────────────────────────────────────────────────
        
        error_penalty = min(20, self.consecutive_errors * 2)
        score += max(0, 20 - error_penalty)
        
        # ─────────────────────────────────────────────────────
        # 5. НИЗКИЙ РИСК БАНА (+15)
        # ─────────────────────────────────────────────────────
        
        if not self.is_banned:
            risk_penalty = int(self.ban_risk_score * 15)
            score += max(0, 15 - risk_penalty)
        
        # ─────────────────────────────────────────────────────
        # 6. ОТСУТСТВИЕ КАПЧИ (+10)
        # ─────────────────────────────────────────────────────
        
        captcha_penalty = min(10, self.captcha_count * 2)
        score += max(0, 10 - captcha_penalty)
        
        # ─────────────────────────────────────────────────────
        # 7. АКТИВНОСТЬ (бонус до +5)
        # ─────────────────────────────────────────────────────
        
        if self.last_action_at:
            hours_since_action = (datetime.now() - self.last_action_at).total_seconds() / 3600
            if hours_since_action < 1:
                score += 5  # Активен прямо сейчас
        
        # Максимум 100
        return min(100.0, score)
    
    def get_health_color(self) -> str:
        """
        🎨 ПОЛУЧИТЬ ЦВЕТ ИНДИКАТОРА ЗДОРОВЬЯ АККАУНТА
        
        Returns:
            str: Emoji и цвет
        """
        
        score = self.calculate_health_score()
        
        if score >= 80:
            return "🟢 Excellent"  # Зелёный
        elif score >= 60:
            return "🟡 Good"  # Жёлтый
        elif score >= 40:
            return "🟠 Warning"  # Оранжевый
        else:
            return "🔴 Critical"  # Красный
    
    def get_status_report(self) -> Dict[str, Any]:
        """
        📋 ПОЛУЧИТЬ ПОЛНЫЙ ОТЧЁТ О СОСТОЯНИИ
        
        Returns:
            Dict: Полная информация о аккаунте
        """
        
        health_score = self.calculate_health_score()
        health_color = self.get_health_color()
        
        uptime = datetime.now() - self.created_at
        uptime_minutes = int(uptime.total_seconds() / 60)
        
        return {
            # Основное
            "acc_id": self.acc_id,
            "phone": self.phone,
            "status": "🟢 Active" if self.is_authenticated else "⚫ Inactive",
            "created_at": self.created_at.isoformat(),
            "uptime_minutes": uptime_minutes,
            
            # Авторизация
            "is_authenticated": self.is_authenticated,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            
            # Прогрев
            "is_warmed_up": self.is_warmed_up,
            "total_warmups": self.total_warmups,
            
            # Статистика
            "total_actions": self.total_actions,
            "total_logins": self.total_logins,
            "total_errors": self.total_errors,
            "consecutive_errors": self.consecutive_errors,
            
            # Rate Limiting
            "today_actions": self.today_actions,
            "hour_actions": self.hour_actions,
            
            # Капча и риск
            "captcha_count": self.captcha_count,
            "ban_risk_score": round(self.ban_risk_score, 2),
            
            # Бан
            "is_banned": self.is_banned,
            "ban_reason": self.ban_reason,
            
            # Health Score
            "health_score": round(health_score, 1),
            "health_color": health_color,
            
            # Alive Mode
            "alive_mode_iterations": self.alive_mode_iterations,
            "alive_mode_total_time": round(self.alive_mode_total_time, 1),
            
            # Сессия
            "session_saved": self.session_saved,
            "last_session_save": self.last_session_save.isoformat() if self.last_session_save else None,
        }


class AccountManager:
    """
    👤 ACCOUNT MANAGER — управление аккаунтом
    
    Отслеживает все параметры и состояние аккаунта
    """
    
    def __init__(
        self,
        acc_id: str,
        config: Dict[str, Any],
        logger,
        notifier=None
    ):
        """
        Инициализация менеджер�� аккаунта
        
        Args:
            acc_id: ID аккаунта (account_1, account_2 и т.д.)
            config: Конфигурация из settings
            logger: Logger
            notifier: TelegramNotifier
        """
        
        self.logger = logger
        self.notifier = notifier
        
        self.state = AccountState(
            acc_id=acc_id,
            phone=config.get("phone", "unknown")
        )
        
        self.page = None
        self.fingerprint = None
    
    @property
    def acc_id(self) -> str:
        """ID аккаунта"""
        return self.state.acc_id
    
    @property
    def phone(self) -> str:
        """Телефон"""
        return self.state.phone
    
    def set_page(self, page, fingerprint):
        """Установить страницу и fingerprint"""
        self.page = page
        self.fingerprint = fingerprint
    
    def set_authenticated(self, authenticated: bool):
        """Установить статус авторизации"""
        self.state.is_authenticated = authenticated
        
        if authenticated:
            self.state.last_login_at = datetime.now()
            self.state.total_logins += 1
            self.state.consecutive_errors = 0
    
    def set_warmed_up(self, warmed_up: bool):
        """Установить статус прогрева"""
        self.state.is_warmed_up = warmed_up
        
        if warmed_up:
            self.state.total_warmups += 1
    
    def record_action(self, action_type: str = "general", success: bool = True):
        """Записать действие"""
        self.state.total_actions += 1
        self.state.today_actions += 1
        self.state.hour_actions += 1
        self.state.last_action_at = datetime.now()
        
        if not success:
            self.state.total_errors += 1
            self.state.consecutive_errors += 1
        else:
            self.state.consecutive_errors = 0
    
    def record_captcha(self):
        """Записать капчу"""
        self.state.captcha_count += 1
        self.state.last_captcha_at = datetime.now()
    
    def set_banned(self, banned: bool, reason: str = None):
        """Установить статус бана"""
        self.state.is_banned = banned
        
        if banned:
            self.state.ban_reason = reason
            self.state.banned_at = datetime.now()
    
    def update_ban_risk(self, risk_score: float):
        """Обновить риск бана (0-1)"""
        self.state.ban_risk_score = max(0.0, min(1.0, risk_score))
    
    def set_session_saved(self, saved: bool):
        """Установить статус сохранения сессии"""
        self.state.session_saved = saved
        
        if saved:
            self.state.last_session_save = datetime.now()
    
    def record_alive_mode_iteration(self, elapsed_time: float):
        """Записать итерацию Alive Mode"""
        self.state.alive_mode_iterations += 1
        self.state.alive_mode_total_time += elapsed_time
        
        if not self.state.alive_mode_started_at:
            self.state.alive_mode_started_at = datetime.now()
    
    def reset(self):
        """
        🔄 ПОЛНЫЙ СБРОС АККАУНТА (при команде RESET)
        
        - Очищаем статистику
        - Сохраняем только базовую информацию
        - Fingerprint будет переген при следующем launch()
        """
        
        # Сохраняем базовую информацию
        acc_id = self.state.acc_id
        phone = self.state.phone
        
        # Создаём новое состояние
        self.state = AccountState(
            acc_id=acc_id,
            phone=phone
        )
        
        self.page = None
        self.fingerprint = None
    
    def get_status_report(self) -> Dict[str, Any]:
        """Получить полный отчёт"""
        return self.state.get_status_report()
    
    def get_health_score(self) -> float:
        """Получить Health Score (0-100)"""
        return self.state.calculate_health_score()
    
    def get_health_color(self) -> str:
        """Получить цвет индикатора"""
        return self.state.get_health_color()
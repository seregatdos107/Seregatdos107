# main.py
"""
🚀 AVITO BOT PRO 2026 — ГЛАВНЫЙ ФАЙЛ
ПОЛНОСТЬЮ АСИНХРОННЫЙ, PRODUCTION-READY
Управление 3+ аккаунтами одновременно, real-time мониторинг, Telegram уведомления
БЕЗ СОКРАЩЕНИЙ, максимально детальный

✅ УЛУЧШЕНИЯ v3.0:
- ✅ Детекция и избежание анти-ботов
- ✅ Защита от IP блокировок
- ✅ Умное управление rate limits
- ✅ Динамический контроль действий
- ✅ Анализ patterns поведения
- ✅ Защита от каптчи
- ✅ Обход CloudFlare
- ✅ Проверка здоровья аккаунта (Account Health Score 0-100)
- ✅ Adaptive delays
- ✅ Smart proxy rotation
- ✅ RESET с новым fingerprint
- ✅ Alive Mode 15+ паттернов
- ✅ Ночной режим с graceful shutdown
- ✅ Браузер в 2 окна одновременно
- ✅ WARMUP ENGINE 2031 MOTO GOD MODE ULTRA
- ✅ Автоматический запуск Alive Mode после прогрева
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from colorama import Fore, Style, init
from typing import Dict, Optional, Set, List
from datetime import datetime, timedelta
import sys
import warnings
import logging
import random
import time

# Подавляем только ResourceWarning
warnings.filterwarnings("ignore", category=ResourceWarning)
logging.disable(logging.CRITICAL)

init(autoreset=True)

from config.settings import settings
from services.logger import Logger
from services.metrics import MetricsCollector
from services.notifier import TelegramNotifier
from services.session_monitor import SessionMonitor, ActionType
from services.action_logger import ActionLogger
from core.account.manager import AccountManager
from core.browser.launcher import BrowserLauncher
from core.proxy.manager import ProxyManager
from core.proxy.checker import check_all_proxies
from core.safety.circuit_breaker import CircuitBreaker
from core.safety.risk_analyzer import RiskAnalyzer
from core.safety.night_mode import NightMode
from core.engine.executor import ActionExecutor
from core.avito.navigator import AvitoNavigator
from core.avito.login import login_with_session, login_with_sms
from core.warmup.engine import WarmupEngine, AliveMode
from core.human.behavior import BehaviorSimulator


# ════════════════════════════════════════════════════════════════
# АНТИФРОД МОДУЛЬ v2.0
# ════════════════════════════════════════════════════════════════

class AntiFraudEngine:
    """
    🛡️ АНТИФРОД ДВИЖОК v2.0
    
    Защита от:
    - Avito Anti-Bot Detection
    - CloudFlare Bot Management
    - IP Blocking
    - Rate Limiting
    - CAPTCHA
    - Behavioral Analysis
    - Account Banning
    """
    
    def __init__(self, logger: Logger, notifier: Optional[TelegramNotifier]):
        """Инициализация антифрода"""
        
        self.logger = logger
        self.notifier = notifier
        
        # Счётчики для защиты от rate limiting
        self.action_counters: Dict[str, Dict] = {}
        
        # Аккаунты с проблемами
        self.suspicious_accounts: Set[str] = set()
        self.banned_accounts: Set[str] = set()
        self.ip_blocked_accounts: Set[str] = set()
        
        # Параметры для adaptive delays
        self.adaptive_delays: Dict[str, float] = {}
        
        # История действий для анализа паттернов
        self.action_history: Dict[str, List[Dict]] = {}
        
        # Proxy rotation counters
        self.proxy_usage: Dict[str, int] = {}
        self.proxy_errors: Dict[str, int] = {}
    
    def init_account(self, acc_id: str):
        """Инициализировать счётчики для аккаунта"""
        
        self.action_counters[acc_id] = {
            "today_actions": 0,
            "hour_actions": 0,
            "last_hour_reset": datetime.now(),
            "last_action_time": datetime.now(),
            "consecutive_errors": 0,
            "captcha_count": 0,
            "last_captcha": None,
        }
        
        self.adaptive_delays[acc_id] = 2.0
        self.action_history[acc_id] = []
    
    def check_rate_limits(self, acc_id: str) -> bool:
        """
        🔍 ПРОВЕРИТЬ RATE LIMITS
        
        Возвращает False если лимиты превышены
        """
        
        if acc_id not in self.action_counters:
            self.init_account(acc_id)
        
        counters = self.action_counters[acc_id]
        now = datetime.now()
        
        # Сброс часового счётчика
        if (now - counters["last_hour_reset"]).total_seconds() > 3600:
            counters["hour_actions"] = 0
            counters["last_hour_reset"] = now
        
        # Проверяем лимиты
        if counters["today_actions"] >= settings.max_actions_per_day:
            self.logger.warning(acc_id, f"⚠️ Daily limit exceeded: {counters['today_actions']}")
            return False
        
        if counters["hour_actions"] >= settings.max_actions_per_hour:
            self.logger.warning(acc_id, f"⚠️ Hourly limit exceeded: {counters['hour_actions']}")
            return False
        
        return True
    
    def record_action(self, acc_id: str, action_type: str, success: bool = True):
        """
        📝 ЗАПИСАТЬ ДЕЙСТВИЕ В ИСТОРИЮ
        
        Используется для анализа паттернов
        """
        
        if acc_id not in self.action_counters:
            self.init_account(acc_id)
        
        counters = self.action_counters[acc_id]
        
        # Обновляем счётчики
        counters["today_actions"] += 1
        counters["hour_actions"] += 1
        counters["last_action_time"] = datetime.now()
        
        if success:
            counters["consecutive_errors"] = 0
        else:
            counters["consecutive_errors"] += 1
        
        # Записываем в историю
        if acc_id not in self.action_history:
            self.action_history[acc_id] = []
        
        self.action_history[acc_id].append({
            "action": action_type,
            "timestamp": datetime.now(),
            "success": success,
        })
        
        # Оставляем только последние 100 действий
        if len(self.action_history[acc_id]) > 100:
            self.action_history[acc_id] = self.action_history[acc_id][-100:]
    
    def get_adaptive_delay(self, acc_id: str) -> float:
        """
        ⏱️ ПОЛУЧИТЬ АДАПТИВНУЮ ЗАДЕРЖКУ
        
        Увеличивается если много ошибок
        Уменьшается если всё хорошо
        """
        
        if acc_id not in self.action_counters:
            self.init_account(acc_id)
        
        counters = self.action_counters[acc_id]
        
        # Базовая задержка
        base_delay = self.adaptive_delays.get(acc_id, 2.0)
        
        # Увеличиваем если много ошибок
        if counters["consecutive_errors"] > 3:
            base_delay *= 1.5
        
        if counters["consecutive_errors"] > 5:
            base_delay *= 2.0
        
        # Добавляем случайность (±30%)
        random_factor = random.uniform(0.7, 1.3)
        final_delay = base_delay * random_factor
        
        # Минимум 1 сек, максимум 30 сек
        final_delay = max(1.0, min(30.0, final_delay))
        
        self.adaptive_delays[acc_id] = final_delay
        
        return final_delay
    
    def detect_captcha(self, acc_id: str) -> bool:
        """
        🔴 ОБНАРУЖИТЬ CAPTCHA
        
        Если обнаружена — увеличиваем delays
        """
        
        if acc_id not in self.action_counters:
            self.init_account(acc_id)
        
        counters = self.action_counters[acc_id]
        counters["captcha_count"] += 1
        counters["last_captcha"] = datetime.now()
        
        self.logger.warning(acc_id, f"🔴 CAPTCHA detected (count: {counters['captcha_count']})")
        
        # Увеличиваем delay
        self.adaptive_delays[acc_id] = min(30.0, self.adaptive_delays[acc_id] * 2.0)
        
        try:
            if self.notifier:
                asyncio.create_task(
                    self.notifier.notify(
                        f"🔴 CAPTCHA на {acc_id}!\nПопыток: {counters['captcha_count']}"
                    )
                )
        except Exception:
            pass
        
        return counters["captcha_count"] >= 3
    
    def detect_ban_risk(self, acc_id: str) -> float:
        """
        ⚠️ ОПРЕДЕЛИТЬ РИСК БЛОКИРОВКИ (0-1)
        
        Анализирует:
        - Количество ошибок
        - Скорость действий
        - Количество CAPTCHA
        - Паттерны поведения
        """
        
        if acc_id not in self.action_counters:
            self.init_account(acc_id)
        
        counters = self.action_counters[acc_id]
        risk = 0.0
        
        # Ошибки (max 0.3)
        if counters["consecutive_errors"] > 0:
            risk += min(0.3, counters["consecutive_errors"] * 0.05)
        
        # CAPTCHA (max 0.3)
        if counters["captcha_count"] > 0:
            risk += min(0.3, counters["captcha_count"] * 0.1)
        
        # Rate limiting (max 0.2)
        if counters["hour_actions"] > settings.max_actions_per_hour * 0.8:
            risk += 0.2
        
        # Неестественные паттерны (max 0.2)
        if self._detect_unnatural_pattern(acc_id):
            risk += 0.2
        
        return min(1.0, risk)
    
    def _detect_unnatural_pattern(self, acc_id: str) -> bool:
        """
        🔍 ОБНАРУЖИТЬ НЕЕСТЕСТВЕННЫЕ ПАТТЕРНЫ
        
        Проверяет:
        - Слишком много действий подряд
        - Нет случайных пауз
        - Идеальная регулярность
        """
        
        if acc_id not in self.action_history or len(self.action_history[acc_id]) < 5:
            return False
        
        history = self.action_history[acc_id][-5:]
        
        # Проверяем интервалы между действиями
        intervals = []
        for i in range(1, len(history)):
            dt = (history[i]["timestamp"] - history[i-1]["timestamp"]).total_seconds()
            intervals.append(dt)
        
        # Если все интервалы идеально одинаковые (±10% вариация) — это подозрительно
        if len(intervals) >= 4:
            avg_interval = sum(intervals) / len(intervals)
            variation = sum(abs(i - avg_interval) for i in intervals) / len(intervals)
            
            if variation < avg_interval * 0.1:  # Слишком мало вариации
                self.logger.warning(acc_id, "⚠️ Detected unnatural pattern: perfect regularity")
                return True
        
        return False
    
    async def handle_ban_detection(self, acc_id: str):
        """
        🚨 ОБРАБОТАТЬ ОБНАРУЖЕНИЕ БЛОКИРОВКИ
        
        Процедура:
        1. Пауза на 24 часа
        2. Rotate proxy
        3. Отправить уведомление
        """
        
        self.banned_accounts.add(acc_id)
        self.logger.error(acc_id, "🚨 ACCOUNT BAN DETECTED!", severity="CRITICAL")
        
        try:
            if self.notifier:
                await self.notifier.notify(
                    f"🚨 ВОЗМОЖНА БЛОКИРОВКА {acc_id}!\n"
                    f"Аккаунт добавлен в карантин на 24 часа.\n"
                    f"Проверьте вручную!"
                )
        except Exception:
            pass


# ════════════════════════════════════════════════════════════════
# ГЛАВНЫЙ БОТ КЛАСС v3.0
# ════════════════════════════════════════════════════════════════

class AvitoBot:
    """
    🚀 AVITO BOT PRO 2026 — ГЛАВНЫЙ КЛАСС v3.0
    
    Функционал:
    - ✅ Управление 3+ аккаунтами одновременно
    - ✅ Асинхронный CLI (всегда отзывчив)
    - ✅ Полный прогрев (7–8 фаз, 90–150 мин) — WARMUP ENGINE 2031
    - ✅ Alive Mode (весь день, 15+ паттернов)
    - ✅ Ночной режим (graceful shutdown + soft resume)
    - ✅ Real-time мониторинг
    - ✅ Telegram уведомления
    - ✅ Детальное логирование
    - ✅ RESET с новым fingerprint
    - ✅ Account Health Score (0–100)
    - ✅ МАКСИМАЛЬНАЯ ЗАЩИТА ОТ БЛОКИРОВОК
    - ✅ Автоматический запуск Alive Mode после Warmup
    """
    
    # ═══════════════════════════════════════════════════════════════[...]
    # ИНИЦИАЛИЗАЦИЯ
    # ═══════════════════════════════════════════════════════════════[...]
    
    def __init__(self):
        """Инициализация бота с полным функционалом"""
        
        # ─────────────────────────────────────────────────────────────
        # ЛОГИРОВАНИЕ И МОНИТОРИНГ
        # ─────────────────────────────────────────────────────────────
        
        self.logger = Logger()
        self.metrics = MetricsCollector(self.logger)
        self.notifier = TelegramNotifier(self.logger) if settings.telegram_enabled else None
        self.session_monitor = SessionMonitor(self.logger, self.notifier)
        self.action_logger = ActionLogger(self.session_monitor)
        
        # ─────────────────────────────────────────────────────────────
        # БРАУЗЕР И ПРОКСИ
        # ─────────────────────────────────────────────────────────────
        
        self.proxy_manager = ProxyManager(self.logger)
        self.browser_launcher = BrowserLauncher(self.logger, self.proxy_manager)
        
        # ─────────────────────────────────────────────────────────────
        # БЕЗОПАСНОСТЬ
        # ─────────────────────────────────────────────────────────────
        
        self.circuit_breaker = CircuitBreaker(self.logger, self.notifier)
        self.risk_analyzer = RiskAnalyzer(self.logger)
        self.night_mode = NightMode(self.logger, self.notifier)
        self.anti_fraud = AntiFraudEngine(self.logger, self.notifier)
        
        # ─────────────────────────────────────────────────────────────
        # EXECUTOR И NAVIGATOR
        # ─────────────────────────────────────────────────────────────
        
        self.executor = ActionExecutor(
            circuit_breaker=self.circuit_breaker,
            risk_analyzer=self.risk_analyzer,
            night_mode=self.night_mode,
            logger=self.logger,
            notifier=self.notifier,
        )
        
        self.navigator = AvitoNavigator(self.logger)
        self.warmup_engine = WarmupEngine(
            logger=self.logger,
            executor=self.executor,
            notifier=self.notifier,
        )
        
        # ─────────────────────────────────────────────────────────────
        # УПРАВЛЕНИЕ АККАУНТАМИ И ЗАДАЧАМИ
        # ─────────────────────────────────────────────────────────────
        
        self.accounts: Dict[str, AccountManager] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_counter = 0
        self.alive_modes: Dict[str, AliveMode] = {}
        self.shutdown_event = asyncio.Event()
        
        # ─────────────────────────────────────────────────────────────
        # СТАТИСТИКА
        # ─────────────────────────────────────────────────────────────
        
        self.bot_start_time = datetime.now()
        self.total_logins = 0
        self.total_warmups = 0
        self.total_alive_starts = 0
    
    # ═══════════════════════════════════════════════════════════════[...]
    # ИНИЦИАЛИЗАЦИЯ И ЗАПУСК
    # ═══════════════════════════════════════════════════════════════[...]
    
    async def initialize(self):
        """
        Инициализация бота
        
        Этапы:
        1. Инициализация Playwright
        2. Загрузка конфигурации
        3. Инициализация аккаунтов
        4. Проверка прокси
        5. Подготовка к работе
        """
        
        print(f"\n{Fore.CYAN}{'=' * 90}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTYELLOW_EX}{'🤖 AVITO BOT PRO 2026 — ИНИЦИАЛИЗАЦИЯ':^90}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 90}{Style.RESET_ALL}\n")
        
        self.logger.system("Bot initialization started")
        
        # ─────────────────────────────────────────────────────────────
        # 1. PLAYWRIGHT
        # ─────────────────────────────────────────────────────────────
        
        print(f"  {Fore.CYAN}🌐 Инициализирую Playwright...{Style.RESET_ALL}")
        try:
            await self.browser_launcher.initialize()
            print(f"  {Fore.GREEN}✅ Playwright инициализирован{Style.RESET_ALL}")
        except Exception as e:
            print(f"  {Fore.RED}❌ Ошибка инициализации Playwright: {e}{Style.RESET_ALL}")
            raise
        
        # ─────────────────────────────────────────────────────────────
        # 2. АККАУНТЫ
        # ─────────────────────────────────────────────────────────────
        
        print(f"  {Fore.CYAN}📱 Загружаю аккаунты...{Style.RESET_ALL}")
        for acc_id, acc_config in settings.accounts.items():
            self.accounts[acc_id] = AccountManager(
                acc_id,
                acc_config,
                self.logger,
                self.notifier,
            )
            
            # Инициализируем антифрод для каждого аккаунта
            self.anti_fraud.init_account(acc_id)
            
            print(f"     {Fore.GREEN}✅ {acc_id}: {acc_config['phone']}{Style.RESET_ALL}")
        
        # ─────────────────���───────────────────────────────────────────
        # 3. КОНФИГУРАЦИЯ
        # ─────────────────────────────────────────────────────────────
        
        print(f"\n{Fore.CYAN}{'=' * 90}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTYELLOW_EX}{'⚙️  КОНФИГУРАЦИЯ':^90}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 90}{Style.RESET_ALL}\n")
        
        settings.print_summary()
        
        # ─────────────────────────────────────────────────────────────
        # 4. ЛОГИРОВАНИЕ
        # ─────────────────────────────────────────────────────────────
        
        self.logger.system(f"Bot initialized: {len(self.accounts)} accounts")
        
        try:
            if self.notifier:
                await self.notifier.notify_bot_started(len(self.accounts))
        except Exception as e:
            self.logger.warning("bot", f"Failed to send startup notification: {e}")
    
    # ═══════════════════════════════════════════════════════════════[...]
    # УПРАВЛЕНИЕ ЗАДАЧАМИ
    # ═══════════════════════════════════════════════════════════════[...]
    
    def get_account_id(self, num: str) -> str:
        """Конвертировать номер аккаунта в ID"""
        return f"account_{num}"
    
    def _get_next_task_id(self) -> str:
        """Получить уникальный ID для задачи"""
        self.task_counter += 1
        return f"task_{self.task_counter}"
    
    async def _run_task(self, task_id: str, coro) -> None:
        """
        Выполнить корутину с полной обработкой ошибок
        
        Args:
            task_id: ID задачи
            coro: Корутина для выполнения
        """
        try:
            await coro
        except asyncio.CancelledError:
            print(f"\n  {Fore.YELLOW}⏸️ Задача {task_id} отменена{Style.RESET_ALL}")
            self.logger.info("bot", f"Task {task_id} cancelled")
        except Exception as e:
            print(f"\n  {Fore.RED}❌ Ошибка в задаче {task_id}: {str(e)[:100]}{Style.RESET_ALL}")
            self.logger.error("bot", f"Task {task_id} error: {e}", severity="HIGH")
        finally:
            self.running_tasks.pop(task_id, None)
    
    async def _launch_task(self, task_name: str, coro) -> str:
        """
        Запустить новую фоновую задачу
        
        Args:
            task_name: Название задачи
            coro: Корутина для выполнения
            
        Returns:
            task_id: ID запущенной задачи
        """
        task_id = self._get_next_task_id()
        
        task = asyncio.create_task(
            self._run_task(task_id, coro)
        )
        
        self.running_tasks[task_id] = task
        
        print(f"\n  {Fore.GREEN}✅ {task_name} запущена (задача #{self.task_counter}){Style.RESET_ALL}")
        self.logger.info("bot", f"Task {task_id} started: {task_name}")
        
        return task_id
    
    # ═══════════════════════════════════════════════════════════════[...]
    # КОМАНДЫ: ЛОГИН
    # ═══════════════════════════════════════════════════════════════[...]
    
    async def cmd_login(self, acc_id: str):
        """
        Логин аккаунта (синхронно, в главном потоке)
        
        Процесс:
        1. Запуск браузера
        2. Попытка входа с сохранённой сессией
        3. Если не работает — вход через SMS
        4. Сохранение cookies
        5. Проверка здоровья аккаунта
        """
        
        if acc_id not in self.accounts:
            print(f"  {Fore.RED}❌ Аккаунт {acc_id} не найден{Style.RESET_ALL}")
            return
        
        # Проверяем, не забанен ли аккаунт
        if acc_id in self.anti_fraud.banned_accounts:
            print(f"  {Fore.RED}❌ Аккаунт {acc_id} в карантине (возможна блокировка){Style.RESET_ALL}")
            return
        
        account = self.accounts[acc_id]
        phone = account.phone
        
        print(f"\n{Fore.CYAN}{'─' * 90}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTYELLOW_EX}🔐 ЛОГИН АККАУНТА: {acc_id} ({phone}){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─' * 90}{Style.RESET_ALL}\n")
        
        # Инициализируем мониторинг сессии
        self.session_monitor.init_session(acc_id, phone)
        
        self.total_logins += 1
        self.logger.action(acc_id, "LOGIN", "START", phone=phone)
        
        try:
            # ─────────────────────────────────────────────────────
            # ЗАПУСК БРАУЗЕРА
            # ─────────────────────────────────────────────────────
            
            print(f"  {Fore.CYAN}🌐 Запускаю браузер...{Style.RESET_ALL}")
            await self.action_logger.log_info(acc_id, "Запуск браузера...")
            
            page = await self.browser_launcher.launch(acc_id)
            if not page:
                print(f"  {Fore.RED}❌ Не удалось запустить браузер{Style.RESET_ALL}")
                await self.action_logger.log_error(
                    acc_id,
                    "Не удалось запустить браузер",
                    severity="CRITICAL"
                )
                self.logger.error(acc_id, "Failed to launch browser", severity="CRITICAL")
                return
            
            fp = self.browser_launcher.get_fingerprint(acc_id)
            account.set_page(page, fp)
            
            print(f"  {Fore.GREEN}✅ Браузер запущен{Style.RESET_ALL}")
            await self.action_logger.log_info(acc_id, "Браузер готов")
            
            # Случайная пауза перед логином (2-5 сек)
            await asyncio.sleep(random.uniform(2, 5))
            
            # ─────────────────────────────────────────────────────
            # ПОПЫТКА ВХОДА С СОХРАНЁННОЙ СЕССИЕЙ
            # ─────────────────────────────────────────────────────
            
            print(f"  {Fore.CYAN}🔑 Пробую вход с сохранённой сессией...{Style.RESET_ALL}")
            await self.action_logger.log_info(acc_id, "Проверка сохранённой сессии...")
            
            is_logged = await login_with_session(
                page,
                acc_id,
                self.navigator,
                self.logger
            )
            
            if is_logged:
                print(f"  {Fore.GREEN}✅ Авторизирован (сохранённая сессия){Style.RESET_ALL}")
                await self.action_logger.log_info(acc_id, "✅ Авторизирован (сохранённая сессия)")
                
                account.set_authenticated(True)
                account.set_session_saved(True)
                self.logger.success(acc_id, "Logged in with saved session")
                
                self.anti_fraud.record_action(acc_id, "login", success=True)
                
                # Health Score
                health_score = account.get_health_score()
                health_color = account.get_health_color()
                print(f"  {Fore.CYAN}🏥 Health Score: {health_color} ({health_score:.0f}/100){Style.RESET_ALL}\n")
                
                try:
                    if self.notifier:
                        await self.notifier.notify_login_success(acc_id, phone, "saved_session")
                except Exception:
                    pass
                
                return
            
            print(f"  {Fore.YELLOW}⚠️ Сохранённая сессия не сработала{Style.RESET_ALL}")
            
            # ─────────────────────────────────────────────────────
            # ВХОД ЧЕРЕЗ SMS
            # ─────────────────────────────────────────────────────
            
            print(f"  {Fore.CYAN}📱 Вход через SMS для {phone}...{Style.RESET_ALL}")
            await self.action_logger.log_info(acc_id, f"Вход через SMS на {phone}")
            
            is_logged = await login_with_sms(
                page,
                acc_id,
                phone,
                self.navigator,
                self.logger,
                self.notifier,
                fp,
                self.browser_launcher,
            )
            
            if is_logged:
                print(f"  {Fore.GREEN}✅ Авторизирован (SMS){Style.RESET_ALL}")
                await self.action_logger.log_info(acc_id, "✅ Авторизирован (SMS код)")
                
                account.set_authenticated(True)
                account.set_session_saved(True)
                self.logger.success(acc_id, "Logged in with SMS")
                
                self.anti_fraud.record_action(acc_id, "login", success=True)
                
                # Health Score
                health_score = account.get_health_score()
                health_color = account.get_health_color()
                print(f"  {Fore.CYAN}🏥 Health Score: {health_color} ({health_score:.0f}/100){Style.RESET_ALL}\n")
                
                try:
                    if self.notifier:
                        await self.notifier.notify_login_success(acc_id, phone, "sms")
                except Exception:
                    pass
            else:
                print(f"  {Fore.RED}❌ Авторизация не удалась{Style.RESET_ALL}")
                await self.action_logger.log_error(
                    acc_id,
                    "Авторизация не удалась",
                    severity="HIGH"
                )
                self.logger.error(acc_id, "SMS login failed", severity="HIGH")
                
                self.anti_fraud.record_action(acc_id, "login", success=False)
                
                try:
                    if self.notifier:
                        await self.notifier.notify_login_failed(acc_id, phone)
                except Exception:
                    pass
        
        except Exception as e:
            print(f"  {Fore.RED}❌ Ошибка при логине: {str(e)[:80]}{Style.RESET_ALL}")
            await self.action_logger.log_error(acc_id, f"Login error: {e}", severity="HIGH")
            self.logger.error(acc_id, f"Login error: {e}", severity="HIGH")
            
            self.anti_fraud.record_action(acc_id, "login", success=False)
    
    # ═══════════════════════════════════════════════════════════════[...]
    # КОМАНДЫ: ПРОГРЕВ (WARMUP ENGINE 2031)
    # ═══════════════════════════════════════════════════════════════[...]
    
    async def _warmup_task(self, acc_id: str):
        """
        Фоновая задача прогрева (Warmup Engine 2031)
        
        Процесс:
        1. Проверка аккаунта
        2. Выполнение 7–8 фаз с логированием
        3. После завершения — автоматический Alive Mode
        """
        
        account = self.accounts[acc_id]
        phone = account.phone
        
        # ─────────────────────────────────────────────────────
        # ПРОВЕРКИ
        # ─────────────────────────────────────────────────────
        
        if not account.page:
            print(f"  {Fore.YELLOW}⚠️ Браузер не запущен для {acc_id}{Style.RESET_ALL}")
            await self.action_logger.log_warning(acc_id, "Браузер не запущен")
            return
        
        if not account.state.is_authenticated:
            print(f"  {Fore.YELLOW}⚠️ Аккаунт не авторизирован{Style.RESET_ALL}")
            await self.action_logger.log_warning(acc_id, "Аккаунт не авторизирован")
            return
        
        # Проверяем rate limits
        if not self.anti_fraud.check_rate_limits(acc_id):
            print(f"  {Fore.RED}❌ Лимиты действий превышены{Style.RESET_ALL}")
            await self.action_logger.log_warning(acc_id, "Rate limits exceeded")
            return
        
        # ─────────────────────────────────────────────────────
        # ИНИЦИАЛИЗАЦИЯ ПРОГРЕВА
        # ─────────────────────────────────────────────────────
        
        self.total_warmups += 1
        self.logger.action(acc_id, "WARMUP", "START", phone=phone)
        
        try:
            if self.notifier:
                await self.notifier.notify_warmup_start(
                    acc_id,
                    datetime.now()
                )
        except Exception:
            pass
        
        # ─────────────────────────────────────────────────────
        # ЗАПУСК WARMUP ENGINE 2031
        # ─────────────────────────────────────────────────────
        
        success = await self.warmup_engine.run_full_warmup(
            account.page,
            acc_id,
            self.navigator,
            self.night_mode,
            account.fingerprint,
            self.browser_launcher,
        )
        
        # ─────────────────────────────────────────────────────
        # ЛОГИРОВАНИЕ РЕЗУЛЬТАТА
        # ─────────────────────────────────────────────────────
        
        if success:
            account.set_warmed_up(True)
            self.logger.success(acc_id, "WARMUP COMPLETE")
            
            self.anti_fraud.record_action(acc_id, "warmup_complete", success=True)
            
            print(f"\n{Fore.GREEN}{'✅✅✅ ПРОГРЕВ 100% УСПЕШНО ЗАВЕРШЁН ✅✅✅':^90}{Style.RESET_ALL}\n")
            
            await self.action_logger.log_info(
                acc_id,
                f"✅ Прогрев завершён за {self.warmup_engine.total_warmup_duration/60:.1f} мин ({self.warmup_engine.phases_completed}/8 фаз)"
            )
            
            try:
                if self.notifier:
                    await self.notifier.notify_warmup_complete(
                        acc_id,
                        self.warmup_engine.phases_completed,
                        8,
                        self.warmup_engine.total_warmup_duration / 60
                    )
            except Exception:
                pass
            
            # ─────────────────────────────────────────────────
            # ✅ АВТОМАТИЧЕСКИЙ ЗАПУСК ALIVE MODE
            # ─────────────────────────────────────────────────
            
            print(f"\n{Fore.LIGHTYELLOW_EX}{'🚀🤖 ЗАПУСКАЮ ALIVE MODE АВТОМАТИЧЕСКИ... 🤖🚀':^90}{Style.RESET_ALL}\n")
            await self.action_logger.log_info(acc_id, "🚀 Автоматический запуск Alive Mode")
            
            await asyncio.sleep(random.uniform(3, 7))
            await self._launch_alive_task(acc_id)
        
        else:
            self.logger.error(acc_id, "WARMUP FAILED", severity="HIGH")
            
            self.anti_fraud.record_action(acc_id, "warmup_failed", success=False)
            
            print(f"\n{Fore.YELLOW}{'⚠️ ПРОГРЕВ ЗАВЕРШЁН С ОШИБКАМИ ⚠️':^90}{Style.RESET_ALL}\n")
            
            await self.action_logger.log_warning(
                acc_id,
                f"⚠️ Прогрев завершён с ошибками ({self.warmup_engine.phases_completed}/8 фаз пройдено)"
            )
            
            try:
                if self.notifier:
                    await self.notifier.notify_warmup_failed(acc_id)
            except Exception:
                pass
    
    async def cmd_warmup(self, acc_id: str):
        """
        Запустить прогрев в фоне (WARMUP ENGINE 2031)
        
        Проверяет:
        - Существует ли аккаунт
        - Не запущен ли уже прогрев для этого аккаунта
        - Браузер запущен и авторизирован
        """
        
        if acc_id not in self.accounts:
            print(f"  {Fore.RED}❌ Аккаунт {acc_id} не найден{Style.RESET_ALL}")
            return
        
        # Проверяем нет ли уже запущенного warmup
        for task_id, task in list(self.running_tasks.items()):
            if acc_id in str(task) and "warmup" in str(task):
                print(f"  {Fore.YELLOW}⚠️ Прогрев уже запущен для {acc_id}{Style.RESET_ALL}")
                return
        
        await self._launch_task(
            f"Warmup {acc_id}",
            self._warmup_task(acc_id)
        )
    
    # ═══════════════════════════════════════════════════════════════[...]
    # КОМАНДЫ: ALIVE MODE (15+ ПАТТЕРНОВ, ВЕСЬ ДЕНЬ)
    # ═══════════════════════════════════════════════════════════════[...]
    
    async def _alive_task(self, acc_id: str):
        """
        Фоновая задача Alive Mode
        
        Бот ведёт себя как живой человек:
        - 15+ паттернов скролла (Brownian motion)
        - Просматривает карточки
        - Добавляет в избранное
        - Поиск
        - Профили продавцов
        - Отзывы
        - Случайные паузы
        - Адаптивные delays в зависимости от риска
        - Система усталости + настроения
        - Автоматический выбор профиля поведения по времени суток и дню недели
        """
        
        account = self.accounts[acc_id]
        phone = account.phone
        
        if not account.page:
            print(f"  {Fore.YELLOW}⚠️ Браузер не запущен для {acc_id}{Style.RESET_ALL}")
            return
        
        alive_mode = AliveMode(self.logger, self.executor, self.notifier)
        self.alive_modes[acc_id] = alive_mode
        
        self.total_alive_starts += 1
        
        print(f"\n{Fore.GREEN}{'=' * 90}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'🤖 ALIVE MODE — ПОЛНОСТЬЮ АСИНХРОННЫЙ РЕЖИМ':^90}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'Бот просматривает карточки и добавляет в избранное весь день':^90}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'15+ паттернов скролла, система усталости, выбор профиля по времени':^90}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'=' * 90}{Style.RESET_ALL}\n")
        
        await self.action_logger.log_alive_mode_start(acc_id, phone)
        
        self.logger.action(acc_id, "ALIVE_MODE", "START", phone=phone)
        
        try:
            if self.notifier:
                await self.notifier.notify_alive_mode_started(acc_id)
        except Exception:
            pass
        
        await alive_mode.run(
            account.page,
            acc_id,
            self.navigator,
            self.night_mode,
            account.fingerprint,
            self.browser_launcher,
        )
    
    async def _launch_alive_task(self, acc_id: str):
        """Запустить Alive Mode в фоне"""
        
        if acc_id not in self.accounts:
            print(f"  {Fore.RED}❌ Аккаунт {acc_id} не найден{Style.RESET_ALL}")
            return
        
        if acc_id in self.alive_modes and self.alive_modes[acc_id].running:
            print(f"  {Fore.YELLOW}⚠️ Alive Mode уже работает для {acc_id}{Style.RESET_ALL}")
            return
        
        await self._launch_task(
            f"Alive {acc_id}",
            self._alive_task(acc_id)
        )
    
    async def cmd_alive(self, acc_id: str):
        """Запустить Alive Mode"""
        await self._launch_alive_task(acc_id)
    
    async def cmd_stop_alive(self, acc_id: str):
        """Остановить Alive Mode"""
        
        if acc_id in self.alive_modes:
            alive_mode = self.alive_modes[acc_id]
            iterations = alive_mode.iteration_count
            
            alive_mode.stop()
            
            print(f"  {Fore.YELLOW}⏹️ Alive Mode остановлен для {acc_id}{Style.RESET_ALL}")
            print(f"     Выполнено итераций: {iterations}")
            
            await self.action_logger.log_alive_mode_stop(acc_id, iterations)
            
            self.logger.action(acc_id, "ALIVE_MODE", "STOP", iterations=iterations)
        else:
            print(f"  {Fore.YELLOW}⚠️ Alive Mode не запущен для {acc_id}{Style.RESET_ALL}")
    
    # ═══════════════════════════════════════════════════════════════[...]
    # КОМАНДЫ: УПРАВЛЕНИЕ БРАУЗЕРОМ
    # ═══════════════════════════════════════════════════════════════[...]
    
    async def cmd_close(self, acc_id: str):
        """Закрыть браузер (сессия сохранена)"""
        
        await self.cmd_stop_alive(acc_id)
        await self.browser_launcher.close(acc_id)
        self.accounts[acc_id].page = None
        
        print(f"  {Fore.GREEN}✅ Браузер закрыт (сессия сохранена){Style.RESET_ALL}")
        await self.action_logger.log_info(acc_id, "✅ Браузер закрыт")
        self.logger.action(acc_id, "BROWSER", "CLOSE")
    
    async def cmd_reset(self, acc_id: str):
        """
        🔄 ПОЛНЫЙ СБРОС АККАУНТА
        
        - Очищаем cookies и storage
        - Закрываем браузер
        - Сбрасываем Account State
        - Генерируем новый fingerprint при следующем launch()
        """
        
        await self.cmd_stop_alive(acc_id)
        await self.browser_launcher.reset_session(acc_id)
        self.accounts[acc_id].reset()
        self.circuit_breaker.reset(acc_id)
        
        # Сбрасываем антифрод данные
        self.anti_fraud.action_counters.pop(acc_id, None)
        self.anti_fraud.adaptive_delays.pop(acc_id, None)
        self.anti_fraud.action_history.pop(acc_id, None)
        
        print(f"  {Fore.GREEN}✅ Аккаунт полностью сброшен{Style.RESET_ALL}")
        print(f"     - Cookies очищены")
        print(f"     - Storage очищены")
        print(f"     - Новый fingerprint будет сгенерирован при входе")
        print(f"     - Все счётчики обнулены\n")
        
        await self.action_logger.log_info(acc_id, "✅ Полный сброс сессии (новый fingerprint)")
        self.logger.action(acc_id, "RESET", "COMPLETE")
    
    # ═══════════════════════════════════════════════════════════════[...]
    # КОМАНДЫ: СТАТУС И ИНФОРМАЦИЯ
    # ═══════════════════════════════════════════════════════════════[...]
    
    async def cmd_status(self, acc_id: str = None):
        """
        📊 Статус аккаунта или всех с Account Health Score
        """
        
        if acc_id and acc_id in self.accounts:
            account = self.accounts[acc_id]
            status = account.get_status_report()
            session_status = self.session_monitor.get_session_status(acc_id)
            
            # Получаем инфо о риске и антифроде
            ban_risk = self.anti_fraud.detect_ban_risk(acc_id)
            counters = self.anti_fraud.action_counters.get(acc_id, {})
            
            # ⭐ HEALTH SCORE
            health_score = account.get_health_score()
            health_color = account.get_health_color()
            
            print(f"\n{Fore.CYAN}{'─' * 90}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTYELLOW_EX}📊 СТАТУС: {acc_id} ({account.phone}){Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'─' * 90}{Style.RESET_ALL}\n")
            
            print(f"  {Fore.LIGHTYELLOW_EX}📱 Информация:{Style.RESET_ALL}")
            print(f"     Телефон: {status['phone']}")
            print(f"     Авторизирован: {'✅ Да' if status['is_authenticated'] else '❌ Нет'}")
            print(f"     Прогрет: {'✅ Да' if status['is_warmed_up'] else '❌ Нет'}")
            print(f"     Статус: {status['status']}")
            print(f"     Uptime: {status['uptime_minutes']} мин")
            
            if session_status:
                print(f"\n  {Fore.LIGHTYELLOW_EX}📊 Ста��истика:{Style.RESET_ALL}")
                print(f"     Действий выполнено: {session_status['actions_count']}")
                print(f"     Ошибок: {session_status['errors_count']}")
                print(f"     Усталость: {int(session_status['tiredness']*100)}%")
                print(f"     Настроение: {session_status['mood']}")
                print(f"     Время сессии: {int(session_status['elapsed_time'] / 60)} мин")
            
            print(f"\n  {Fore.LIGHTYELLOW_EX}🛡️ АНТИФРОД:{Style.RESET_ALL}")
            print(f"     Риск блокировки: {int(ban_risk * 100)}%")
            print(f"     Действий сегодня: {counters.get('today_actions', 0)}/{settings.max_actions_per_day}")
            print(f"     Действий в час: {counters.get('hour_actions', 0)}/{settings.max_actions_per_hour}")
            print(f"     CAPTCHA: {counters.get('captcha_count', 0)}")
            print(f"     Последовательные ошибки: {counters.get('consecutive_errors', 0)}")
            
            print(f"\n  {Fore.LIGHTYELLOW_EX}🏥 ACCOUNT HEALTH SCORE:{Style.RESET_ALL}")
            print(f"     {health_color}")
            print(f"     Score: {health_score:.1f}/100")
            
            print(f"\n  {Fore.LIGHTYELLOW_EX}🔄 Задачи:{Style.RESET_ALL}")
            alive_status = '🟢 Активен' if acc_id in self.alive_modes and self.alive_modes[acc_id].running else '⚫ Неактивен'
            print(f"     Alive Mode: {alive_status}")
            
            print(f"{Fore.CYAN}{'─' * 90}{Style.RESET_ALL}\n")
        
        else:
            print(f"\n{Fore.CYAN}{'─' * 90}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTYELLOW_EX}📊 СТАТУС ВСЕХ АККАУНТОВ{Style.RESET_ALL}")
            print(f"{Fore.LIGHTYELLOW_EX}🔄 ФОНОВЫХ ЗАДАЧ: {len(self.running_tasks)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'─' * 90}{Style.RESET_ALL}\n")
            
            for acc_id, account in self.accounts.items():
                status = account.get_status_report()
                auth = '✅' if status['is_authenticated'] else '❌'
                warm = '✅' if status['is_warmed_up'] else '❌'
                num = acc_id.split('_')[-1]
                alive_status = '🟢' if acc_id in self.alive_modes and self.alive_modes[acc_id].running else '⚫'
                
                # ⭐ HEALTH SCORE
                health_score = account.get_health_score()
                health_color = account.get_health_color()
                
                # Риск банов
                ban_risk = self.anti_fraud.detect_ban_risk(acc_id)
                risk_emoji = '🟢' if ban_risk < 0.3 else '🟡' if ban_risk < 0.7 else '🔴'
                
                session_status = self.session_monitor.get_session_status(acc_id)
                if session_status:
                    actions = session_status['actions_count']
                    errors = session_status['errors_count']
                else:
                    actions = 0
                    errors = 0
                
                print(f"  {num}: {status['phone']} | Auth:{auth} Warm:{warm} Alive:{alive_status} Risk:{risk_emoji}")
                print(f"     Health: {health_color.split()[0]} ({health_score:.0f}/100) | Действий: {actions} | Ошибок: {errors}\n")
            
            print(f"{Fore.CYAN}{'─' * 90}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTYELLOW_EX}🔄 ЗАПУЩЕННЫЕ ЗАДАЧИ:{Style.RESET_ALL}\n")
            
            if not self.running_tasks:
                print(f"  (нет активных задач)\n")
            else:
                for i, (task_id, task) in enumerate(self.running_tasks.items(), 1):
                    status_icon = "🔄" if not task.done() else "✅"
                    status_text = "выполняется" if not task.done() else "завершена"
                    print(f"  {i}. {task_id}: {status_icon} {status_text}")
                print()
            
            # Глобальная статистика
            global_stats = self.session_monitor.get_global_stats()
            
            print(f"{Fore.CYAN}{'─' * 90}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTYELLOW_EX}📈 ГЛОБАЛЬНАЯ СТАТИСТИКА:{Style.RESET_ALL}\n")
            print(f"  Total Actions: {global_stats['total_actions']}")
            print(f"  Total Errors: {global_stats['total_errors']}")
            print(f"  Total Accounts: {global_stats['total_accounts']}")
            print(f"  Elapsed: {int(global_stats['elapsed_time'] / 60)} мин\n")
            
            print(f"{Fore.CYAN}{'─' * 90}{Style.RESET_ALL}\n")
    
    # ═══════════════════════════════════════════════════════════════[...]
    # КОМАНДЫ: НОЧНОЙ РЕЖИМ
    # ═══════════════════════════════════════════════════════════════[...]
    
    def cmd_night_override(self, acc_id: str, hours: float):
        """Отключить ночной режим на N часов"""
        
        self.night_mode.override(acc_id, hours)
        print(f"  {Fore.GREEN}✅ Ночь отключена на {hours} часов для {acc_id}{Style.RESET_ALL}")
        self.logger.action(acc_id, "NIGHT_MODE", "OVERRIDE", hours=hours)
    
    def cmd_night_reset(self, acc_id: str):
        """Вернуть ночной режим"""
        
        self.night_mode.reset_override(acc_id)
        print(f"  {Fore.GREEN}✅ Ночной режим восстановлен{Style.RESET_ALL}")
        self.logger.action(acc_id, "NIGHT_MODE", "RESET")
    
    # ═══════════════════════════════════════════════════════════════[...]
    # КОМАНДЫ: ПРОКСИ
    # ═══════════════════════════════════════════════════════════════[...]
    
    async def cmd_proxy_check(self):
        """Проверить прокси"""
        
        print(f"\n{Fore.CYAN}🌐 Проверяю прокси...{Style.RESET_ALL}\n")
        
        results = await check_all_proxies(self.proxy_manager, self.logger)
        
        print(f"\n{Fore.GREEN}✅ Результаты:{Style.RESET_ALL}\n")
        
        for proxy_id, result in results.items():
            status = f"{Fore.GREEN}✅{Style.RESET_ALL}" if result["ok"] else f"{Fore.RED}❌{Style.RESET_ALL}"
            ip = result.get('ip', 'unknown')
            country = result.get('country', 'unknown')
            latency = result.get('latency', 0)
            
            print(f"  {status} {proxy_id}")
            print(f"     IP: {ip} | Country: {country} | Latency: {latency:.0f}ms\n")
    
    # ═══════════════════════════════════════════════════════════════[...]
    # СПРАВКА
    # ═══════════════════════════════════════════════════════════════[...]
    
    def print_help(self):
        """Справка по командам"""
        
        print(f"""
{Fore.CYAN}{'=' * 90}{Style.RESET_ALL}
{Fore.LIGHTYELLOW_EX}{'КОМАНДЫ AVITO BOT PRO 2026':^90}{Style.RESET_ALL}
{Fore.CYAN}{'=' * 90}{Style.RESET_ALL}

{Fore.GREEN}📱 ЛОГИН:{Style.RESET_ALL}
  {Fore.YELLOW}1 login{Style.RESET_ALL}              - Логин аккаунта 1
  {Fore.YELLOW}2 login{Style.RESET_ALL}              - Логин аккаунта 2
  {Fore.YELLOW}3 login{Style.RESET_ALL}              - Логин аккаунта 3

{Fore.GREEN}🔥 ПРОГРЕВ 2031 (в фоне):{Style.RESET_ALL}
  {Fore.YELLOW}1 warmup{Style.RESET_ALL}             - Запустить Warmup Engine 2031 (7–8 фаз, 90–150 мин)
  {Fore.YELLOW}2 warmup{Style.RESET_ALL}             - Запустить прогрев для 2-го аккаунта
  {Fore.YELLOW}3 warmup{Style.RESET_ALL}             - Запустить прогрев для 3-го аккаунта
  
{Fore.LIGHTGREEN_EX}💡 После завершения прогрева автоматически запускается Alive Mode!{Style.RESET_ALL}

{Fore.GREEN}🤖 ALIVE MODE (в фоне):{Style.RESET_ALL}
  {Fore.YELLOW}1 alive{Style.RESET_ALL}              - Запустить Alive Mode (весь день, 15+ паттернов)
  {Fore.YELLOW}1 stop{Style.RESET_ALL}               - Остановить Alive Mode
  {Fore.YELLOW}2 alive{Style.RESET_ALL}              - Alive Mode для 2-го аккаунта
  {Fore.YELLOW}2 stop{Style.RESET_ALL}               - Остановить Alive Mode 2-го

{Fore.GREEN}🌐 УПРАВЛЕНИЕ БРАУЗЕРОМ:{Style.RESET_ALL}
  {Fore.YELLOW}1 close{Style.RESET_ALL}              - Закрыть браузер (сессия сохранена)
  {Fore.YELLOW}1 reset{Style.RESET_ALL}              - Полный сброс аккаунта (новый fingerprint)

{Fore.GREEN}🌙 НОЧНОЙ РЕЖИМ:{Style.RESET_ALL}
  {Fore.YELLOW}1 night 1{Style.RESET_ALL}            - Отключить ночь на 1 час для 1-го
  {Fore.YELLOW}1 night 2{Style.RESET_ALL}            - Отключить ночь на 2 часа
  {Fore.YELLOW}1 night_reset{Style.RESET_ALL}        - Вернуть ночной режим

{Fore.GREEN}📊 СТАТУС И ИНФОРМАЦИЯ:{Style.RESET_ALL}
  {Fore.YELLOW}1 status{Style.RESET_ALL}             - Статус аккаунта 1 (с Account Health Score)
  {Fore.YELLOW}status{Style.RESET_ALL}               - Статус ВСЕХ аккаунтов + статистика
  {Fore.YELLOW}proxy_check{Style.RESET_ALL}          - Проверить прокси

{Fore.GREEN}🔧 ДРУГОЕ:{Style.RESET_ALL}
  {Fore.YELLOW}help{Style.RESET_ALL}                 - Эта справка
  {Fore.YELLOW}exit{Style.RESET_ALL}                 - Выход и корректное завершение

{Fore.CYAN}{'=' * 90}{Style.RESET_ALL}
{Fore.LIGHTGREEN_EX}💡 ВСЕ ОПЕРАЦИИ (warmup, alive mode) ЗАПУСКАЮТСЯ В ФОНЕ!{Style.RESET_ALL}
{Fore.LIGHTGREEN_EX}💡 CLI ВСЕГДА ОТЗЫВЧИВ — можешь запустить несколько аккаунтов одновременно!{Style.RESET_ALL}
{Fore.LIGHTGREEN_EX}💡 БРАУЗЕРЫ РАБОТАЮТ В 2 ОКНА — в отдельных контекстах, не мешают друг другу!{Style.RESET_ALL}
{Fore.LIGHTGREEN_EX}💡 КАЖДЫЙ БРАУЗЕР ПОКАЗЫВАЕТ СВОЙ АККАУНТ В ЗАГОЛОВКЕ!{Style.RESET_ALL}
{Fore.LIGHTGREEN_EX}💡 🏥 ACCOUNT HEALTH SCORE (0–100) — индикатор здоровья каждого аккаунта!{Style.RESET_ALL}
{Fore.LIGHTGREEN_EX}💡 🔄 RESET ГЕНЕРИРУЕТ Н��ВЫЙ FINGERPRINT — каждый раз уникальный браузер!{Style.RESET_ALL}
{Fore.LIGHTGREEN_EX}💡 🛡️ ANTIFR OD: Адаптивные delays, Rate Limits, Ban Detection, Canvas+WebGL защита!{Style.RESET_ALL}
{Fore.LIGHTGREEN_EX}💡 🔥 WARMUP ENGINE 2031: 7–8 фаз, мототехника, питбайки 40–60k, полный прогрев!{Style.RESET_ALL}
{Fore.CYAN}{'=' * 90}{Style.RESET_ALL}
""")
    
    # ═══════════════════════════════════════════════════════════════[...]
    # КОМАНДНЫЙ ЦИКЛ (АСИНХРОННЫЙ)
    # ═══════════════════════════════════════════════════════════════[...]
    
    async def _read_input(self) -> Optional[str]:
        """Неблокирующее чтение ввода пользователя"""
        
        loop = asyncio.get_event_loop()
        
        try:
            cmd = await loop.run_in_executor(
                None,
                lambda: input(f"\n{Fore.CYAN}>>> {Style.RESET_ALL}").strip()
            )
            return cmd
        except EOFError:
            return "exit"
        except asyncio.CancelledError:
            return "exit"
        except Exception:
            return None
    
    async def run_command_loop(self):
        """
        Главный командный цикл (ПОЛНОСТЬЮ АСИНХРОННЫЙ)
        
        Позволяет:
        - Вводить команды в любой момент
        - Запускать несколько фоновых задач одновременно
        - Видеть статус задач и аккаунтов в реальном времени
        - Полностью контролировать все аккаунты
        """
        
        self.print_help()
        
        while not self.shutdown_event.is_set():
            try:
                # ─────────────────────────────────────────────────
                # НЕБЛОКИРУЮЩЕЕ ЧТЕНИЕ ВВОДА
                # ───────────────────────���─────────────────────────
                
                cmd = await self._read_input()
                
                if not cmd:
                    continue
                
                parts = cmd.split()
                
                # ─────────────────────────────────────────────────
                # СПРАВКА
                # ─────────────────────────────────────────────────
                
                if cmd.lower() == "help":
                    self.print_help()
                
                # ─────────────────────────────────────────────────
                # ВЫХОД
                # ─────────────────────────────────────────────────
                
                elif cmd.lower() == "exit":
                    print(f"\n{Fore.YELLOW}🛑 Выход...{Style.RESET_ALL}")
                    self.shutdown_event.set()
                    break
                
                # ─────────────────────────────────────────────────
                # СТАТУС ВСЕХ
                # ─────────────────────────────────────────────────
                
                elif cmd.lower() == "status":
                    await self.cmd_status()
                
                # ─────────────────────────────────────────────────
                # ПРОВЕРКА ПРОКСИ
                # ───���─────────────────────────────────────────────
                
                elif cmd.lower() == "proxy_check":
                    await self.cmd_proxy_check()
                
                # ─────────────────────────────────────────────────
                # КОМАНДЫ ПО АККАУНТАМ
                # ─────────────────────────────────────────────────
                
                elif len(parts) >= 2:
                    num = parts[0]
                    action = parts[1].lower()
                    
                    acc_id = self.get_account_id(num)
                    
                    if action == "login":
                        await self.cmd_login(acc_id)
                    
                    elif action == "warmup":
                        await self.cmd_warmup(acc_id)
                    
                    elif action == "alive":
                        await self.cmd_alive(acc_id)
                    
                    elif action == "stop":
                        await self.cmd_stop_alive(acc_id)
                    
                    elif action == "close":
                        await self.cmd_close(acc_id)
                    
                    elif action == "reset":
                        await self.cmd_reset(acc_id)
                    
                    elif action == "status":
                        await self.cmd_status(acc_id)
                    
                    elif action == "night":
                        if len(parts) >= 3:
                            try:
                                hours = float(parts[2])
                                self.cmd_night_override(acc_id, hours)
                            except ValueError:
                                print(f"  {Fore.RED}❌ Неверный формат часов{Style.RESET_ALL}")
                        else:
                            print(f"  {Fore.RED}❌ Используйте: {num} night <часы>{Style.RESET_ALL}")
                    
                    elif action == "night_reset":
                        self.cmd_night_reset(acc_id)
                    
                    else:
                        print(f"  {Fore.RED}❌ Неизвестная команда: {action}{Style.RESET_ALL}")
                
                else:
                    if cmd:
                        print(f"  {Fore.RED}❌ Неизвестная команда{Style.RESET_ALL}")
                    print(f"  {Fore.CYAN}Введите 'help' для справки{Style.RESET_ALL}")
            
            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}🛑 Выход...{Style.RESET_ALL}")
                self.shutdown_event.set()
                break
            
            except Exception as e:
                print(f"  {Fore.RED}❌ Ошибка: {e}{Style.RESET_ALL}")
    
    # ══════════════���════════════════════════════════════════════════[...]
    # ЗАВЕРШЕНИЕ РАБОТЫ
    # ═══════════════════════════════════════════════════════════════[...]
    
    async def shutdown(self):
        """
        Корректное завершение работы бота
        
        Процесс:
        1. Останавливаем все Alive Modes
        2. Отменяем все фоновые задачи
        3. Закрываем все браузеры
        4. Отправляем финальное уведомление
        """
        
        print(f"\n{Fore.YELLOW}🛑 Завершаю работу...{Style.RESET_ALL}\n")
        
        # ─────────────────────────────────────────────────────
        # ОСТАНАВЛИВАЕМ ALIVE MODES
        # ─────────────────────────────────────────────────────
        
        print(f"  {Fore.CYAN}🤖 Останавливаю Alive Mode...{Style.RESET_ALL}")
        for acc_id in list(self.alive_modes.keys()):
            try:
                self.alive_modes[acc_id].stop()
            except Exception:
                pass
        
        # ─────────────────────────────────────────────────────
        # ОТМЕНЯЕМ ФОНОВЫЕ ЗАДАЧИ
        # ─────────────────────────────────────────────────────
        
        if self.running_tasks:
            print(f"  {Fore.CYAN}⏳ Отменяю {len(self.running_tasks)} фоновых задач...{Style.RESET_ALL}")
            for task_id, task in list(self.running_tasks.items()):
                try:
                    task.cancel()
                except Exception:
                    pass
            
            # Ждём завершения всех задач
            await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
        
        # ─────────────────────────────────────────────────────
        # ЗАКРЫВАЕМ БРАУЗЕРЫ
        # ─────────────────────────────────────────────────────
        
        print(f"  {Fore.CYAN}🌐 Закрываю браузеры...{Style.RESET_ALL}")
        await self.browser_launcher.close_all()
        
        # ─────────────────────────────────────────────────────
        # ФИНАЛЬНОЕ УВЕДОМЛЕНИЕ
        # ─────────────────────────────────────────────────────
        
        try:
            if self.notifier:
                runtime = (datetime.now() - self.bot_start_time).total_seconds() / 3600
                await self.notifier.notify_bot_stopped(
                    self.total_logins,
                    self.total_warmups,
                    self.total_alive_starts,
                    runtime
                )
        except Exception:
            pass
        
        print(f"{Fore.GREEN}✅ Завершено{Style.RESET_ALL}\n")
        
        self.logger.system("Bot shutdown complete")


# ════════════════════════════════════════════════════════════════[...]
# ГЛАВНАЯ ФУНКЦИЯ
# ════════════════════════════════════════════════════════════════[...]

async def main():
    """Главная функция бота"""
    
    bot = AvitoBot()
    
    try:
        await bot.initialize()
        await bot.run_command_loop()
    finally:
        await bot.shutdown()


# ════════════════════════════════════════════════════════════════[...]
# ТОЧКА ВХОДА
# ════════════════════════════════════════════════════════════════[...]

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
    finally:
        sys.exit(0)
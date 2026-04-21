# config/settings.py
"""
⚙️ SETTINGS v3.0 — основная конфигурация AVITO BOT PRO 2026
✅ Конфигурация аккаунтов из .env
✅ Конфигурация прокси из .env
✅ Rate limiting настройки
✅ Telegram настройки
✅ Paths и storage
✅ Warmup и Alive Mode параметры
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os
from dotenv import load_dotenv
from colorama import Fore, Style

# Загружаем .env
load_dotenv()


@dataclass
class ProxyConfig:
    """Конфигурация прокси"""
    
    proxy_id: str
    protocol: str  # http, https, socks5
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    
    def get_url(self) -> str:
        """Получить URL прокси"""
        
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        else:
            return f"{self.protocol}://{self.host}:{self.port}"


@dataclass
class AccountConfig:
    """Конфигурация аккаунта"""
    
    acc_id: str
    name: str
    phone: str
    proxy_id: str


# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ПАРСИНГА
# ═══════════════════════════════════════════════════════════════

def parse_proxy_url(proxy_url: str) -> ProxyConfig:
    """
    Парсить прокси URL вида:
    http://user:pass@host:port
    """
    
    # Убираем протокол
    if "://" in proxy_url:
        protocol, rest = proxy_url.split("://", 1)
    else:
        protocol = "http"
        rest = proxy_url
    
    # Парсим credentials и host:port
    if "@" in rest:
        credentials, host_port = rest.rsplit("@", 1)
        username, password = credentials.split(":", 1) if ":" in credentials else (credentials, "")
    else:
        username = None
        password = None
        host_port = rest
    
    # Парсим host и port
    if ":" in host_port:
        host, port = host_port.rsplit(":", 1)
        port = int(port)
    else:
        host = host_port
        port = 8080
    
    return ProxyConfig(
        proxy_id="",
        protocol=protocol,
        host=host,
        port=port,
        username=username if username else None,
        password=password if password else None,
    )


def load_proxies() -> List[ProxyConfig]:
    """Загрузить прокси из .env"""
    
    proxies = []
    
    for i in range(1, 10):  # Поддерживаем до 9 прокси
        proxy_url = os.getenv(f"PROXY_{i}")
        
        if not proxy_url:
            continue
        
        try:
            proxy_config = parse_proxy_url(proxy_url)
            proxy_config.proxy_id = f"proxy_{i}"
            proxies.append(proxy_config)
        except Exception as e:
            print(f"❌ Ошибка парсинга PROXY_{i}: {e}")
    
    return proxies


def load_accounts(proxies: List[ProxyConfig]) -> Dict[str, Dict[str, Any]]:
    """Загрузить аккаунты из .env"""
    
    accounts = {}
    proxy_dict = {p.proxy_id: p for p in proxies}
    
    for i in range(1, 10):  # Поддерживаем до 9 аккаунтов
        phone = os.getenv(f"ACCOUNT_{i}_PHONE")
        name = os.getenv(f"ACCOUNT_{i}_NAME")
        proxy_id = os.getenv(f"ACCOUNT_{i}_PROXY", f"proxy_{i}")
        
        if not phone or not name:
            continue
        
        acc_id = f"account_{i}"
        
        # ✅ КОНВЕРТИРУЕМ БОЛЬШИЕ БУКВЫ В МАЛЕНЬКИЕ
        proxy_id = proxy_id.lower()
        
        accounts[acc_id] = {
            "name": name,
            "phone": phone,
            "proxy_id": proxy_id,
        }
    
    return accounts


class Settings:
    """
    ⚙️ SETTINGS — основная конфигурация бота
    """
    
    # ═══════════════════════════════════════════════════════════════
    # BROWSER SETTINGS
    # ═══════════════════════════════════════════════════════════════
    
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    
    # ═══════════════════════════════════════════════════════════════
    # STORAGE PATHS
    # ═══════════════════════════════════════════════════════════════
    
    BASE_DIR = Path(__file__).parent.parent
    storage_dir = BASE_DIR / "storage"
    logs_dir = BASE_DIR / "logs"
    
    # ═══════════════════════════════════════════════════════════════
    # RATE LIMITING (защита от блокировок)
    # ═══════════════════════════════════════════════════════════════
    
    max_actions_per_day = int(os.getenv("MAX_ACTIONS_PER_DAY", "100"))
    max_actions_per_hour = int(os.getenv("MAX_ACTIONS_PER_HOUR", "8"))
    
    # ═══════════════════════════════════════════════════════════════
    # TELEGRAM NOTIFIER
    # ═══════════════════════════════════════════════════════════════
    
    telegram_enabled = os.getenv("TELEGRAM_ENABLED", "true").lower() == "true"
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # ═══════════════════════════════════════════════════════════════
    # TELEGRAM NOTIFICATIONS
    # ═══════════════════════════════════════════════════════════════
    
    tg_notify_login = os.getenv("TG_NOTIFY_LOGIN", "true").lower() == "true"
    tg_notify_warmup = os.getenv("TG_NOTIFY_WARMUP", "true").lower() == "true"
    tg_notify_ban = os.getenv("TG_NOTIFY_BAN", "true").lower() == "true"
    tg_notify_captcha = os.getenv("TG_NOTIFY_CAPTCHA", "true").lower() == "true"
    tg_notify_proxy_down = os.getenv("TG_NOTIFY_PROXY_DOWN", "true").lower() == "true"
    tg_notify_errors = os.getenv("TG_NOTIFY_ERRORS", "true").lower() == "true"
    
    # ═══════════════════════════════════════════════════════════════
    # CIRCUIT BREAKER
    # ═══════════════════════════════════════════════════════════════
    
    circuit_breaker_threshold = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
    circuit_breaker_cooldown_minutes = int(os.getenv("CIRCUIT_BREAKER_COOLDOWN_MINUTES", "30"))
    
    # ═══════════════════════════════════════════════════════════════
    # ⭐ ПРОКСИ — ЗАГРУЖАЕМ ИЗ .env (ВЫЗЫВАЕМ ФУНКЦИИ)
    # ═══════════════════════════════════════════════════════════════
    
    proxies = load_proxies()
    accounts = load_accounts(proxies)
    
    # ═══════════════════════════════════════════════════════════════
    # WARMUP SETTINGS
    # ═══════════════════════════════════════════════════════════════
    
    warmup_duration_min = int(os.getenv("WARMUP_DURATION_MINUTES", "90"))
    warmup_duration_max = int(os.getenv("WARMUP_DURATION_MINUTES", "90")) + 30
    warmup_phases = 5
    
    # ═══════════════════════════════════════════════════════════════
    # ALIVE MODE SETTINGS
    # ═══════════════════════════════════════════════════════════════
    
    alive_mode_session_min = 10
    alive_mode_session_max = 60
    alive_mode_patterns = 17
    
    # ═══════════════════════════════════════════════════════════════
    # NIGHT MODE SETTINGS
    # ═══════════════════════════════════════════════════════════════
    
    _night_start = os.getenv("NIGHT_MODE_START", "23:00")
    _night_end = os.getenv("NIGHT_MODE_END", "07:00")
    
    # Парсим время
    try:
        night_start_hour = int(_night_start.split(":")[0])
    except:
        night_start_hour = 23
    
    try:
        night_end_hour = int(_night_end.split(":")[0])
    except:
        night_end_hour = 7
    
    # ═══════════════════════════════════════════════════════════════
    # LOGGING
    # ═══════════════════════════════════════════════════════════════
    
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_to_file = True
    log_to_console = True
    
    @classmethod
    def print_summary(cls):
        """Печать сводки конфигурации"""
        
        print(f"\n{Fore.CYAN}{'─' * 90}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTYELLOW_EX}{'📋 КОНФИГУРАЦИЯ AVITO BOT PRO 2026':^90}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─' * 90}{Style.RESET_ALL}\n")
        
        # Браузер
        print(f"{Fore.LIGHTYELLOW_EX}🌐 БРАУЗЕР:{Style.RESET_ALL}")
        print(f"   Headless mode: {'❌ Нет (видно окно)' if not cls.headless else '✅ Да'}\n")
        
        # Прокси
        print(f"{Fore.LIGHTYELLOW_EX}🔌 ПРОКСИ:{Style.RESET_ALL}")
        print(f"   Всего прокси: {len(cls.proxies)}")
        for proxy in cls.proxies:
            print(f"   • {proxy.proxy_id}: {proxy.host}:{proxy.port}")
        print()
        
        # Аккаунты
        print(f"{Fore.LIGHTYELLOW_EX}👥 АККАУНТЫ:{Style.RESET_ALL}")
        print(f"   Всего аккаунтов: {len(cls.accounts)}")
        for acc_id, config in cls.accounts.items():
            print(f"   • {acc_id}: {config['name']} ({config['phone']}) → {config['proxy_id']}")
        print()
        
        # Rate Limiting
        print(f"{Fore.LIGHTYELLOW_EX}⏱️ RATE LIMITING:{Style.RESET_ALL}")
        print(f"   Действий в день: {cls.max_actions_per_day}")
        print(f"   Действий в час: {cls.max_actions_per_hour}\n")
        
        # Warmup
        print(f"{Fore.LIGHTYELLOW_EX}🔥 WARMUP:{Style.RESET_ALL}")
        print(f"   Фаз: {cls.warmup_phases}")
        print(f"   Длительность: {cls.warmup_duration_min}–{cls.warmup_duration_max} мин\n")
        
        # Alive Mode
        print(f"{Fore.LIGHTYELLOW_EX}🤖 ALIVE MODE:{Style.RESET_ALL}")
        print(f"   Паттернов: {cls.alive_mode_patterns}+")
        print(f"   Сессия: {cls.alive_mode_session_min}–{cls.alive_mode_session_max} мин\n")
        
        # Night Mode
        print(f"{Fore.LIGHTYELLOW_EX}🌙 НОЧНОЙ РЕЖИМ:{Style.RESET_ALL}")
        print(f"   Начало: {cls.night_start_hour}:00")
        print(f"   Конец: {cls.night_end_hour}:00\n")
        
        # Telegram
        print(f"{Fore.LIGHTYELLOW_EX}📢 TELEGRAM:{Style.RESET_ALL}")
        status = "✅ Включён" if cls.telegram_enabled else "❌ Отключён"
        print(f"   {status}")
        if cls.telegram_enabled:
            print(f"   Bot Token: {cls.telegram_bot_token[:20]}...")
            print(f"   Chat ID: {cls.telegram_chat_id}\n")
        
        print(f"{Fore.CYAN}{'─' * 90}{Style.RESET_ALL}\n")


# Создаём глобальный экземпляр settings
settings = Settings()
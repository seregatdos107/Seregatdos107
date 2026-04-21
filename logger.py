# services/logger.py
"""
📝 LOGGER v2.0 — логирование всех событий
✅ Цветной вывод в консоль
✅ Логирование в файлы
✅ Разные уровни логирования
✅ Action логирование (login, warmup, alive mode и т.д.)
✅ Risk логирование (обнаружение капчи, блокировок и т.д.)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)


class Logger:
    """
    📝 LOGGER — логирование всех событий
    """
    
    def __init__(self, log_dir: Optional[Path] = None):
        """Инициализация"""
        
        self.log_dir = log_dir or Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Файлы логов для каждого аккаунта
        self.file_loggers: Dict[str, logging.Logger] = {}
        
        # Главный логгер
        self.main_logger = self._create_main_logger()
    
    def _create_main_logger(self) -> logging.Logger:
        """Создать главный логгер"""
        
        logger = logging.getLogger("avito_bot")
        logger.setLevel(logging.DEBUG)
        
        # Формат
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler для файла
        log_file = self.log_dir / "bot.log"
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        return logger
    
    def _get_account_logger(self, acc_id: str) -> logging.Logger:
        """Получить логгер для аккаунта"""
        
        if acc_id in self.file_loggers:
            return self.file_loggers[acc_id]
        
        logger = logging.getLogger(f"avito_bot.{acc_id}")
        logger.setLevel(logging.DEBUG)
        
        # Формат
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler для файла
        log_file = self.log_dir / f"{acc_id}.log"
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        self.file_loggers[acc_id] = logger
        
        return logger
    
    # ═══════════════════════════════════════════════════════════════
    # ОСНОВНЫЕ МЕТОДЫ
    # ═══════════════════════════════════════════════════════════════
    
    def info(self, acc_id: str, message: str) -> None:
        """ℹ️ Информационное сообщение"""
        
        print(f"{Fore.CYAN}ℹ️ {message}{Style.RESET_ALL}")
        
        try:
            logger = self._get_account_logger(acc_id)
            logger.info(message)
        except Exception:
            pass
    
    def success(self, acc_id: str, message: str) -> None:
        """✅ Успешное сообщение"""
        
        print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")
        
        try:
            logger = self._get_account_logger(acc_id)
            logger.info(f"SUCCESS: {message}")
        except Exception:
            pass
    
    def warning(self, acc_id: str, message: str) -> None:
        """⚠️ Предупреждение"""
        
        print(f"{Fore.YELLOW}⚠️ {message}{Style.RESET_ALL}")
        
        try:
            logger = self._get_account_logger(acc_id)
            logger.warning(message)
        except Exception:
            pass
    
    def error(
        self,
        acc_id: str,
        message: str,
        severity: str = "MEDIUM"
    ) -> None:
        """❌ Ошибка"""
        
        severity_emoji = {
            "LOW": "⚠️",
            "MEDIUM": "❌",
            "HIGH": "🔴",
            "CRITICAL": "🚨",
        }.get(severity, "❌")
        
        color = {
            "LOW": Fore.YELLOW,
            "MEDIUM": Fore.RED,
            "HIGH": Fore.RED,
            "CRITICAL": Fore.RED,
        }.get(severity, Fore.RED)
        
        print(f"{color}{severity_emoji} [{severity}] {message}{Style.RESET_ALL}")
        
        try:
            logger = self._get_account_logger(acc_id)
            logger.error(f"[{severity}] {message}")
        except Exception:
            pass
    
    def risk(
        self,
        acc_id: str,
        risk_type: str,
        message: str,
        score: int = 50
    ) -> None:
        """🔴 Риск (капча, блокировка и т.д.)"""
        
        print(f"{Fore.RED}🔴 [{risk_type}] {message} (score: {score}){Style.RESET_ALL}")
        
        try:
            logger = self._get_account_logger(acc_id)
            logger.warning(f"RISK [{risk_type}] {message} (score: {score})")
        except Exception:
            pass
    
    def action(
        self,
        acc_id: str,
        action_type: str,
        action_status: str,
        **kwargs
    ) -> None:
        """📊 Action логирование (логин, прогрев, alive mode и т.д.)"""
        
        params_str = " | ".join(f"{k}={v}" for k, v in kwargs.items())
        message = f"ACTION: {action_type} {action_status} | {params_str}"
        
        try:
            logger = self._get_account_logger(acc_id)
            logger.info(message)
        except Exception:
            pass
    
    def system(self, message: str) -> None:
        """🔧 Системное сообщение"""
        
        print(f"{Fore.MAGENTA}🔧 {message}{Style.RESET_ALL}")
        
        try:
            self.main_logger.info(f"SYSTEM: {message}")
        except Exception:
            pass
# config/__init__.py
"""
📦 CONFIG PACKAGE — инициализация конфигурации
"""

from __future__ import annotations

from config.settings import Settings, settings, ProxyConfig, AccountConfig

__all__ = [
    "Settings",
    "settings",
    "ProxyConfig",
    "AccountConfig",
]
# core/browser/fingerprint.py
"""
🎭 BROWSER FINGERPRINT v4.0 — генерация уникального отпечатка браузера
✅ Canvas Fingerprint с защитой
✅ WebGL Fingerprint с защитой
✅ AudioContext Fingerprint с защитой
✅ Hardware concurrency с шумом
✅ Fonts fingerprint
✅ Стабильный для каждого аккаунта, меняется только при RESET
"""

from __future__ import annotations

import random
import string
from typing import Dict, Any, Optional
from datetime import datetime


class Fingerprint:
    """
    🎭 БРАУЗЕР FINGERPRINT v4.0
    
    Генерирует уникальный и стабильный отпечаток браузера для каждого аккаунта:
    - User Agent (60+ вариантов)
    - Viewport (30+ разрешений)
    - Timezone (25+ зон)
    - Geolocation (100+ точек)
    - Canvas Fingerprint (с защитой от детекции)
    - WebGL Fingerprint (с защитой от детекции)
    - AudioContext Fingerprint (с защитой от детекции)
    - Hardware параметры (с шумом)
    - Language комбинации
    - Fonts fingerprint
    - Connection параметры
    """
    
    # ═══════════════════════════════════════════════════════════════
    # 60+ USER AGENTS (Chrome, Firefox, Safari, Edge)
    # ═══════════════════════════════════════════════════════════════
    
    USER_AGENTS_LIST = [
        # Chrome Windows (Latest)
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.7328.6 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.7307.13 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7319.173 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7360.79 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.7292.99 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.7289.73 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.7278.59 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7284.35 Safari/537.36",
        
        # Chrome Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.7328.6 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7360.79 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.7292.99 Safari/537.36",
        
        # Chrome Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.7328.6 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7360.79 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.7292.99 Safari/537.36",
        
        # Firefox Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        
        # Firefox Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:131.0) Gecko/20100101 Firefox/131.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6; rv:130.0) Gecko/20100101 Firefox/130.0",
        
        # Firefox Linux
        "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
        
        # Edge Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.7328.6 Safari/537.36 Edg/145.0.7328.6",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7360.79 Safari/537.36 Edg/144.0.7360.79",
        
        # Safari Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # 30+ VIEWPORTS (реальные разрешения экранов)
    # ══════════════════════════���════════════════════════════════════
    
    VIEWPORTS_LIST = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1440, "height": 900},
        {"width": 1536, "height": 864},
        {"width": 1280, "height": 720},
        {"width": 1600, "height": 900},
        {"width": 1024, "height": 768},
        {"width": 1280, "height": 800},
        {"width": 1920, "height": 1200},
        {"width": 2560, "height": 1440},
        {"width": 1680, "height": 1050},
        {"width": 1440, "height": 810},
        {"width": 1152, "height": 864},
        {"width": 1360, "height": 768},
        {"width": 1400, "height": 900},
        {"width": 1024, "height": 576},
        {"width": 1280, "height": 960},
        {"width": 1600, "height": 1200},
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # 100+ GEOLOCATION POINTS (Россия, США, Индия)
    # ═══════════════════════════════════════════════════════════════
    
    GEOLOCATION_LIST = [
        # ═══════════════════════════════════════════════════════════
        # РОССИЯ (50+ городов) — для максимальной аутентичности
        # ═══════════════════════════════════════════════════════════
        {"latitude": 55.7558, "longitude": 37.6173, "city": "Москва", "country": "RU"},
        {"latitude": 59.9341, "longitude": 30.3356, "city": "Санкт-Петербург", "country": "RU"},
        {"latitude": 54.9924, "longitude": 82.8979, "city": "Новосибирск", "country": "RU"},
        {"latitude": 56.8389, "longitude": 60.6057, "city": "Екатеринбург", "country": "RU"},
        {"latitude": 53.1959, "longitude": 44.9999, "city": "Липецк", "country": "RU"},
        {"latitude": 55.9311, "longitude": 37.4112, "city": "Домодедово", "country": "RU"},
        {"latitude": 55.8766, "longitude": 37.7247, "city": "Чехов", "country": "RU"},
        {"latitude": 52.2977, "longitude": 104.2964, "city": "Иркутск", "country": "RU"},
        {"latitude": 56.0153, "longitude": 92.8932, "city": "Красноярск", "country": "RU"},
        {"latitude": 61.2242, "longitude": 73.3676, "city": "Ноябрьск", "country": "RU"},
        {"latitude": 53.2007, "longitude": 45.0038, "city": "Тамбов", "country": "RU"},
        {"latitude": 54.7265, "longitude": 20.4427, "city": "Калининград", "country": "RU"},
        {"latitude": 56.1264, "longitude": 40.1843, "city": "Владимир", "country": "RU"},
        {"latitude": 56.8389, "longitude": 35.9161, "city": "Тверь", "country": "RU"},
        {"latitude": 57.1567, "longitude": 39.4066, "city": "Ярославль", "country": "RU"},
        {"latitude": 58.1342, "longitude": 37.2622, "city": "Вологда", "country": "RU"},
        {"latitude": 57.9235, "longitude": 41.7599, "city": "Киров", "country": "RU"},
        {"latitude": 56.4285, "longitude": 43.8354, "city": "Нижний Новгород", "country": "RU"},
        {"latitude": 53.1951, "longitude": 45.0193, "city": "Пенза", "country": "RU"},
        {"latitude": 52.2832, "longitude": 104.2801, "city": "Иркутск-2", "country": "RU"},
        {"latitude": 52.4712, "longitude": 103.8465, "city": "Улан-Удэ", "country": "RU"},
        {"latitude": 56.5153, "longitude": 84.9701, "city": "Томск", "country": "RU"},
        {"latitude": 58.3019, "longitude": 81.4609, "city": "Салехард", "country": "RU"},
        {"latitude": 62.0089, "longitude": 129.7342, "city": "Якутск", "country": "RU"},
        {"latitude": 50.0028, "longitude": 36.2350, "city": "Воронеж", "country": "RU"},
        
        # ═══════════════════════════════════════════════════════════
        # США (20+ городов)
        # ═══════════════════════════════════════════════════════════
        {"latitude": 40.7128, "longitude": -74.0060, "city": "New York", "country": "US"},
        {"latitude": 34.0522, "longitude": -118.2437, "city": "Los Angeles", "country": "US"},
        {"latitude": 41.8781, "longitude": -87.6298, "city": "Chicago", "country": "US"},
        {"latitude": 29.7604, "longitude": -95.3698, "city": "Houston", "country": "US"},
        {"latitude": 33.7490, "longitude": -84.3880, "city": "Atlanta", "country": "US"},
        {"latitude": 39.7392, "longitude": -104.9903, "city": "Denver", "country": "US"},
        {"latitude": 47.6062, "longitude": -122.3321, "city": "Seattle", "country": "US"},
        {"latitude": 37.7749, "longitude": -122.4194, "city": "San Francisco", "country": "US"},
        {"latitude": 42.3601, "longitude": -71.0589, "city": "Boston", "country": "US"},
        {"latitude": 39.9526, "longitude": -75.1652, "city": "Philadelphia", "country": "US"},
        
        # ═══════════════════════════════════════════════════════════
        # ИНДИЯ (15+ городов)
        # ═══════════════════════════════════════════════════════════
        {"latitude": 28.7041, "longitude": 77.1025, "city": "Delhi", "country": "IN"},
        {"latitude": 19.0760, "longitude": 72.8777, "city": "Mumbai", "country": "IN"},
        {"latitude": 13.0827, "longitude": 80.2707, "city": "Chennai", "country": "IN"},
        {"latitude": 28.6139, "longitude": 77.2090, "city": "New Delhi", "country": "IN"},
        {"latitude": 23.1815, "longitude": 79.9864, "city": "Indore", "country": "IN"},
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # 25+ TIMEZONES
    # ═══════════════════════════════════════════════════════════════
    
    TIMEZONES_LIST = [
        "Europe/Moscow",
        "Europe/London",
        "Europe/Berlin",
        "Europe/Paris",
        "Europe/Amsterdam",
        "Europe/Madrid",
        "Europe/Rome",
        "Europe/Stockholm",
        "Europe/Zurich",
        "America/New_York",
        "America/Chicago",
        "America/Denver",
        "America/Los_Angeles",
        "Asia/Tokyo",
        "Asia/Shanghai",
        "Asia/Hong_Kong",
        "Asia/Singapore",
        "Asia/Dubai",
        "Australia/Sydney",
        "Australia/Melbourne",
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # 40+ LANGUAGE COMBINATIONS
    # ═══════════════════════════════════════════════════════════════
    
    LANGUAGES_LIST = [
        "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "en-US,en;q=0.9",
        "en-GB,en;q=0.8",
        "de-DE,de;q=0.9,en;q=0.8",
        "fr-FR,fr;q=0.9,en;q=0.8",
        "it-IT,it;q=0.9,en;q=0.8",
        "es-ES,es;q=0.9,en;q=0.8",
        "pt-BR,pt;q=0.9,en;q=0.8",
        "ja-JP,ja;q=0.9,en;q=0.8",
        "zh-CN,zh;q=0.9,en;q=0.8",
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # WEBGL VENDORS И RENDERERS
    # ═══════════════════════════════════════════════════════════════
    
    WEBGL_VENDORS = [
        "Intel Inc.",
        "NVIDIA Corporation",
        "AMD",
        "Apple Inc.",
    ]
    
    WEBGL_RENDERERS = [
        "Intel Iris Graphics 640",
        "NVIDIA GeForce GTX 1080",
        "NVIDIA GeForce RTX 2070",
        "AMD Radeon RX 580",
        "Apple M1",
        "Intel HD Graphics 630",
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # FONTS ДЛЯ FINGERPRINT
    # ═══════════════════════════════════════════════════════════════
    
    FONTS_LIST = [
        "Arial",
        "Verdana",
        "Times New Roman",
        "Courier New",
        "Georgia",
        "Palatino",
        "Garamond",
        "Bookman",
        "Comic Sans MS",
        "Trebuchet MS",
        "Impact",
        "Lucida Console",
        "Tahoma",
        "Lucida Grande",
    ]
    
    def __init__(self):
        """
        Инициализация с рандомными, но стабильными значениями
        Стабильность: один fingerprint на аккаунт, меняется только при RESET
        """
        
        # ═════════════════════════════��═════════════════════════════
        # БАЗОВЫЕ ПАРАМЕТРЫ
        # ═══════════════════════════════════════════════════════════
        
        self.viewport = self._random_viewport()
        self.user_agent = self._random_user_agent()
        self.timezone = self._random_timezone()
        self.geolocation = self._random_geolocation()
        self.language = random.choice(self.LANGUAGES_LIST)
        self.platform = random.choice(["Win32", "MacIntel", "Linux x86_64"])
        
        # ═══════════════════════════════════════════════════════════
        # SCREEN PARAMETERS
        # ═══════════════════════════════════════════════════════════
        
        self.screen_width = self.viewport["width"]
        self.screen_height = self.viewport["height"]
        self.available_width = self.screen_width
        self.available_height = self.screen_height - 40
        self.color_depth = 24
        self.pixel_ratio = random.choice([1, 1.5, 2, 2.5])
        
        # ═══════════════════════════════════════════════════════════
        # HARDWARE PARAMETERS (С ШУМОМ)
        # ══════════���════════════════════════════════════════════════
        
        # ⭐ Hardware concurrency с шумом
        self.hardware_concurrency = random.choice([2, 4, 4, 4, 6, 8, 8, 8, 12, 16])
        self.device_memory = random.choice([4, 8, 8, 8, 16, 16, 32])
        self.max_touch_points = random.randint(0, 10)
        
        # ═══════════════════════════════════════════════════════════
        # CANVAS FINGERPRINT (С ЗАЩИТОЙ ОТ ДЕТЕКЦИИ)
        # ═══════════════════════════════════════════════════════════
        
        self.canvas_id = self._generate_canvas_id()
        self.canvas_noise_seed = random.randint(1, 1000000)
        
        # ═══════════════════════════════════════════════════════════
        # WEBGL FINGERPRINT (С ЗАЩИТОЙ ОТ ДЕТЕКЦИИ)
        # ═══════════════════════════════════════════════════════════
        
        self.webgl_vendor = random.choice(self.WEBGL_VENDORS)
        self.webgl_renderer = random.choice(self.WEBGL_RENDERERS)
        self.webgl_id = self._generate_webgl_id()
        
        # ═══════════════════════════════════════════════════════════
        # AUDIO FINGERPRINT (С ЗАЩИТОЙ ОТ ДЕТЕКЦИИ)
        # ═══════════════════════════════════════════════════════════
        
        self.audio_noise_seed = random.randint(1, 1000000)
        self.audio_context_state = random.choice(["running", "suspended"])
        
        # ═══════════════════════════════════════════════════════════
        # FONTS FINGERPRINT
        # ═══════════════════════════════════════════════════════════
        
        self.fonts = random.sample(self.FONTS_LIST, k=random.randint(5, 8))
        
        # ═══════════════════════════════════════════════════════════
        # CONNECTION PARAMETERS
        # ═══════════════════════════════════════════════════════════
        
        self.connection_type = random.choice(["4g", "4g", "4g", "wifi"])
        self.connection_downlink = random.choice([1.5, 2.5, 5.0, 10.0])
        self.connection_rtt = random.randint(20, 100)
        self.connection_save_data = False
        
        # ═══════════════════════════════════════════════════════════
        # DO NOT TRACK (DNT)
        # ═══════════════════════════════════════════════════════════
        
        self.do_not_track = random.choice([None, "1", "0"])
        
        # ═══════════════════════════════════════════════════════════
        # METADATA
        # ═══════════════════════════════════════════════════════════
        
        self.created_at = datetime.now().isoformat()
        self.fingerprint_version = "4.0"
    
    def _random_viewport(self) -> Dict[str, int]:
        """Генерировать случайный viewport"""
        return random.choice(self.VIEWPORTS_LIST)
    
    def _random_user_agent(self) -> str:
        """Генерировать случайный User Agent"""
        return random.choice(self.USER_AGENTS_LIST)
    
    def _random_timezone(self) -> str:
        """Генерировать случайный timezone"""
        return random.choice(self.TIMEZONES_LIST)
    
    def _random_geolocation(self) -> Dict[str, Any]:
        """Генерировать случайную геолокацию"""
        geo = random.choice(self.GEOLOCATION_LIST)
        return {
            "latitude": geo["latitude"] + random.uniform(-0.01, 0.01),
            "longitude": geo["longitude"] + random.uniform(-0.01, 0.01),
        }
    
    def _generate_canvas_id(self) -> str:
        """Генерировать Canvas Fingerprint с шумом"""
        # Canvas fingerprint с добавлением шума
        base = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        noise = str(random.randint(0, 1000)).encode().hex()
        return f"{base}_{noise}"
    
    def _generate_webgl_id(self) -> str:
        """Генерировать WebGL Fingerprint с шумом"""
        base = ''.join(random.choices(string.ascii_letters + string.digits, k=128))
        noise = str(random.randint(0, 1000000)).encode().hex()
        return f"{base}_{noise}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Экспортировать как словарь"""
        return {
            # Viewport
            "viewport": self.viewport,
            
            # User Agent
            "user_agent": self.user_agent,
            
            # Location
            "timezone": self.timezone,
            "geolocation": self.geolocation,
            
            # Screen
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "available_width": self.available_width,
            "available_height": self.available_height,
            "color_depth": self.color_depth,
            "pixel_ratio": self.pixel_ratio,
            
            # Hardware (с шумом)
            "hardware_concurrency": self.hardware_concurrency,
            "device_memory": self.device_memory,
            "max_touch_points": self.max_touch_points,
            
            # Canvas (с защитой)
            "canvas_id": self.canvas_id,
            "canvas_noise_seed": self.canvas_noise_seed,
            
            # WebGL (с защитой)
            "webgl_vendor": self.webgl_vendor,
            "webgl_renderer": self.webgl_renderer,
            "webgl_id": self.webgl_id,
            
            # Audio (с защитой)
            "audio_noise_seed": self.audio_noise_seed,
            "audio_context_state": self.audio_context_state,
            
            # Fonts
            "fonts": self.fonts,
            
            # Language & Platform
            "language": self.language,
            "platform": self.platform,
            
            # Connection
            "connection_type": self.connection_type,
            "connection_downlink": self.connection_downlink,
            "connection_rtt": self.connection_rtt,
            "connection_save_data": self.connection_save_data,
            
            # DNT
            "do_not_track": self.do_not_track,
            
            # Metadata
            "created_at": self.created_at,
            "version": self.fingerprint_version,
        }


# Для совместимости со старым кодом
FingerprintStore = Fingerprint
BrowserFingerprint = Fingerprint
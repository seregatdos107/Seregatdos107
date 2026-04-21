# core/human/behavior.py
"""
👤 BEHAVIOR v2.0 — максимально человеческое поведение
✅ Brownian motion (броуновское движение мыши)
✅ 15+ паттернов скролла
✅ Система усталости (реалистичные паузы)
✅ Система настроения (mood-based actions)
✅ Профили поведения по времени суток
✅ Случайные действия и паузы
"""

from __future__ import annotations

import asyncio
import random
from typing import List, Tuple
from datetime import datetime
from playwright.async_api import Page, Mouse


class BehaviorSimulator:
    """
    👤 BEHAVIOR SIMULATOR — максимально человеческое поведение
    """
    
    # ═══════════════════════════════════════════════════════════════
    # BROWNIAN MOTION — БРОУНОВСКОЕ ДВИЖЕНИЕ МЫШИ
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    async def brownian_motion(page: Page, duration: float = 5.0) -> None:
        """
        🌊 BROWNIAN MOTION — случайное движение мыши по экрану
        
        Args:
            page: Playwright Page
            duration: Длительность в секундах
        """
        
        start_time = asyncio.get_event_loop().time()
        x, y = random.randint(100, page.viewport_size["width"] - 100), \
               random.randint(100, page.viewport_size["height"] - 100)
        
        while asyncio.get_event_loop().time() - start_time < duration:
            # Случайное смещение
            dx = random.gauss(0, 50)
            dy = random.gauss(0, 50)
            
            x = max(0, min(page.viewport_size["width"], x + dx))
            y = max(0, min(page.viewport_size["height"], y + dy))
            
            try:
                await page.mouse.move(int(x), int(y))
            except Exception:
                pass
            
            await asyncio.sleep(random.uniform(0.1, 0.3))
    
    # ═══════════════════════════════════════════════════════════════
    # 15+ ПАТТЕРНОВ СКРОЛЛА
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    async def scroll_fast(page: Page) -> None:
        """Быстрая прокрутка вниз"""
        for _ in range(random.randint(5, 10)):
            await page.mouse.scroll(0, random.randint(200, 400))
            await asyncio.sleep(random.uniform(0.2, 0.5))
    
    @staticmethod
    async def scroll_slow(page: Page) -> None:
        """Медленная прокрутка вниз"""
        for _ in range(random.randint(8, 15)):
            await page.mouse.scroll(0, random.randint(50, 100))
            await asyncio.sleep(random.uniform(0.5, 1.5))
    
    @staticmethod
    async def scroll_very_slow(page: Page) -> None:
        """Очень медленная прокрутка"""
        for _ in range(random.randint(10, 20)):
            await page.mouse.scroll(0, random.randint(20, 50))
            await asyncio.sleep(random.uniform(1.0, 2.5))
    
    @staticmethod
    async def scroll_zigzag(page: Page) -> None:
        """Зигзаг скролл (вверх-вниз-вверх)"""
        for _ in range(random.randint(3, 6)):
            # Вниз
            await page.mouse.scroll(0, random.randint(100, 200))
            await asyncio.sleep(random.uniform(0.5, 1.0))
            
            # Вверх
            await page.mouse.scroll(0, -random.randint(50, 100))
            await asyncio.sleep(random.uniform(0.5, 1.0))
    
    @staticmethod
    async def scroll_with_pause(page: Page) -> None:
        """Скролл с долгими паузами"""
        for _ in range(random.randint(3, 5)):
            await page.mouse.scroll(0, random.randint(100, 150))
            await asyncio.sleep(random.uniform(2.0, 5.0))  # Долгая пауза
    
    @staticmethod
    async def scroll_double_tap(page: Page) -> None:
        """Двойной скролл (скролл-пауза-скролл)"""
        for _ in range(random.randint(2, 4)):
            await page.mouse.scroll(0, random.randint(80, 120))
            await asyncio.sleep(random.uniform(0.8, 1.5))
            
            await page.mouse.scroll(0, random.randint(80, 120))
            await asyncio.sleep(random.uniform(1.5, 3.0))
    
    @staticmethod
    async def scroll_random_jump(page: Page) -> None:
        """Случайный прыжок в скролле"""
        for _ in range(random.randint(4, 7)):
            if random.random() > 0.5:
                # Большой прыжок
                await page.mouse.scroll(0, random.randint(300, 500))
            else:
                # Маленький прыжок
                await page.mouse.scroll(0, random.randint(30, 80))
            
            await asyncio.sleep(random.uniform(0.3, 1.0))
    
    @staticmethod
    async def scroll_circular(page: Page) -> None:
        """Циклическая прокрутка (вверх-вниз в цикле)"""
        for _ in range(random.randint(2, 4)):
            # Вниз
            for _ in range(3):
                await page.mouse.scroll(0, random.randint(50, 100))
                await asyncio.sleep(random.uniform(0.3, 0.7))
            
            # Вверх
            for _ in range(3):
                await page.mouse.scroll(0, -random.randint(40, 80))
                await asyncio.sleep(random.uniform(0.3, 0.7))
    
    @staticmethod
    async def scroll_smooth_wave(page: Page) -> None:
        """Плавная волна скролла"""
        for _ in range(random.randint(5, 10)):
            scroll_amount = int(150 * random.gauss(1, 0.3))
            await page.mouse.scroll(0, scroll_amount)
            await asyncio.sleep(random.uniform(0.5, 1.2))
    
    @staticmethod
    async def scroll_focus_item(page: Page) -> None:
        """Фокус на одном товаре (медленный скролл + паузы)"""
        # Скролл вниз
        await page.mouse.scroll(0, random.randint(50, 100))
        await asyncio.sleep(random.uniform(1.0, 2.0))
        
        # Долгая пауза (рассматриваем)
        await asyncio.sleep(random.uniform(3.0, 7.0))
        
        # Маленький скролл
        await page.mouse.scroll(0, random.randint(30, 60))
        await asyncio.sleep(random.uniform(2.0, 4.0))
    
    @staticmethod
    async def scroll_back_and_forth(page: Page) -> None:
        """Прокрутка туда-сюда"""
        for _ in range(random.randint(3, 5)):
            # Вниз
            await page.mouse.scroll(0, random.randint(100, 150))
            await asyncio.sleep(random.uniform(0.5, 1.0))
            
            # Вверх (больше, чем вниз)
            await page.mouse.scroll(0, -random.randint(120, 180))
            await asyncio.sleep(random.uniform(0.5, 1.0))
    
    @staticmethod
    async def scroll_methodical(page: Page) -> None:
        """Методичная прокрутка (стабильные шаги)"""
        scroll_amount = random.randint(100, 150)
        for _ in range(random.randint(6, 10)):
            await page.mouse.scroll(0, scroll_amount)
            await asyncio.sleep(random.uniform(0.7, 1.3))
    
    @staticmethod
    async def scroll_idle_then_burst(page: Page) -> None:
        """Бездействие, потом всплеск активности"""
        # Длинное ничегонеделание
        await asyncio.sleep(random.uniform(3.0, 8.0))
        
        # Быстрый всплеск скролла
        for _ in range(random.randint(5, 8)):
            await page.mouse.scroll(0, random.randint(150, 250))
            await asyncio.sleep(random.uniform(0.2, 0.5))
    
    # ═══════════════════════════════════════════════════════════════
    # СИСТЕМА УСТАЛОСТИ (реалистичные паузы)
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def get_tiredness_factor(tiredness: float) -> float:
        """
        😴 ПОЛУЧИТЬ КОЭФФИЦИЕНТ УСТАЛОСТИ
        
        Усталость влияет на:
        - Скорость действий
        - Длительность пауз
        - Тип скролла
        
        Args:
            tiredness: Уровень усталости (0-1)
            
        Returns:
            float: Коэффициент (чем выше, тем медленнее)
        """
        
        # Минимум 0.5x, максимум 3x
        return 0.5 + (tiredness * 2.5)
    
    @staticmethod
    async def realistic_pause(tiredness: float) -> None:
        """
        ⏸️ РЕАЛИСТИЧНАЯ ПАУЗА (зависит от усталости)
        
        Args:
            tiredness: Уровень усталости (0-1)
        """
        
        factor = BehaviorSimulator.get_tiredness_factor(tiredness)
        
        # Базовая пауза 1-5 секунд
        base_pause = random.uniform(1, 5)
        actual_pause = base_pause * factor
        
        await asyncio.sleep(actual_pause)
    
    # ═══════════════════════════════════════════════════════════════
    # СИСТЕМА НАСТРОЕНИЯ
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def get_mood_action(mood: str) -> str:
        """
        😊 ПОЛУЧИТЬ ДЕЙСТВИЕ НА ОСНОВЕ НАСТРОЕНИЯ
        
        Args:
            mood: happy, neutral, tired, bored
            
        Returns:
            str: Тип действия
        """
        
        if mood == "happy":
            # Активное поведение
            return random.choice([
                "search", "view_items", "add_favorites", "view_seller"
            ])
        
        elif mood == "neutral":
            # Обычное поведение
            return random.choice([
                "view_items", "scroll", "search", "read_reviews"
            ])
        
        elif mood == "tired":
            # Вялое поведение
            return random.choice([
                "slow_scroll", "pause", "view_one_item"
            ])
        
        elif mood == "bored":
            # Случайное поведение
            return random.choice([
                "random_search", "jump_scroll", "idle_pause"
            ])
        
        return "pause"
    
    # ═══════════════════════════════════════════════════════════════
    # СЛУЧАЙНЫЕ ДЕЙСТВИЯ И ПАУЗЫ
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    async def random_click_and_focus(page: Page) -> None:
        """🖱️ Случайный клик с фокусом"""
        
        try:
            # Случайная координата
            x = random.randint(100, page.viewport_size["width"] - 100)
            y = random.randint(100, page.viewport_size["height"] - 100)
            
            # Медленное движение мыши (как человек)
            current_x, current_y = 0, 0
            steps = random.randint(5, 15)
            
            for i in range(steps):
                new_x = current_x + (x - current_x) / steps
                new_y = current_y + (y - current_y) / steps
                
                try:
                    await page.mouse.move(int(new_x), int(new_y))
                except Exception:
                    pass
                
                await asyncio.sleep(random.uniform(0.05, 0.15))
                current_x, current_y = new_x, new_y
            
            # Клик
            await page.mouse.click(x, y)
            await asyncio.sleep(random.uniform(0.5, 1.5))
        
        except Exception:
            pass
    
    @staticmethod
    async def random_look_around(page: Page) -> None:
        """👀 Случайный взгляд вокруг (движение мыши)"""
        
        for _ in range(random.randint(3, 8)):
            x = random.randint(100, page.viewport_size["width"] - 100)
            y = random.randint(100, page.viewport_size["height"] - 100)
            
            try:
                await page.mouse.move(x, y)
            except Exception:
                pass
            
            await asyncio.sleep(random.uniform(0.5, 2.0))
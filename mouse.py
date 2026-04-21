# core/human/mouse.py
"""
🖱️ MOUSE ENGINE 2030 v2.0 - ПОЛНАЯ ПЕРЕДЕЛКА
✅ Броуновское движение
✅ Микро-дрожание (tremor)
✅ Fidgeting (мелкие движения)
✅ Overshoot имитация
✅ Естественное ускорение/замедление
✅ Усталость влияет на качество движения
"""

import asyncio
import random
import math
import time
from typing import Tuple, List, Optional
from enum import Enum

from playwright.async_api import Page
from core.browser.fingerprint import Fingerprint


class MouseMovementStyle(Enum):
    """Стиль движения мыши"""
    PRECISE = "precise"
    FAST = "fast"
    CASUAL = "casual"
    NERVOUS = "nervous"
    TIRED = "tired"


class MouseEngine:
    """🖱️ MOUSE ENGINE 2030 v2.0"""
    
    def __init__(self, fp: Optional[Fingerprint] = None):
        self.fp = fp
        self.last_x = random.randint(150, 1200)
        self.last_y = random.randint(100, 700)
        self.session_start_time = time.time()
        self.movement_style = self._get_movement_style()
        self.total_movements = 0
        self.total_clicks = 0
    
    def _get_movement_style(self) -> MouseMovementStyle:
        """Определить стиль движения мыши"""
        styles = list(MouseMovementStyle)
        return random.choice(styles)
    
    def get_tiredness(self) -> float:
        """Получить уровень усталости (0-1)"""
        elapsed_hours = (time.time() - self.session_start_time) / 3600
        return min(1.0, elapsed_hours / 8.0)
    
    def _get_mouse_speed_multiplier(self) -> float:
        """Получить множитель скорости мыши"""
        multipliers = {
            MouseMovementStyle.PRECISE: 0.5,
            MouseMovementStyle.FAST: 2.0,
            MouseMovementStyle.CASUAL: 1.0,
            MouseMovementStyle.NERVOUS: 1.3,
            MouseMovementStyle.TIRED: 0.7,
        }
        
        base_mult = multipliers.get(self.movement_style, 1.0)
        tiredness = self.get_tiredness()
        base_mult *= (1.0 - tiredness * 0.3)
        
        return base_mult
    
    def _get_tremor_intensity(self) -> float:
        """Получить интенсивность дрожания"""
        intensities = {
            MouseMovementStyle.PRECISE: 0.3,
            MouseMovementStyle.FAST: 0.8,
            MouseMovementStyle.CASUAL: 0.5,
            MouseMovementStyle.NERVOUS: 1.5,
            MouseMovementStyle.TIRED: 1.2,
        }
        
        intensity = intensities.get(self.movement_style, 0.5)
        tiredness = self.get_tiredness()
        intensity *= (1.0 + tiredness * 0.8)
        
        return intensity


def _brownian_motion(
    start: Tuple[float, float],
    end: Tuple[float, float],
    num_points: int = 50,
    deviation: float = 0.0
) -> List[Tuple[int, int]]:
    """Броуновское движение"""
    
    x0, y0 = start
    x_end, y_end = end
    
    points = []
    current_x, current_y = x0, y0
    
    dx = (x_end - x0) / num_points
    dy = (y_end - y0) / num_points
    
    for i in range(num_points + 1):
        target_x = x0 + dx * i
        target_y = y0 + dy * i
        
        random_deviation_x = random.gauss(0, deviation * (x_end - x0) / 100)
        random_deviation_y = random.gauss(0, deviation * (y_end - y0) / 100)
        
        current_x = target_x + random_deviation_x
        current_y = target_y + random_deviation_y
        
        points.append((int(current_x), int(current_y)))
    
    return points


def _bezier_curve(
    start: Tuple[float, float],
    end: Tuple[float, float],
    num_points: int = 50,
    fatigue: float = 0.0,
    deviation: float = 0.2
) -> List[Tuple[int, int]]:
    """Кривая Безье для гладкого движения"""
    
    x0, y0 = start
    x3, y3 = end
    
    dist = math.sqrt((x3 - x0) ** 2 + (y3 - y0) ** 2)
    offset = dist * (0.15 + deviation) * (1 + fatigue * 0.8)
    
    x1 = x0 + (x3 - x0) * random.uniform(0.15, 0.35) + random.uniform(-offset, offset)
    y1 = y0 + (y3 - y0) * random.uniform(0.05, 0.35) + random.uniform(-offset, offset)
    
    x2 = x0 + (x3 - x0) * random.uniform(0.65, 0.85) + random.uniform(-offset, offset)
    y2 = y0 + (y3 - y0) * random.uniform(0.65, 0.95) + random.uniform(-offset, offset)
    
    points = []
    for i in range(num_points + 1):
        t = i / num_points
        
        x = (1 - t)**3 * x0 + 3*(1 - t)**2 * t * x1 + 3*(1 - t)*t**2 * x2 + t**3 * x3
        y = (1 - t)**3 * y0 + 3*(1 - t)**2 * t * y1 + 3*(1 - t)*t**2 * y2 + t**3 * y3
        
        jitter = random.uniform(-1.5, 1.5)
        points.append((int(x + jitter), int(y + jitter)))
    
    return points


async def move_mouse(
    page: Page,
    target_x: int,
    target_y: int,
    fp: Optional[Fingerprint] = None,
    duration: Optional[float] = None,
    allow_overshoot: bool = True,
    fidget: bool = True,
) -> None:
    """МАКСИМАЛЬНО РЕАЛИСТИЧНОЕ ДВИЖЕНИЕ МЫШИ"""
    
    engine = getattr(page, "_mouse_engine", None)
    if not engine:
        engine = MouseEngine(fp)
        page._mouse_engine = engine
    
    engine.total_movements += 1
    
    try:
        # Получение текущей позиции
        try:
            current = await page.evaluate("() => ({x: window._mouseX || 0, y: window._mouseY || 0})")
            start_x, start_y = current.get("x", engine.last_x), current.get("y", engine.last_y)
        except:
            start_x, start_y = engine.last_x, engine.last_y
        
        # Расчет пути
        dist = math.sqrt((target_x - start_x) ** 2 + (target_y - start_y) ** 2)
        num_points = max(25, min(100, int(dist / 5)))
        
        # Выбираем тип кривой
        if dist < 20:
            path = [(start_x + (target_x - start_x) * i / num_points,
                     start_y + (target_y - start_y) * i / num_points)
                    for i in range(num_points + 1)]
            path = [(int(x), int(y)) for x, y in path]
        else:
            fatigue = engine.get_tiredness()
            path = _bezier_curve(
                (start_x, start_y),
                (target_x, target_y),
                num_points=num_points,
                fatigue=fatigue,
                deviation=0.2
            )
        
        # Расчет длительности
        if duration is None:
            base_duration = (dist / 400) * (1 + engine.get_tiredness() * 0.5)
            duration = base_duration * engine._get_mouse_speed_multiplier()
        
        step_duration = duration / len(path)
        
        # Движение по пути
        for i, (x, y) in enumerate(path):
            tremor = engine._get_tremor_intensity()
            jitter_x = x + random.gauss(0, tremor)
            jitter_y = y + random.gauss(0, tremor)
            
            await page.mouse.move(int(jitter_x), int(jitter_y))
            
            t = i / len(path)
            ease_out = t ** 2
            delay = step_duration * (0.3 + ease_out * 0.7)
            
            await asyncio.sleep(delay / 1000.0)
        
        # Overshoot
        if allow_overshoot and random.random() < (0.2 + engine.get_tiredness() * 0.2):
            overshoot_x = target_x + random.randint(-20, 20)
            overshoot_y = target_y + random.randint(-20, 20)
            
            await page.mouse.move(overshoot_x, overshoot_y)
            await asyncio.sleep(random.uniform(0.04, 0.08))
            
            await page.mouse.move(target_x, target_y)
            await asyncio.sleep(random.uniform(0.02, 0.04))
        
        # Fidgeting
        if fidget and random.random() < 0.15:
            for _ in range(random.randint(1, 3)):
                fidget_x = target_x + random.randint(-3, 3)
                fidget_y = target_y + random.randint(-3, 3)
                
                await page.mouse.move(fidget_x, fidget_y)
                await asyncio.sleep(random.uniform(0.05, 0.1))
        
        engine.last_x, engine.last_y = target_x, target_y
    
    except Exception:
        pass
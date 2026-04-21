# core/safety/risk_analyzer.py
"""
⚠️ RISK ANALYZER v2.0 — анализ риска блокировок
✅ Анализ паттернов поведения
✅ Обнаружение подозрительной активности
✅ Оценка риска (0-100)
"""

from __future__ import annotations

from typing import Dict, Optional
from services.logger import Logger


class RiskAnalyzer:
    """
    ⚠️ RISK ANALYZER — анализ риска блокировок
    """
    
    def __init__(self, logger: Logger):
        """Инициализация"""
        
        self.logger = logger
        self.risk_scores: Dict[str, float] = {}
    
    def calculate_risk(
        self,
        acc_id: str,
        factors: Dict[str, float]
    ) -> float:
        """
        📊 РАССЧИТАТЬ РИСК (0-100)
        
        Учитывает факторы:
        - Количество ошибок
        - Скорость действий
        - Капча
        - IP блокировки
        - Паттерны поведения
        
        Args:
            acc_id: ID аккаунта
            factors: Словарь с факторами
            
        Returns:
            float: Risk score (0-100)
        """
        
        risk = 0.0
        
        # Ошибки (max 30)
        error_factor = factors.get("errors", 0)
        risk += min(30, error_factor * 5)
        
        # Капча (max 25)
        captcha_factor = factors.get("captcha_count", 0)
        risk += min(25, captcha_factor * 8)
        
        # IP блокировки (max 20)
        ip_block_factor = factors.get("ip_blocks", 0)
        risk += min(20, ip_block_factor * 10)
        
        # Rate limiting (max 15)
        rate_limit_factor = factors.get("rate_limits", 0)
        risk += min(15, rate_limit_factor * 3)
        
        # Неестественные паттерны (max 10)
        pattern_factor = factors.get("unnatural_patterns", 0)
        risk += min(10, pattern_factor * 10)
        
        # Максимум 100
        risk = min(100.0, risk)
        
        self.risk_scores[acc_id] = risk
        
        return risk
    
    def get_risk_color(self, risk_score: float) -> str:
        """
        🎨 ПОЛУЧИТЬ ЦВЕТ РИСКА
        
        Args:
            risk_score: Risk score (0-100)
            
        Returns:
            str: Emoji и описание
        """
        
        if risk_score < 20:
            return "🟢 Low"
        elif risk_score < 40:
            return "🟡 Medium"
        elif risk_score < 70:
            return "🟠 High"
        else:
            return "🔴 Critical"
    
    def should_pause(self, risk_score: float) -> bool:
        """
        ⏸️ НУЖНА ЛИ ПАУЗА?
        
        Args:
            risk_score: Risk score (0-100)
            
        Returns:
            bool: True если нужна пауза
        """
        
        return risk_score > 60
    
    def should_slow_down(self, risk_score: float) -> bool:
        """
        🐢 НУЖНО ЛИ ЗАМЕДЛЯТЬСЯ?
        
        Args:
            risk_score: Risk score (0-100)
            
        Returns:
            bool: True если нужно замедляться
        """
        
        return risk_score > 40
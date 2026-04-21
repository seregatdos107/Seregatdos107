# core/avito/detector.py
"""
🔍 DETECTOR v2.0 — обнаружение угроз (капча, CloudFlare, IP блокировка)
✅ Обнаружение капчи
✅ Обнаружение CloudFlare
✅ Обнаружение IP блокировки
✅ Обнаружение бан-листов
"""

from __future__ import annotations

from typing import Optional
from playwright.async_api import Page

from core.avito.selectors import ThreatType, ThreatInfo


async def check_threats(page: Page) -> Optional[ThreatInfo]:
    """
    🔍 ПРОВЕРИТЬ УГРОЗЫ
    
    Args:
        page: Playwright Page
        
    Returns:
        ThreatInfo или None если нет угроз
    """
    
    try:
        page_content = await page.content()
        page_text = await page.evaluate("() => document.body.innerText")
        url = page.url
        
        # ─────────────────────────────────────────────────────
        # КАПЧА
        # ─────────────────────────────────────────────────────
        
        captcha_patterns = [
            "captcha",
            "recaptcha",
            "verification",
            "подтвердите",
            "robozapros",
            "перейти капча",
        ]
        
        for pattern in captcha_patterns:
            if pattern.lower() in page_text.lower():
                return ThreatInfo(
                    threat_type=ThreatType.CAPTCHA,
                    message="CAPTCHA detected on page",
                    is_safe=False,
                    score=80
                )
        
        # ─────────────────────────────────────────────────────
        # CLOUDFLARE
        # ─────────────────────────────────────────────────────
        
        cloudflare_patterns = [
            "Just a moment",
            "Checking your browser",
            "Enable JavaScript",
            "cloudflare",
            "Challenge passed",
            "cf_clearance",
        ]
        
        for pattern in cloudflare_patterns:
            if pattern in page_text or pattern in page_content:
                return ThreatInfo(
                    threat_type=ThreatType.CLOUDFLARE,
                    message="CloudFlare protection detected",
                    is_safe=False,
                    score=70
                )
        
        # ─────────────────────────────────────────────────────
        # IP БЛОКИРОВКА
        # ─────────────────────────────────────────────────────
        
        ip_block_patterns = [
            "access denied",
            "403 forbidden",
            "ip blocked",
            "your ip",
            "заблокирован",
            "доступ запрещён",
            "access restricted",
        ]
        
        for pattern in ip_block_patterns:
            if pattern.lower() in page_text.lower():
                return ThreatInfo(
                    threat_type=ThreatType.IP_BLOCKED,
                    message="IP blocked or access denied",
                    is_safe=False,
                    score=90
                )
        
        # ─────────────────────────────────────────────────────
        # RATE LIMIT
        # ─────────────────────────────────────────────────────
        
        rate_limit_patterns = [
            "too many requests",
            "too fast",
            "slow down",
            "429",
            "rate limit",
        ]
        
        for pattern in rate_limit_patterns:
            if pattern.lower() in page_text.lower():
                return ThreatInfo(
                    threat_type=ThreatType.RATE_LIMIT,
                    message="Rate limit exceeded",
                    is_safe=False,
                    score=60
                )
        
        # ─────────────────────────────────────────────────────
        # БОТ ДЕТЕКЦИЯ
        # ─────────────────────────────────────────────────────
        
        bot_detection_patterns = [
            "bot",
            "automated",
                "автоматизированн",
            "script",
            "robot",
        ]
        
        for pattern in bot_detection_patterns:
            if pattern.lower() in page_text.lower() and "captcha" not in page_text.lower():
                return ThreatInfo(
                    threat_type=ThreatType.BOT_DETECTED,
                    message="Bot detection suspected",
                    is_safe=False,
                    score=50
                )
        
        # ─────────────────────────────────────────────────────
        # БЕЗ УГРОЗ
        # ─────────────────────────────────────────────────────
        
        return ThreatInfo(
            threat_type=ThreatType.UNKNOWN,
            message="No threats detected",
            is_safe=True,
            score=0
        )
    
    except Exception as e:
        return ThreatInfo(
            threat_type=ThreatType.UNKNOWN,
            message=f"Error checking threats: {e}",
            is_safe=True,
            score=10
        )
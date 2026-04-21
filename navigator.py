# core/avito/navigator.py
"""
🚀 NAVIGATOR v6.2 — ПОЛНОСТЬЮ ИСПРАВЛЕН ДЛЯ AVITO 2026
✅ Таймаут 120 секунд
✅ Кнопка "Найти" надёжно нажимается
✅ Улучшенный клик на карточки
✅ Работает с медленными прокси и "Не защищено"
✅ Полная совместимость с Warmup Engine 2031
"""

import asyncio
import random
from typing import Optional, List
from datetime import datetime
from playwright.async_api import Page

from core.avito.detector import check_threats, ThreatInfo
from core.avito.selectors import AvitoUrls, AvitoSelectors
from core.human.mouse import move_mouse


class AvitoNavigator:
    """🚀 NAVIGATOR v6.2 — ПОЛНАЯ ПЕРЕДЕЛКА"""

    def __init__(self, logger):
        self.logger = logger
        self.last_navigation_time = datetime.now()
        self.navigation_history: List[str] = []
        self.click_stats = {
            "total_clicks": 0,
            "successful_clicks": 0,
            "failed_clicks": 0,
        }

    # ═══════════════════════════════════════════════════════════════
    # НАВИГАЦИЯ
    # ═══════════════════════════════════════════════════════════════

    async def goto_main(self, page: Page, account_id: str = "system") -> bool:
        try:
            self.logger.info(account_id, "🏠 Going to Avito main page...")
            threat = await self.goto(page, AvitoUrls.MAIN, account_id=account_id, attempts=5, timeout_ms=120000)
            return threat is not None
        except Exception as e:
            self.logger.error(account_id, f"goto_main error: {e}")
            return False

    async def goto_login(self, page: Page, account_id: str = "system") -> bool:
        try:
            self.logger.info(account_id, "🔐 Going to Avito login page...")
            threat = await self.goto(page, AvitoUrls.LOGIN, account_id=account_id, attempts=4, timeout_ms=90000)
            return threat is not None
        except Exception as e:
            self.logger.error(account_id, f"goto_login error: {e}")
            return False

    async def goto(
        self,
        page: Page,
        url: str,
        account_id: str = "system",
        attempts: int = 5,
        timeout_ms: int = 120000,
        wait_until: str = "domcontentloaded",
    ) -> Optional[ThreatInfo]:
        for attempt in range(1, attempts + 1):
            try:
                self.logger.info(account_id, f"🌐 [{attempt}/{attempts}] {url[:60]}")
                await page.goto(url, wait_until=wait_until, timeout=timeout_ms)
                await asyncio.sleep(random.uniform(4, 7))

                if await self._verify_page_loaded(page, account_id, url):
                    threat = await check_threats(page)
                    self.logger.success(account_id, f"✅ Loaded successfully")
                    return threat

                if attempt < attempts:
                    await asyncio.sleep(random.uniform(10, 18))
            except Exception as e:
                self.logger.warning(account_id, f"⚠️ Attempt {attempt} failed")
                if attempt < attempts:
                    await asyncio.sleep(random.uniform(8, 15))
        return None

    async def _verify_page_loaded(self, page: Page, account_id: str, url: str) -> bool:
        try:
            content = await page.content()
            return len(content) > 500 and "html" in content.lower()
        except:
            return False

    # ═══════════════════════════════════════════════════════════════
    # ПОИСК (САМОЕ ВАЖНОЕ ИСПРАВЛЕНИЕ)
    # ═══════════════════════════════════════════════════════════════

    async def search(self, page: Page, query: str, account_id: str = "system") -> bool:
        """
        🔍 ПОИСК — МАКСИМАЛЬНО НАДЁЖНЫЙ (КНОПКА "НАЙТИ" + ENTER FALLBACK)
        """
        try:
            await asyncio.sleep(random.uniform(1.0, 1.8))

            # 1. Находим поле поиска
            search_input = None
            for selector in AvitoSelectors.SEARCH_INPUT_PRIMARY:
                try:
                    loc = page.locator(selector)
                    if await loc.count() > 0 and await loc.first.is_visible(timeout=4000):
                        search_input = loc.first
                        break
                except:
                    continue

            if not search_input:
                self.logger.warning(account_id, "⚠️ Поле поиска не найдено")
                return False

            # 2. Кликаем и вводим текст
            await search_input.scroll_into_view_if_needed()
            await search_input.click(timeout=7000)
            await asyncio.sleep(random.uniform(0.4, 0.8))
            await search_input.clear()
            await asyncio.sleep(0.3)

            for char in query:
                await search_input.type(char, delay=random.uniform(70, 160))

            await asyncio.sleep(random.uniform(1.0, 1.8))

            # 3. Пытаемся нажать кнопку "Найти"
            button_clicked = False
            for selector in AvitoSelectors.SEARCH_SUBMIT_PRIMARY:
                try:
                    btn = page.locator(selector)
                    if await btn.count() > 0 and await btn.first.is_visible(timeout=3000):
                        await btn.first.scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)
                        await btn.first.click(timeout=6000)
                        button_clicked = True
                        self.logger.success(account_id, "✅ Нажата кнопка 'Найти'")
                        break
                except:
                    continue

            # 4. Если кнопку не нашли — жмём Enter
            if not button_clicked:
                try:
                    await search_input.press("Enter")
                    self.logger.info(account_id, "✅ Нажат Enter")
                except:
                    pass

            await asyncio.sleep(random.uniform(4, 6))

            # 5. Ждём результаты
            try:
                await page.locator('[data-marker="catalog-list"]').first.wait_for(timeout=18000)
                self.logger.success(account_id, f"✅ Поиск выполнен: '{query}'")
                return True
            except:
                self.logger.warning(account_id, "⚠️ Результаты поиска не появились")
                return False

        except Exception as e:
            self.logger.error(account_id, f"Search error: {str(e)[:80]}")
            return False

    # ═══════════════════════════════════════════════════════════════
    # КЛИК НА КАРТОЧКИ (УЛУЧШЕННЫЙ)
    # ═══════════════════════════════════════════════════════════════

    async def click_listing(self, page: Page, index: int = 0, account_id: str = "system") -> bool:
        try:
            await asyncio.sleep(random.uniform(0.8, 1.5))

            # Ждём появления карточек
            for _ in range(7):
                count = await page.locator('div[data-marker="item"]').count()
                if count > index:
                    break
                await page.evaluate("window.scrollBy(0, 350)")
                await asyncio.sleep(1.3)

            items = page.locator('div[data-marker="item"]')
            if await items.count() <= index:
                self.logger.warning(account_id, f"⚠️ Карточек меньше чем {index+1}")
                return False

            item = items.nth(index)
            await item.scroll_into_view_if_needed()
            await asyncio.sleep(random.uniform(0.6, 1.3))

            # Ищем ссылку
            link = item.locator('a[href*="/items/"], a[data-marker*="item-title"]')
            target = link.first if await link.count() > 0 else item

            await target.click(timeout=8000)
            await page.wait_for_load_state("domcontentloaded", timeout=25000)
            await asyncio.sleep(random.uniform(2, 3.5))

            self.logger.success(account_id, f"✅ Карточка #{index+1} открыта")
            return True

        except Exception as e:
            self.logger.warning(account_id, f"⚠️ Не удалось открыть карточку #{index+1}")
            return False

    # ═══════════════════════════════════════════════════════════════
    # ОСТАЛЬНЫЕ МЕТОДЫ
    # ═══════════════════════════════════════════════════════════════

    async def go_back(self, page: Page, account_id: str = "system") -> bool:
        try:
            await page.go_back(timeout=20000)
            await asyncio.sleep(random.uniform(1.5, 2.5))
            return True
        except:
            return False

    async def scroll_page(self, page: Page, distance: int = 300, account_id: str = "system") -> bool:
        try:
            await page.evaluate(f"window.scrollBy(0, {distance})")
            await asyncio.sleep(random.uniform(0.5, 1.5))
            return True
        except:
            return False

    async def add_to_favorites(self, page: Page, account_id: str = "system") -> bool:
        try:
            for selector in AvitoSelectors.FAVORITES_BUTTON:
                try:
                    btn = page.locator(selector)
                    if await btn.count() > 0 and await btn.first.is_visible(timeout=2000):
                        await btn.first.click(timeout=5000)
                        await asyncio.sleep(random.uniform(0.5, 1.0))
                        return True
                except:
                    continue
            return False
        except:
            return False

    async def view_seller_profile(self, page: Page, account_id: str = "system") -> bool:
        try:
            for selector in AvitoSelectors.SELLER_LINK:
                try:
                    link = page.locator(selector)
                    if await link.count() > 0:
                        await link.first.click(timeout=5000)
                        await asyncio.sleep(random.uniform(2, 4))
                        return True
                except:
                    continue
            return False
        except:
            return False

    async def is_logged_in(self, page: Page, account_id: str = "system") -> bool:
        try:
            if "login" in page.url.lower():
                return False
            for selector in ['[data-marker="header/profile"]', 'a[href*="/user/"]']:
                if await page.locator(selector).count() > 0:
                    return True
            return False
        except:
            return False
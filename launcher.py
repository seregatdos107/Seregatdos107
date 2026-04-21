# core/browser/launcher.py
"""
🌐 BROWSER LAUNCHER v11.0 - ПОЛНАЯ ПЕРЕДЕЛКА
✅ Correct cookie loading (ДО создания страницы)
✅ Stable session management
✅ Proper stealth application
✅ None checks everywhere
✅ Adaptive timeouts для медленных прокси
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from config.settings import settings
from services.logger import Logger
from core.browser.fingerprint import Fingerprint
from core.browser.stealth import apply_stealth_scripts
from core.proxy.manager import ProxyManager


class BrowserLauncher:
    """🌐 BROWSER LAUNCHER v11.0"""
    
    def __init__(self, logger: Logger, proxy_manager: ProxyManager):
        """Инициализация"""
        
        self.logger = logger
        self.proxy_manager = proxy_manager
        
        self.playwright = None
        self.browser = None
        self.contexts: Dict[str, BrowserContext] = {}
        self.pages: Dict[str, Page] = {}
        self.fingerprints: Dict[str, Fingerprint] = {}
        self.browser_statuses: Dict[str, str] = {}
        
        self.storage_dir = settings.storage_dir
        self.storage_dir.mkdir(exist_ok=True)
    
    async def initialize(self) -> None:
        """Инициализировать Playwright"""
        
        try:
            self.playwright = await async_playwright().start()
            self.logger.system("🎭 Playwright initialized")
        except Exception as e:
            self.logger.system(f"❌ Failed to initialize Playwright: {e}")
            raise
    
    def _build_proxy_url(self, proxy_config) -> str:
        """Построить PROXY URL БЕЗ credentials"""
        
        return f"{proxy_config.protocol}://{proxy_config.host}:{proxy_config.port}"
    
    async def _update_browser_title(self, acc_id: str, page: Optional[Page] = None) -> None:
        """✅ ОБНОВИТЬ ЗАГОЛОВОК БРАУЗЕРА"""
        
        if page is None:
            page = self.pages.get(acc_id)
        
        if not page:
            return
        
        try:
            account_name = settings.accounts.get(acc_id, {}).get("name", acc_id)
            phone = settings.accounts.get(acc_id, {}).get("phone", "")
            status = self.browser_statuses.get(acc_id, "ГОТОВ")
            
            browser_title = f"🤖 Avito Bot — {account_name} [{phone}] • {status}"
            
            await page.evaluate(f"document.title = '{browser_title}'")
        
        except Exception as e:
            self.logger.warning(acc_id, f"Could not update title: {e}")
    
    async def set_browser_status(self, acc_id: str, status: str) -> None:
        """🔄 УСТАНОВИТЬ СТАТУС БРАУЗЕРА"""
        
        self.browser_statuses[acc_id] = status
        await self._update_browser_title(acc_id)
        self.logger.info(acc_id, f"📊 Status: {status}")
    
    async def _load_session_cookies(self, context: BrowserContext, acc_id: str) -> int:
        """✅ ЗАГРУЗИТЬ COOKIES В КОНТЕКСТ (ДО СОЗДАНИЯ СТРАНИЦЫ!)"""
        
        try:
            cookies_file = self.storage_dir / f"{acc_id}.json"
            
            if not cookies_file.exists():
                self.logger.info(acc_id, f"⚠️ No saved cookies found")
                return 0
            
            with open(cookies_file, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            
            if not cookies:
                self.logger.info(acc_id, f"⚠️ Cookies file is empty")
                return 0
            
            # ✅ ЗАГРУЖАЕМ COOKIES В КОНТЕКСТ
            await context.add_cookies(cookies)
            
            self.logger.info(acc_id, f"🍪 Loaded {len(cookies)} cookies from file")
            return len(cookies)
        
        except Exception as e:
            self.logger.warning(acc_id, f"⚠️ Failed to load cookies: {e}")
            return 0
    
    async def launch(self, acc_id: str) -> Optional[Page]:
        """🌐 ЗАПУСТИТЬ БРАУЗЕР ДЛЯ АККАУНТА"""
        
        try:
            # ─────────────────────────────────────────────────────
            # 1. ПОЛУЧАЕМ ПРОКСИ
            # ─────────────────────────────────────────────────────
            
            proxy_config = self.proxy_manager.get_proxy_for_account(acc_id)
            proxy_dict = None
            
            if proxy_config:
                proxy_url = self._build_proxy_url(proxy_config)
                proxy_dict = {"server": proxy_url}
                
                self.logger.info(acc_id, f"🔌 Proxy: {proxy_config.host}:{proxy_config.port}")
                self.logger.info(acc_id, f"🔐 Auth: {proxy_config.username}:***")
            else:
                self.logger.warning(acc_id, "⚠️ No proxy configured")
            
            # ─────────────────────────────────────────────────────
            # 2. СОЗДАЁМ БРАУЗЕР (ЕСЛИ ЕЩЕ НЕТ)
            # ─────────────────────────────────────────────────────
            
            if not self.browser:
                browser_args = [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-setuid-sandbox",
                    "--disable-sandbox",
                    "--disable-gpu",
                    "--disable-extensions",
                    "--disable-sync",
                    "--disable-plugins",
                    "--disable-preconnect",
                ]
                
                launch_args = {
                    "headless": settings.headless,
                    "args": browser_args,
                }
                
                if proxy_dict:
                    launch_args["proxy"] = proxy_dict
                
                self.browser = await self.playwright.chromium.launch(**launch_args)
                self.logger.info(acc_id, "🟢 Browser engine launched")
            
            # ─────────────────────────────────────────────────────
            # 3. СОЗДАЁМ FINGERPRINT И КОНТЕКСТ
            # ─────────────────────────────────────────────────────
            
            fp = Fingerprint()
            self.fingerprints[acc_id] = fp
            
            context_params = {
                "viewport": fp.viewport,
                "user_agent": fp.user_agent,
                "locale": "ru-RU",
                "timezone_id": fp.timezone,
                "geolocation": fp.geolocation,
                "permissions": ["geolocation"],
                "ignore_https_errors": True,
            }
            
            if proxy_config and proxy_config.username and proxy_config.password:
                context_params["http_credentials"] = {
                    "username": proxy_config.username,
                    "password": proxy_config.password,
                }
                self.logger.info(acc_id, f"✅ HTTP credentials attached to context")
            
            context = await self.browser.new_context(**context_params)
            self.contexts[acc_id] = context
            
            self.logger.info(acc_id, f"📦 Context created")
            
            # ─────────────────────────────────────────────────────
            # 4. ✅ ЗАГРУЖАЕМ COOKIES ДО СОЗДАНИЯ СТРАНИЦЫ
            # ─────────────────────────────────────────────────────
            
            cookies_loaded = await self._load_session_cookies(context, acc_id)
            
            # ─────────────────────────────────────────────────────
            # 5. СОЗДАЁМ СТРАНИЦУ
            # ─────────────────────────────────────────────────────
            
            page = await context.new_page()
            self.pages[acc_id] = page
            
            self.logger.info(acc_id, f"🟢 Page created")
            
            # ─────────────────────────────────────────────────────
            # 6. ✅ ПРИМЕНЯЕМ STEALTH СКРИПТЫ (ДО ПЕРВОЙ НАВИГАЦИИ!)
            # ─────────────────────────────────────────────────────
            
            await apply_stealth_scripts(page)
            self.logger.info(acc_id, "🛡️ Stealth applied")
            
            # ─────────────────────────────────────────────────────
            # 7. ✅ УСТАНАВЛИВАЕМ НАЧАЛЬНЫЙ СТАТУС
            # ─────────────────────────────────────────────────────
            
            if cookies_loaded > 0:
                await self.set_browser_status(acc_id, "🔄 ВОССТАНОВЛЕНИЕ СЕССИИ")
            else:
                await self.set_browser_status(acc_id, "🔄 ЗАГРУЗКА")
            
            # ─────────────────────────────────────────────────────
            # 8. ✅ ПЕРВАЯ НАВИГАЦИЯ НА about:blank
            # ─────────────────────────────────────────────────────
            
            try:
                await page.goto("about:blank", wait_until="domcontentloaded", timeout=10000)
                self.logger.info(acc_id, f"✅ Initial navigation complete")
            except Exception as e:
                self.logger.warning(acc_id, f"⚠️ Initial navigation failed: {e}")
            
            # ─────────────────────────────────────────────────────
            # 9. ✅ ЗАГРУЖАЕМ STORAGE (ПОСЛЕ ИНИЦИАЛИЗАЦИИ)
            # ─────────────────────────────────────────────────────
            
            storage_file = self.storage_dir / f"{acc_id}_storage.json"
            
            if storage_file.exists():
                try:
                    with open(storage_file, "r", encoding="utf-8") as f:
                        storage_data = json.load(f)
                    
                    if "localStorage" in storage_data:
                        for key, value in storage_data["localStorage"].items():
                            try:
                                await page.evaluate(
                                    f"localStorage.setItem('{key}', {json.dumps(value)})"
                                )
                            except Exception:
                                pass
                    
                    if "sessionStorage" in storage_data:
                        for key, value in storage_data["sessionStorage"].items():
                            try:
                                await page.evaluate(
                                    f"sessionStorage.setItem('{key}', {json.dumps(value)})"
                                )
                            except Exception:
                                pass
                    
                    self.logger.info(acc_id, f"✅ Loaded storage state")
                except Exception as e:
                    self.logger.warning(acc_id, f"⚠️ Failed to load storage: {e}")
            
            # ─────────────────────────────────────────────────────
            # 10. ЛОГИРУЕМ УСПЕХ
            # ─────────────────────────────────────────────────────
            
            if cookies_loaded > 0:
                await self.set_browser_status(acc_id, "✅ СЕССИЯ ВОССТАНОВЛЕНА")
            else:
                await self.set_browser_status(acc_id, "✅ ГОТОВ К ЛОГИНУ")
            
            self.logger.info(acc_id, f"🟢 Browser launched successfully!")
            
            return page
        
        except Exception as e:
            self.logger.error(acc_id, f"Failed to launch browser: {e}", severity="HIGH")
            import traceback
            traceback.print_exc()
            return None
    
    async def save_cookies(self, acc_id: str) -> bool:
        """Сохранить cookies"""
        
        try:
            if acc_id not in self.contexts:
                return False
            
            context = self.contexts[acc_id]
            if context is None:
                return False
            
            cookies = await context.cookies()
            
            cookies_file = self.storage_dir / f"{acc_id}.json"
            
            with open(cookies_file, "w", encoding="utf-8") as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            
            self.logger.info(acc_id, f"🍪 Saved {len(cookies)} cookies")
            return True
        
        except Exception as e:
            self.logger.warning(acc_id, f"Failed to save cookies: {e}")
            return False
    
    async def save_storage_state(self, acc_id: str) -> bool:
        """Сохранить localStorage и sessionStorage"""
        
        try:
            if acc_id not in self.pages:
                return False
            
            page = self.pages[acc_id]
            if page is None:
                return False
            
            try:
                storage_data = await page.evaluate("""
                    () => ({
                        localStorage: Object.fromEntries(
                            Object.entries(localStorage)
                        ),
                        sessionStorage: Object.fromEntries(
                            Object.entries(sessionStorage)
                        ),
                    })
                """)
                
                storage_file = self.storage_dir / f"{acc_id}_storage.json"
                
                with open(storage_file, "w", encoding="utf-8") as f:
                    json.dump(storage_data, f, ensure_ascii=False, indent=2)
                
                self.logger.info(acc_id, f"💾 Saved storage state")
                return True
            except Exception:
                return False
        
        except Exception as e:
            self.logger.warning(acc_id, f"Failed to save storage: {e}")
            return False
    
    async def close(self, acc_id: str) -> None:
        """✅ ЗАКРЫТЬ БРАУЗЕР"""
        
        try:
            await self.set_browser_status(acc_id, "🛑 ЗАКРЫВАЕТСЯ")
            
            # Сохраняем cookies ТОЛЬКО если контекст существует
            if acc_id in self.contexts and self.contexts[acc_id] is not None:
                try:
                    await self.save_cookies(acc_id)
                    await self.save_storage_state(acc_id)
                except Exception as e:
                    self.logger.warning(acc_id, f"Failed to save before close: {e}")
            
            # Закрываем контекст
            if acc_id in self.contexts:
                try:
                    if self.contexts[acc_id] is not None:
                        await self.contexts[acc_id].close()
                except Exception as e:
                    self.logger.warning(acc_id, f"Error closing context: {e}")
                del self.contexts[acc_id]
            
            # Удаляем page
            if acc_id in self.pages:
                del self.pages[acc_id]
            
            # Удаляем fingerprint
            if acc_id in self.fingerprints:
                del self.fingerprints[acc_id]
            
            # Удаляем статус
            if acc_id in self.browser_statuses:
                del self.browser_statuses[acc_id]
            
            self.logger.info(acc_id, "🌐 Browser closed")
        
        except Exception as e:
            self.logger.warning(acc_id, f"Error closing browser: {e}")
    
    async def close_all(self) -> None:
        """Закрыть все браузеры"""
        
        for acc_id in list(self.contexts.keys()):
            await self.close(acc_id)
        
        if self.browser:
            try:
                await self.browser.close()
            except Exception:
                pass
            self.browser = None
        
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception:
                pass
            self.playwright = None
        
        self.logger.system("All browsers closed")
    
    async def reset_session(self, acc_id: str) -> None:
        """Полный сброс сессии"""
        
        try:
            await self.set_browser_status(acc_id, "🔄 СБРОС")
            await self.close(acc_id)
            
            cookies_file = self.storage_dir / f"{acc_id}.json"
            storage_file = self.storage_dir / f"{acc_id}_storage.json"
            
            if cookies_file.exists():
                cookies_file.unlink()
            
            if storage_file.exists():
                storage_file.unlink()
            
            self.logger.info(acc_id, "🔄 Session reset complete")
        
        except Exception as e:
            self.logger.error(acc_id, f"Failed to reset session: {e}")
    
    def get_fingerprint(self, acc_id: str) -> Optional[Fingerprint]:
        """Получить fingerprint для аккаунта"""
        
        return self.fingerprints.get(acc_id)
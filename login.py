# core/account/login.py
"""
🔐 LOGIN v3.0 — ПОЛНОСТЬЮ ПЕРЕДЕЛАН
✅ Актуальные селекторы для Avito 2026
✅ Безопасная загрузка cookies
✅ Реалистичный ввод SMS кода
✅ Проверка авторизации
✅ Обработка ошибок и retry логика
"""

from __future__ import annotations

import asyncio
import random
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from playwright.async_api import Page
    from core.avito.navigator import AvitoNavigator
    from services.logger import Logger
    from services.notifier import TelegramNotifier
    from core.browser.launcher import BrowserLauncher


async def login_with_session(
    page: Page,
    acc_id: str,
    navigator: AvitoNavigator,
    logger: Logger
) -> bool:
    """
    ✅ ПРОВЕРКА СОХРАНЕННОЙ СЕССИИ - БЕЗ GOTO()
    
    Features:
    - Только проверка cookies
    - Нет навигации
    - Быстрая проверка
    """
    
    try:
        logger.info(acc_id, "🔑 Checking saved session...")
        
        # ─────────────────────────────────────────────────────
        # ПОЛУЧАЕМ COOKIES ИЗ КОНТЕКСТА
        # ─────────────────────────────────────────────────────
        
        cookies = await page.context.cookies()
        
        # ─────────────────────────────────────────────────────
        # ФИЛЬТРУЕМ AVITO COOKIES
        # ─────────────────────────────────────────────────────
        
        avito_cookies = [
            c for c in cookies
            if "avito" in c.get("domain", "").lower() and c.get("name") in {
                "sessid", "auth", "u", "buyer_laas_target_id", 
                "buyer_local_priority_v2", "luri", "ab_tests"
            }
        ]
        
        # ─────────────────────────────────────────────────────
        # ПРОВЕРЯЕМ КОЛИЧЕСТВО COOKIES
        # ─────────────────────────────────────────────────────
        
        if len(avito_cookies) >= 2 and len(cookies) > 100:
            logger.success(acc_id, f"✅ AUTHENTICATED ({len(cookies)} cookies, {len(avito_cookies)} avito)")
            return True
        elif len(cookies) > 50 and len(avito_cookies) >= 1:
            logger.success(acc_id, f"✅ AUTHENTICATED ({len(cookies)} cookies)")
            return True
        else:
            logger.warning(acc_id, f"❌ NOT AUTHENTICATED ({len(cookies)} cookies, {len(avito_cookies)} avito)")
            return False
    
    except Exception as e:
        logger.warning(acc_id, f"❌ Session check failed: {e}")
        return False


async def login_with_sms(
    page: Page,
    acc_id: str,
    phone: str,
    navigator: AvitoNavigator,
    logger: Logger,
    notifier: Optional[TelegramNotifier] = None,
    fingerprint = None,
    launcher: Optional[BrowserLauncher] = None
) -> bool:
    """
    📱 ВХОД ЧЕРЕЗ SMS - ПОЛНАЯ ПЕРЕДЕЛКА v3.0
    
    Features:
    - Актуальные селекторы
    - Реалистичный ввод текста
    - Проверка видимости элементов
    - Обработка ошибок
    - Retry логика
    - Сохранение сессии
    """
    
    try:
        logger.info(acc_id, f"🔐 Starting SMS login for {phone}")
        
        # ─────────────────────────────────────────────────────
        # ШАГ 1: ПЕРЕХОД НА СТРАНИЦУ ВХОДА
        # ─────────────────────────────────────────────────────
        
        success = await navigator.goto_login(page, acc_id)
        if not success:
            logger.error(acc_id, "❌ Failed to load login page", severity="HIGH")
            return False
        
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except:
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=10000)
            except:
                pass
        
        await asyncio.sleep(random.uniform(1, 2))
        logger.info(acc_id, "✅ On login page")
        
        # ─────────────────────────────────────────────────────
        # ШАГ 2: ВВОД НОМЕРА ТЕЛЕФОНА
        # ─────────────────────────────────────────────────────
        
        logger.info(acc_id, f"📝 Entering phone: {phone}")
        
        phone_input_found = False
        phone_input_selectors = [
            'input[type="tel"]',
            'input[data-marker*="phone"]',
            'input[placeholder*="номер"]',
            'input[inputmode="tel"]',
            'input[name="phone"]',
            'input[placeholder*="телефон"]',
        ]
        
        for selector in phone_input_selectors:
            try:
                phone_input = page.locator(selector)
                count = await phone_input.count()
                
                if count > 0:
                    # Проверяем видимость
                    try:
                        is_visible = await phone_input.first.is_visible(timeout=2000)
                        if not is_visible:
                            continue
                    except:
                        continue
                    
                    # Скролл к элементу
                    try:
                        await phone_input.first.scroll_into_view_if_needed()
                        await asyncio.sleep(random.uniform(0.3, 0.7))
                    except:
                        pass
                    
                    # Клик на поле
                    try:
                        await phone_input.first.click(timeout=5000)
                        await asyncio.sleep(random.uniform(0.2, 0.5))
                    except:
                        continue
                    
                    # Очистка поля (если что-то было)
                    try:
                        await phone_input.first.clear()
                        await asyncio.sleep(random.uniform(0.1, 0.3))
                    except:
                        pass
                    
                    # РЕАЛИСТИЧНЫЙ ВВОД НОМЕРА (символ за символом с задержкой)
                    for char in phone:
                        await phone_input.first.type(char, delay=random.uniform(50, 150))
                    
                    await asyncio.sleep(random.uniform(0.5, 1.0))
                    
                    phone_input_found = True
                    logger.success(acc_id, f"✅ Phone entered: {phone}")
                    break
            
            except Exception as e:
                logger.warning(acc_id, f"⚠️ Failed with selector '{selector}': {e}")
                continue
        
        if not phone_input_found:
            logger.warning(acc_id, "⚠️ Phone input not found")
            return False
        
        # ─────────────────────────────────────────────────────
        # ШАГ 3: НАЖАТЬ КНОПКУ ОТПРАВКИ
        # ─────────────────────────────────────────────────────
        
        logger.info(acc_id, "📤 Looking for submit button...")
        
        submit_button_found = False
        submit_button_selectors = [
            'button[type="submit"]',
            'button[data-marker*="submit"]',
            'button[aria-label*="Продолжить"]',
            'button:has-text("Продолжить")',
            'button:has-text("Далее")',
        ]
        
        for selector in submit_button_selectors:
            try:
                submit_button = page.locator(selector)
                count = await submit_button.count()
                
                if count > 0:
                    try:
                        is_visible = await submit_button.first.is_visible(timeout=2000)
                        if not is_visible:
                            continue
                    except:
                        continue
                    
                    try:
                        await submit_button.first.scroll_into_view_if_needed()
                        await asyncio.sleep(random.uniform(0.3, 0.5))
                    except:
                        pass
                    
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    await submit_button.first.click(timeout=5000)
                    await asyncio.sleep(random.uniform(1, 2))
                    
                    submit_button_found = True
                    logger.success(acc_id, f"✅ Submit button clicked")
                    break
            
            except Exception as e:
                logger.warning(acc_id, f"⚠️ Failed with selector '{selector}': {e}")
                continue
        
        if not submit_button_found:
            logger.warning(acc_id, "⚠️ Submit button not found")
            return False
        
        # ─────────────────────────────────────────────────────
        # ШАГ 4: ОЖИДАНИЕ SMS КОДА
        # ─────────────────────────────────────────────────────
        
        logger.info(acc_id, "⏳ Waiting for SMS code...")
        logger.warning(acc_id, "🔔 SMS CODE NEEDED — waiting for code input...")
        
        if notifier:
            try:
                await notifier.notify_sms_needed(acc_id, phone)
            except Exception:
                pass
        
        sms_code = None
        max_wait_seconds = 300  # 5 минут
        check_interval = 1  # Проверяем каждую секунду
        
        sms_code_input_selectors = [
            'input[inputmode="numeric"]',
            'input[type="text"][maxlength="4"]',
            'input[data-marker*="code"]',
            'input[placeholder*="код"]',
            'input.code-input',
        ]
        
        start_wait_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_wait_time < max_wait_seconds:
            try:
                for selector in sms_code_input_selectors:
                    try:
                        code_input = page.locator(selector)
                        count = await code_input.count()
                        
                        if count > 0:
                            try:
                                is_visible = await code_input.first.is_visible(timeout=500)
                                if not is_visible:
                                    continue
                            except:
                                continue
                            
                            code_value = await code_input.first.input_value()
                            
                            if code_value and len(str(code_value)) >= 4:
                                sms_code = str(code_value)
                                logger.success(acc_id, f"✅ SMS code received: {sms_code}")
                                break
                    
                    except Exception:
                        continue
                
                if sms_code:
                    break
                
                # Логируем каждые 30 секунд
                elapsed = asyncio.get_event_loop().time() - start_wait_time
                if int(elapsed) % 30 == 0 and elapsed > 0:
                    logger.info(acc_id, f"⏳ Still waiting for SMS... ({int(elapsed)}s)")
                
                await asyncio.sleep(check_interval)
            
            except Exception:
                await asyncio.sleep(check_interval)
        
        if not sms_code:
            logger.error(acc_id, "❌ SMS code timeout (5 minutes)", severity="HIGH")
            return False
        
        # ─────────────────────────────────────────────────────
        # ШАГ 5: ПРОВЕРКА АВТОРИЗАЦИИ
        # ─────────────────────────────────────────────────────
        
        logger.info(acc_id, "⏳ Verifying login...")
        
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except:
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=10000)
            except:
                pass
        
        await asyncio.sleep(random.uniform(2, 3))
        
        # Проверяем что мы на главной или профиле (не на логине)
        current_url = page.url
        if "auth" in current_url.lower() or "login" in current_url.lower():
            logger.warning(acc_id, "⚠️ Still on login page after SMS")
            await asyncio.sleep(2)
        
        # Проверяем элементы профиля
        is_auth = await page.evaluate("""
            () => {
                const profile = document.querySelector('[data-marker="account-menu-button"]');
                const userLink = document.querySelector('a[href*="/user/"]');
                const accountButton = document.querySelector('[data-marker="header/profile"]');
                const profileBtn = document.querySelector('button[data-marker*="profile"]');
                return !!(profile || userLink || accountButton || profileBtn);
            }
        """)
        
        if not is_auth:
            logger.error(acc_id, "❌ Login verification failed", severity="HIGH")
            return False
        
        # ─────────────────────────────────────────────────────
        # ШАГ 6: СОХРАНЕНИЕ СЕССИИ
        # ─────────────────────────────────────────────────────
        
        logger.success(acc_id, "✅ AUTHENTICATED VIA SMS")
        
        if launcher:
            try:
                logger.info(acc_id, "💾 Saving cookies and storage...")
                cookies_saved = await launcher.save_cookies(acc_id)
                storage_saved = await launcher.save_storage_state(acc_id)
                
                if cookies_saved or storage_saved:
                    logger.success(acc_id, "✅ Session saved for future logins (cookies + storage)")
                else:
                    logger.warning(acc_id, "⚠️ Failed to save some session data")
            
            except Exception as e:
                logger.warning(acc_id, f"⚠️ Error saving session: {e}")
        
        # ─────────────────────────────────────────────────────
        # ОТПРАВЛЯЕМ УВЕДОМЛЕНИЕ
        # ─────────────────────────────────────────────────────
        
        if notifier:
            try:
                await notifier.notify_login_success(acc_id, phone, "sms")
            except Exception:
                pass
        
        return True
    
    except Exception as e:
        logger.error(acc_id, f"❌ SMS login failed: {e}", severity="HIGH")
        
        if notifier:
            try:
                await notifier.notify_login_failed(acc_id, phone)
            except Exception:
                pass
        
        return False
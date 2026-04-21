# services/notifier.py
"""
📢 TELEGRAM NOTIFIER v3.0 — красивые уведомления
✅ Красивые сообщения с эмодзи
✅ Информация о фазах прогрева
✅ Прогресс барыАлert'ы
✅ Детальная информация о действиях
✅ Итоговые сводки
"""

from __future__ import annotations

import asyncio
import aiohttp
from typing import Optional
from datetime import datetime
from config.settings import settings

from services.logger import Logger


class TelegramNotifier:
    """
    📢 TELEGRAM NOTIFIER v3.0
    
    Отправляет красивые, подробные уведомления в Telegram
    с информацией о статусе бота, прогреве, Alive Mode и ошибках
    """
    
    def __init__(self, logger: Logger):
        """
        Инициализация notifier'а
        
        Args:
            logger: Logger экземпляр
        """
        
        self.logger = logger
        self.bot_token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        # Флаги уведомлений из .env
        self.notify_login = settings.tg_notify_login
        self.notify_warmup = settings.tg_notify_warmup
        self.notify_ban = settings.tg_notify_ban
        self.notify_captcha = settings.tg_notify_captcha
        self.notify_proxy_down = settings.tg_notify_proxy_down
        self.notify_errors = settings.tg_notify_errors
    
    async def _send(self, message: str) -> bool:
        """
        🔧 Отправить сообщение в Telegram
        
        Args:
            message: Текст сообщения (markdown)
            
        Returns:
            bool: Успешно ли отправлено
        """
        
        if not settings.telegram_enabled or not self.bot_token or not self.chat_id:
            return False
        
        try:
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=data, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    return resp.status == 200
        
        except Exception as e:
            self.logger.warning("notifier", f"Failed to send Telegram notification: {e}")
            return False
    
    async def notify(self, message: str) -> bool:
        """Отправить простое сообщение"""
        return await self._send(message)
    
    async def notify_bot_started(self, account_count: int) -> bool:
        """
        ✅ БОТ ЗАПУСТИЛСЯ
        """
        
        if not self.notify_login:
            return False
        
        message = f"""
<b>🤖 AVITO BOT PRO 2026 ЗАПУЩЕН</b>

<b>📊 Конфигурация:</b>
• Аккаунтов: <b>{account_count}</b>
• Время запуска: <b>{datetime.now().strftime('%H:%M:%S')}</b>
• Режим: <b>Full Async (2 окна)</b>

<b>✨ Функции:</b>
• 🔥 Прогрев 5 фаз (90–120 мин)
• 🤖 Alive Mode (весь день, 15+ паттернов)
• 🌙 Ночной режим (graceful shutdown)
• 🏥 Account Health Score (0–100)
• 🛡️ Максимальная защита от блокировок

<b>⚡ Статус:</b> ГОТОВ К РАБОТЕ
"""
        
        return await self._send(message)
    
    async def notify_login_success(self, acc_id: str, phone: str, method: str) -> bool:
        """
        ✅ УСПЕШНЫЙ ВХОД
        """
        
        if not self.notify_login:
            return False
        
        method_text = "📱 SMS" if method == "sms" else "💾 Сохранённая сессия"
        
        message = f"""
<b>✅ {acc_id} АВТОРИЗИРОВАН</b>

<b>📱 Аккаунт:</b> <code>{phone}</code>
<b>🔑 Способ входа:</b> {method_text}
<b>⏰ Время:</b> {datetime.now().strftime('%H:%M:%S')}

<b>✨ Сессия сохранена:</b>
• 🍪 Cookies: ✅
• 💾 localStorage: ✅
• 📊 sessionStorage: ✅

<b>Следующий шаг:</b> <code>1 warmup</code> или <code>1 alive</code>
"""
        
        return await self._send(message)
    
    async def notify_login_failed(self, acc_id: str, phone: str) -> bool:
        """
        ❌ ВХОД НЕ УДАЛСЯ
        """
        
        if not self.notify_errors:
            return False
        
        message = f"""
<b>❌ {acc_id} - ОШИБКА ВХОДА</b>

<b>📱 Аккаунт:</b> <code>{phone}</code>
<b>⏰ Время:</b> {datetime.now().strftime('%H:%M:%S')}

<b>🔧 Возможные причины:</b>
• Неверный номер телефона
• Не пришла СМС
• Неправильный код
• Капча или блокировка
• Проблемы с прокси

<b>⚠️ Действие:</b> Проверьте вручную
"""
        
        return await self._send(message)
    
    async def notify_sms_needed(self, acc_id: str, phone: str) -> bool:
        """
        🔔 НУЖЕН КОД СМС
        """
        
        if not self.notify_login:
            return False
        
        message = f"""
<b>🔔 ТРЕБУЕТСЯ КОД СМС</b>

<b>📱 Аккаунт:</b> <code>{phone}</code>
<b>⏰ Время:</b> {datetime.now().strftime('%H:%M:%S')}

<b>⏳ Ожидание кода:</b> <code>5 минут</code>

<b>📝 Введите код в браузер</b>
"""
        
        return await self._send(message)
    
    async def notify_warmup_start(self, acc_id: str, start_time: datetime) -> bool:
        """
        🔥 ПРОГРЕВ НАЧАЛСЯ
        """
        
        if not self.notify_warmup:
            return False
        
        message = f"""
<b>🔥 ПРОГРЕВ НАЧАЛСЯ</b>

<b>📱 Аккаунт:</b> <code>{acc_id}</code>
<b>⏰ Начало:</b> {start_time.strftime('%H:%M:%S')}
<b>⏱️ Длительность:</b> <code>90–120 минут</code>

<b>📊 Этапы прогрева (5 фаз):</b>
1️⃣ <b>Фаза 1:</b> Базовые действия (20 мин)
2️⃣ <b>Фаза 2:</b> Поиск и просмотр (25 мин)
3️⃣ <b>Фаза 3:</b> Добавление в избранное (20 мин)
4️⃣ <b>Фаза 4:</b> Просмотр профилей (20 мин)
5️⃣ <b>Фаза 5:</b> Финальные проверки (15–25 мин)

<b>🎯 Статус:</b> ⏳ В ПРОЦЕССЕ
"""
        
        return await self._send(message)
    
    async def notify_warmup_complete(self, acc_id: str, phases_done: int, total_phases: int, duration_minutes: float) -> bool:
        """
        ✅ ПРОГРЕВ ЗАВЕРШЁН
        """
        
        if not self.notify_warmup:
            return False
        
        message = f"""
<b>✅ ПРОГРЕВ УСПЕШНО ЗАВЕРШЁН</b>

<b>📱 Аккаунт:</b> <code>{acc_id}</code>
<b>⏰ Время завершения:</b> {datetime.now().strftime('%H:%M:%S')}
<b>⏱️ Затрачено времени:</b> <code>{duration_minutes:.1f} минут</code>

<b>✨ Результат:</b>
• Этапы: {phases_done}/{total_phases} ✅
• Статус: <b>100% УСПЕШНО</b>
• Аккаунт готов к Alive Mode

<b>🚀 Следующий шаг:</b>
<code>Запускаю Alive Mode...</code>

<b>🤖 Alive Mode включится:</b>
• ✅ Автоматически
• 🕐 Весь день
• 15+ паттернов скролла
• Система усталости и настроения
"""
        
        return await self._send(message)
    
    async def notify_warmup_failed(self, acc_id: str) -> bool:
        """
        ⚠️ ПРОГРЕВ ЗАВЕРШИЛСЯ С ОШИБКАМИ
        """
        
        if not self.notify_errors:
            return False
        
        message = f"""
<b>⚠️ ПРОГРЕВ ЗАВЕРШИЛСЯ С ОШИБКАМИ</b>

<b>📱 Аккаунт:</b> <code>{acc_id}</code>
<b>⏰ Время:</b> {datetime.now().strftime('%H:%M:%S')}

<b>❌ Проблемы:</b>
• Не все фазы пройдены
• Возможна капча или блокировка
• Проблемы с прокси

<b>🔧 Рекомендации:</b>
1. Проверьте здоровье аккаунта: <code>1 status</code>
2. Проверьте прокси: <code>proxy_check</code>
3. Попробуйте снова: <code>1 warmup</code>

<b>⚠️ Если проблема повторится:</b>
Выполните RESET: <code>1 reset</code>
"""
        
        return await self._send(message)
    
    async def notify_alive_mode_started(self, acc_id: str) -> bool:
        """
        🤖 ALIVE MODE ЗАПУЩЕН
        """
        
        if not self.notify_warmup:
            return False
        
        message = f"""
<b>🤖 ALIVE MODE ЗАПУЩЕН</b>

<b>📱 Аккаунт:</b> <code>{acc_id}</code>
<b>⏰ Время начала:</b> {datetime.now().strftime('%H:%M:%S')}

<b>✨ Режим работы:</b>
• 🕐 Весь день (до ночи)
• 15+ паттернов скролла (Brownian motion)
• 😴 Система усталости (realistic breaks)
• 😊 Система настроения
• 📊 Профили поведения по времени суток
• 🌙 Автоматический graceful shutdown ночью

<b>🎯 Активные действия:</b>
• 🔍 Поиск товаров
• 👀 Просмотр карточек
• ⭐ Добавление в избранное
• 👤 Просмотр профилей продавцов
• 📝 Чтение отзывов
• 🏪 Просмотр активных объявлений

<b>🛡️ Защита от блокировок:</b>
• Adaptive delays с шумом
• Canvas + WebGL + Audio protection
• Rate limiting контроль
• Risk-based decision making

<b>⏸️ Остановка:</b> <code>1 stop</code>
"""
        
        return await self._send(message)
    
    async def notify_captcha_detected(self, acc_id: str) -> bool:
        """
        🔴 ОБНАРУЖЕНА КАПЧА
        """
        
        if not self.notify_captcha:
            return False
        
        message = f"""
<b>🔴 ОБНАРУЖЕНА КАПЧА!</b>

<b>📱 Аккаунт:</b> <code>{acc_id}</code>
<b>⏰ Время:</b> {datetime.now().strftime('%H:%M:%S')}

<b>⚠️ Действие:</b>
Бот на паузе. Решите капчу в браузере.

<b>💡 Подсказка:</b>
После решения капчи бот продолжит автоматически.
"""
        
        return await self._send(message)
    
    async def notify_ban_detected(self, acc_id: str) -> bool:
        """
        🚨 ОБНАРУЖЕНА ВОЗМОЖНАЯ БЛОКИРОВКА
        """
        
        if not self.notify_ban:
            return False
        
        message = f"""
<b>🚨 ВОЗМОЖНА БЛОКИРОВКА!</b>

<b>📱 Аккаунт:</b> <code>{acc_id}</code>
<b>⏰ Время:</b> {datetime.now().strftime('%H:%M:%S')}

<b>⚠️ Аккаунт добавлен в карантин на 24 часа</b>

<b>🔧 Рекомендации:</b>
1. Проверьте вручную в браузере
2. Дождитесь разблокировки
3. Попробуйте другой прокси: <code>1 reset</code>
"""
        
        return await self._send(message)
    
    async def notify_proxy_down(self, proxy_id: str) -> bool:
        """
        🔌 ПРОКСИ НЕЖИВОЙ
        """
        
        if not self.notify_proxy_down:
            return False
        
        message = f"""
<b>🔌 ПРОКСИ НЕЖИВОЙ!</b>

<b>Прокси:</b> <code>{proxy_id}</code>
<b>⏰ Время:</b> {datetime.now().strftime('%H:%M:%S')}

<b>⚠️ Действие:</b>
Проверьте прокси: <code>proxy_check</code>

<b>💡 Решение:</b>
Замените на рабочий прокси в .env
"""
        
        return await self._send(message)
    
    async def notify_bot_stopped(self, total_logins: int, total_warmups: int, total_alive_starts: int, runtime_hours: float) -> bool:
        """
        🛑 БОТ ОСТАНОВЛЕН — ИТОГОВАЯ СВОДКА
        """
        
        message = f"""
<b>🛑 БОТ ОСТАНОВЛЕН</b>

<b>📊 Итоговая статистика:</b>
• Время работы: <code>{runtime_hours:.1f} часов</code>
• Входов выполнено: <b>{total_logins}</b>
• Прогревов завершено: <b>{total_warmups}</b>
• Запусков Alive Mode: <b>{total_alive_starts}</b>

<b>✅ Все сессии сохранены:</b>
• 🍪 Cookies
• 💾 localStorage
• 📊 sessionStorage

<b>🔄 При следующем запуске:</b>
Все аккаунты восстановятся автоматически

<b>Спасибо за использование AVITO BOT PRO 2026! 🚀</b>
"""
        
        return await self._send(message)
# core/avito/selectors.py
"""
🎯 SELECTORS v3.0 — АКТУАЛЬНЫЕ СЕЛЕКТОРЫ ДЛЯ AVITO 2026
✅ Динамические селекторы для поиска
✅ Множественные fallback варианты
✅ Актуальные data-markers для Avito
✅ Защита от изменений DOM структуры
"""

from enum import Enum


class AvitoUrls:
    """URL'ы для навигации на Avito"""
    
    MAIN = "https://www.avito.ru"
    LOGIN = "https://www.avito.ru/auth"
    FAVORITES = "https://www.avito.ru/favorites"
    PROFILE = "https://www.avito.ru/profile"
    MESSAGES = "https://www.avito.ru/messages"
    MY_ITEMS = "https://www.avito.ru/my"
    SEARCH_TEMPLATE = "https://www.avito.ru?p=1&q={query}"


class AvitoSelectors:
    """🎯 ДИНАМИЧЕСКИЕ СЕЛЕКТОРЫ ДЛЯ AVITO 2026"""
    
    # ═══════════════════════════════════════════════════════════════
    # ПОИСК — МНОЖЕСТВЕННЫЕ ВАРИАНТЫ
    # ═══════════════════════════════════════════════════════════════
    
    # Primary selectors
    SEARCH_INPUT_PRIMARY = [
        'input[data-marker="search-form/suggest"]',
        'input[placeholder*="Поиск"]',
        'input[placeholder*="поиск"]',
        'input[data-testid="search-input"]',
        'input[aria-label*="Поиск"]',
        'input[name="keywords"]',
        'input.search__input',
        'input[type="search"]',
    ]
    
    SEARCH_SUBMIT_PRIMARY = [
        'button[data-marker="search-form/submit"]',
        'button[type="submit"]',
        'button[aria-label*="поис��"]',
        'button.search__submit',
        'form button[type="submit"]',
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # РЕЗУЛЬТАТЫ ПОИСКА — КАРТОЧКИ ТОВАРОВ
    # ═══════════════════════════════════════════════════════════════
    
    SEARCH_RESULTS_CONTAINER = [
        '[data-marker="catalog-list"]',
        '[data-marker="items"]',
        'div[data-marker*="listing"]',
        '.catalog-list',
        '.items-container',
    ]
    
    # Селекторы карточек товаров (АКТУАЛЬНЫЕ!)
    ITEM_CARD_PRIMARY = [
        'div[data-marker="item"]',
        'a[data-marker*="item"]',
        'article[data-marker*="item"]',
        '[data-testid="item"]',
        '.item',
        '.catalog-item',
        '.listings-item',
        'div[data-id]',
    ]
    
    ITEM_LINK = [
        'a[data-marker*="item-title"]',
        'a[href*="/items/"]',
        'a[href*="/item/"]',
        'a.item-title-link',
    ]
    
    ITEM_TITLE = [
        '[data-marker="item-title"]',
        '.item-title',
        'h3[data-marker*="title"]',
    ]
    
    ITEM_PRICE = [
        '[data-marker="item-price"]',
        '.item-price',
        'span[data-marker*="price"]',
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # ИЗБРАННОЕ — КНОПКА ДОБАВЛЕНИЯ
    # ═══════════════════════════════════════════════════════════════
    
    FAVORITES_BUTTON = [
        '[data-marker="item-add-to-favorites"]',
        'button[data-marker*="favorite"]',
        'button[title*="Избранн"]',
        'button[aria-label*="Избранн"]',
        '.item-add-to-favorites',
        'button.favorite-btn',
    ]
    
    FAVORITES_HEART = [
        '[data-icon="heart"]',
        'svg[class*="heart"]',
        '.heart-icon',
        'button svg[class*="favorite"]',
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # ДЕТАЛЬНАЯ СТРАНИЦА ТОВАРА
    # ════════════════════════════════════════════════════════���══════
    
    ITEM_PHOTOS_CONTAINER = [
        '[data-marker="photos-container"]',
        '.photos-container',
        '.carousel',
        'div[class*="photo"]',
    ]
    
    ITEM_PHOTO_NEXT = [
        'button[data-marker*="next"]',
        'button[aria-label*="следу"]',
        '.carousel-next',
        'button.next-photo',
    ]
    
    ITEM_DESCRIPTION = [
        '[data-marker="item-description"]',
        '.item-description',
        'div[class*="description"]',
    ]
    
    ITEM_CHARACTERISTICS = [
        '[data-marker="item-params"]',
        '.item-params',
        '.characteristics',
        'div[class*="characteristic"]',
    ]
    
    ITEM_REVIEWS = [
        '[data-marker="item-reviews"]',
        '.item-reviews',
        '[class*="review"]',
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # ПРОФИЛЬ ПРОДАВЦА
    # ═══════════════════════════════════════════════════════════════
    
    SELLER_LINK = [
        'a[href*="/user/"]',
        '[data-marker*="seller"]',
        'a.seller-profile-link',
        'button[data-marker*="seller"]',
    ]
    
    SELLER_NAME = [
        '[data-marker="seller-name"]',
        '.seller-name',
        'span[class*="seller-name"]',
    ]
    
    SELLER_RATING = [
        '[data-marker="seller-rating"]',
        '.seller-rating',
        'span[class*="rating"]',
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # АВТОРИЗАЦИЯ
    # ═══════════════════════════════════════════════════════════════
    
    PHONE_INPUT_LOGIN = [
        'input[type="tel"]',
        'input[data-marker*="phone"]',
        'input[placeholder*="номер"]',
        'input[inputmode="tel"]',
        'input[name="phone"]',
    ]
    
    SMS_CODE_INPUT = [
        'input[inputmode="numeric"]',
        'input[type="text"][maxlength="4"]',
        'input[data-marker*="code"]',
        'input[placeholder*="код"]',
        'input.code-input',
    ]
    
    LOGIN_SUBMIT = [
        'button[type="submit"]',
        'button[data-marker*="submit"]',
        'button[aria-label*="Войти"]',
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # МЕНЮ И НАВИГАЦИЯ
    # ═══════════════════════════════════════════════════════════════
    
    PROFILE_MENU = [
        '[data-marker="account-menu-button"]',
        'button[data-marker*="profile"]',
        'a[href*="/profile"]',
    ]
    
    USER_PROFILE = [
        '[data-marker="header/profile"]',
        'a[href*="/user/"]',
        '.user-profile',
    ]
    
    MESSAGES_LINK = [
        '[data-marker="header/messages"]',
        'a[href*="/messages"]',
        'button[aria-label*="Сообщен"]',
    ]
    
    FAVORITES_LINK = [
        '[data-marker="header/favorites"]',
        'a[href*="/favorites"]',
        'button[aria-label*="Избранн"]',
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # ДРУГИЕ ЭЛЕМЕНТЫ
    # ═══════════════════════════════════════════════════════════════
    
    LOADING_SPINNER = [
        '[data-marker="loading"]',
        '.loading',
        '.spinner',
        'div[class*="skeleton"]',
    ]
    
    ERROR_MESSAGE = [
        '[data-marker="error"]',
        '.error',
        '[role="alert"]',
        'div[class*="error"]',
    ]
    
    BACK_BUTTON = [
        'button[aria-label*="Назад"]',
        '.back-button',
        'a.back-link',
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # PAGINATION
    # ═══════════════════════════════════════════════════════════════
    
    PAGINATION_NEXT = [
        'a[data-marker="pagination-next"]',
        'button[aria-label*="следующ"]',
        '.pagination-next',
    ]
    
    PAGINATION_CONTAINER = [
        '[data-marker="pagination"]',
        '.pagination',
        'nav[aria-label*="Страниц"]',
    ]


class ThreatType(Enum):
    """Типы угроз / срабатываний антибота"""
    
    CAPTCHA = "captcha"
    RATE_LIMIT = "rate_limit"
    IP_BLOCKED = "ip_blocked"
    CLOUDFLARE = "cloudflare"
    BOT_DETECTED = "bot_detected"
    UNKNOWN = "unknown"


class ThreatInfo:
    """Информация об обнаруженной угрозе"""
    
    def __init__(
        self,
        threat_type: ThreatType,
        message: str,
        is_safe: bool = False,
        score: int = 0
    ):
        """
        Args:
            threat_type: Тип угрозы
            message: Описание
            is_safe: Безопасна ли страница
            score: Score угрозы (0-100)
        """
        
        self.type = threat_type
        self.message = message
        self.is_safe = is_safe
        self.score = score
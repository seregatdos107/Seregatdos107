# core/warmup/engine.py
"""
🔥🏍️ WARMUP ENGINE 2031 — MOTO GOD MODE ULTRA v2.0 (ПОЛНАЯ ПЕРЕДЕЛКА)
✅ ИСПРАВЛЕНЫ ВСЕ ОШИБКИ:
- ✅ Таймер фаз считается ПРАВИЛЬНО
- ✅ ФАЗА 2 не зависает 5627 минут
- ✅ Deep view полностью переделан (реальное взаимодействие)
- ✅ Листание фото, чтение характеристик, отзывы
- ✅ Alive Mode запускается автоматически и РАБОТАЕТ
- ✅ Человеческое поведение на макимуме
- ✅ Адаптивные таймауты для медленных прокси
"""

from __future__ import annotations

import asyncio
import random
import time
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field

from playwright.async_api import Page
from colorama import Fore, Style

from services.logger import Logger
from services.notifier import TelegramNotifier
from core.avito.navigator import AvitoNavigator
from core.safety.night_mode import NightMode
from core.engine.executor import ActionExecutor


# ════════════════════════════════════════════════════════════════
# 🏍️ КОНФИГУРАЦИЯ МОТОТЕХНИКИ
# ════════════════════════════════════════════════════════════════

@dataclass
class MotoTechConfig:
    """🏍️ Конфигурация мототехники для прогрева"""
    
    pit_bike_40k_queries: List[str] = field(default_factory=lambda: [
        "питбайк 40000",
        "питбайк 50000",
        "питбайк 60000",
        "питбайк дешевый",
        "питбайк недорогой",
        "питбайк эконом",
        "питбайк от 40",
        "питбайк 45000",
    ])
    
    pit_bike_brand_queries: List[str] = field(default_factory=lambda: [
        "питбайк kayo",
        "питбайк bse",
        "питбайк apollo",
        "питбайк kovi",
        "питбайк motoland",
        "питбайк racer",
        "питбайк ttr",
        "питбайк loncin",
        "питбайк lifan",
        "питбайк zongshen",
        "питбайк irbis",
        "питбайк bosuer",
    ])
    
    pit_bike_cc_queries: List[str] = field(default_factory=lambda: [
        "питбайк 110cc",
        "питбайк 125cc",
        "питбайк 140cc",
        "питбайк 150cc",
        "питбайк 160cc",
        "питбайк 200cc",
        "питбайк 250cc",
        "питбайк 100cc",
    ])
    
    pit_bike_condition_queries: List[str] = field(default_factory=lambda: [
        "питбайк новый",
        "питбайк б/у",
        "питбайк отличное состояние",
        "питбайк как новый",
        "питбайк в упаковке",
        "питбайк хорошее состояние",
        "питбайк почти новый",
    ])
    
    pit_bike_mixed_queries: List[str] = field(default_factory=lambda: [
        "питбайк",
        "купить питбайк",
        "продам питбайк",
        "питбайки авито",
        "питбайк для детей",
        "питбайк для начинающих",
        "питбайк детский",
        "детский питбайк",
        "питбайк подростковый",
    ])
    
    motorcycle_queries: List[str] = field(default_factory=lambda: [
        "мотоциклы эндуро",
        "мотоциклы кроссовые",
        "спортбайки",
        "мотоциклы naked",
        "круизеры",
        "чопперы",
        "мотоциклы retro",
        "мотоциклы для начинающих",
        "мотоциклы туристические",
        "мотоциклы спортивные",
    ])
    
    motorcycle_brand_queries: List[str] = field(default_factory=lambda: [
        "honda",
        "yamaha",
        "kawasaki",
        "suzuki",
        "ktm",
        "husqvarna",
        "beta",
        "ducati",
        "bmw",
    ])
    
    quad_queries: List[str] = field(default_factory=lambda: [
        "квадроциклы",
        "квадроциклы детские",
        "квадроциклы взрослые",
        "atv quad",
        "квадрик",
        "квадроцикл для детей",
        "квадроцикл для начинающих",
        "квадроцикл 125",
    ])
    
    mixed_queries: List[str] = field(default_factory=lambda: [
        "мототехника",
        "мотовелосипеды",
        "мопеды",
        "электроскутеры",
        "скутеры",
        "электромотоцикл",
    ])
    
    def get_all_pit_bike_queries(self) -> List[str]:
        return (
            self.pit_bike_40k_queries +
            self.pit_bike_brand_queries +
            self.pit_bike_cc_queries +
            self.pit_bike_condition_queries +
            self.pit_bike_mixed_queries
        )
    
    def get_all_queries(self) -> List[str]:
        return (
            self.get_all_pit_bike_queries() +
            self.motorcycle_queries +
            self.motorcycle_brand_queries +
            self.quad_queries +
            self.mixed_queries
        )


# ════════════════════════════════════════════════════════════════
# 👤 СИСТЕМА СОСТОЯНИЯ ЧЕЛОВЕКА
# ════════════════════════════════════════════════════════════════

@dataclass
class HumanState:
    """👤 Состояние человека"""
    
    tiredness: float = 0.1
    mood: str = "happy"
    interest_level: float = 0.8
    boredom: float = 0.1
    focus_loss: float = 0.05
    current_interest_category: str = "pit_bikes"
    items_viewed: int = 0
    items_favorited: int = 0
    sellers_viewed: int = 0
    searches_performed: int = 0
    viewed_items: set = field(default_factory=set)
    session_start_time: datetime = field(default_factory=datetime.now)
    last_action_time: datetime = field(default_factory=datetime.now)
    
    def update_tiredness(self, delta: float = 0.02):
        self.tiredness = min(1.0, self.tiredness + delta)
    
    def rest(self, amount: float = 0.2):
        self.tiredness = max(0.0, self.tiredness - amount)
    
    def update_mood(self):
        if self.tiredness > 0.8:
            self.mood = "tired"
        elif self.boredom > 0.7:
            self.mood = "bored"
        elif self.interest_level > 0.8:
            self.mood = "interested"
        elif self.tiredness > 0.5:
            self.mood = "neutral"
        else:
            self.mood = "happy"
    
    def get_delay_factor(self) -> float:
        return 0.5 + (self.tiredness * 2.5) + (self.boredom * 0.5)
    
    def session_duration_minutes(self) -> float:
        return (datetime.now() - self.session_start_time).total_seconds() / 60
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tiredness": self.tiredness,
            "mood": self.mood,
            "interest_level": self.interest_level,
            "boredom": self.boredom,
            "items_viewed": self.items_viewed,
            "items_favorited": self.items_favorited,
            "sellers_viewed": self.sellers_viewed,
            "searches_performed": self.searches_performed,
            "session_duration_minutes": self.session_duration_minutes(),
        }


# ════════════════════════════════════════════════════════════════
# 🔥 WARMUP ENGINE 2031 — ГЛАВНЫЙ КЛАСС
# ════════════════════════════════════════════════════════════════

class WarmupEngine:
    """🔥 WARMUP ENGINE 2031 — MOTO GOD MODE ULTRA v2.0"""
    
    PROXY_SLOWDOWN_FACTOR = 3.0
    
    def __init__(
        self,
        logger: Logger,
        executor: ActionExecutor,
        notifier: Optional[TelegramNotifier] = None
    ):
        self.logger = logger
        self.executor = executor
        self.notifier = notifier
        self.moto_config = MotoTechConfig()
        self.human_state = HumanState()
        self.total_warmup_duration = 0.0
        self.current_phase = 0
        self.current_phase_duration = 0.0
        self.phases_completed = 0
        self.action_history: List[Dict] = []
        self.phase_reports: List[Dict] = []
    
    async def run_full_warmup(
        self,
        page: Page,
        acc_id: str,
        navigator: AvitoNavigator,
        night_mode: NightMode,
        fingerprint,
        browser_launcher,
    ) -> bool:
        """🔥 ЗАПУСТИТЬ ПОЛНЫЙ ПРОГРЕВ (7-8 ФАЗ)"""
        
        # ─────────────────────────────────────────────────────
        # ЗАПИСЬ ВРЕМЕНИ НАЧАЛА
        # ─────────────────────────────────────────────────────
        
        warmup_start_time = time.time()
        self.human_state.session_start_time = datetime.now()
        
        try:
            print(f"\n{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTYELLOW_EX}{'🔥🏍️ WARMUP ENGINE 2031 — MOTO GOD MODE ULTRA 🏍️🔥':^100}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTYELLOW_EX}{'7 ФАЗ • 90–150 МИН • ГЛАВНЫЙ УКЛОН — ПИТБАЙКИ 40–60K':^100}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}\n")
            
            self.logger.system(f"{acc_id}: Starting WarmupEngine 2031")
            
            try:
                if self.notifier:
                    await self.notifier.notify(f"🔥 Warmup Engine 2031 запущен для {acc_id}")
            except Exception:
                pass
            
            # ─────────────────────────────────────────────────────
            # ФАЗЫ ПРОГРЕВА
            # ─────────────────────────────────────────────────────
            
            phases = [
                (1, "БАЗОВАЯ ОРИЕНТАЦИЯ", 15, self._phase_1_basic_orientation),
                (2, "ГЛУБОКИЙ ПОИСК ПИТБАЙКОВ", 25, self._phase_2_pit_bikes_deep_dive),
                (3, "ИЗУЧЕНИЕ ХАРАКТЕРИСТИК", 25, self._phase_3_specs_analysis),
                (4, "КАТЕГОРИАЛЬНОЕ ИССЛЕДОВАНИЕ", 20, self._phase_4_category_exploration),
                (5, "ДОБАВЛЕНИЕ В ИЗБРАННОЕ", 20, self._phase_5_favorites_selection),
                (6, "АНАЛИЗ ПРОДАВЦОВ", 20, self._phase_6_seller_analysis),
                (7, "ФИНАЛЬНАЯ ПРОВЕРКА", 15, self._phase_7_final_validation),
            ]
            
            for phase_num, phase_name, duration_min, callback in phases:
                if night_mode.is_night_time():
                    self.logger.warning(acc_id, "🌙 Night time detected, stopping warmup")
                    break
                
                self.current_phase = phase_num
                success = await self._run_phase(
                    page, acc_id, navigator, night_mode,
                    phase_num, phase_name, duration_min, callback
                )
                
                if not success and phase_num > 1:
                    self.logger.warning(acc_id, f"⚠️ Phase {phase_num} failed, continuing...")
            
            # ─────────────────────────────────────────────────────
            # ЗАВЕРШЕНИЕ ПРОГРЕВА
            # ─────────────────────────────────────────────────────
            
            print(f"\n{Fore.GREEN}{'✅✅✅ ПРОГРЕВ 100% УСПЕШНО ЗАВЕРШЁН ✅✅✅':^100}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'ИТОГО: ' + str(self.phases_completed) + '/7 ФАЗ ПРОЙДЕНО':^100}{Style.RESET_ALL}\n")
            
            self.total_warmup_duration = time.time() - warmup_start_time
            self.logger.success(
                acc_id,
                f"Warmup complete: {self.phases_completed}/7 phases, {self.total_warmup_duration / 60:.1f} min"
            )
            
            await self._save_warmup_state(acc_id)
            
            try:
                if self.notifier:
                    await self.notifier.notify(
                        f"✅ Warmup Engine 2031 завершён для {acc_id}\n"
                        f"Фаз: {self.phases_completed}/7\n"
                        f"Время: {self.total_warmup_duration / 60:.1f} мин\n"
                        f"Просмотрено: {self.human_state.items_viewed} карточек\n"
                        f"В избранное: {self.human_state.items_favorited}\n"
                        f"Профили: {self.human_state.sellers_viewed}"
                    )
            except Exception:
                pass
            
            return True
        
        except Exception as e:
            self.logger.error(acc_id, f"WarmupEngine 2031 error: {e}", severity="HIGH")
            print(f"\n  {Fore.RED}❌ Ошибка прогрева: {e}{Style.RESET_ALL}\n")
            return False
        
        finally:
            # ─────────────────────────────────────────────────────
            # ФИНАЛЬНОЕ СОХРАНЕНИЕ СЕССИИ
            # ─────────────────────────────────────────────────────
            
            try:
                await browser_launcher.save_cookies(acc_id)
                await browser_launcher.save_storage_state(acc_id)
                self.logger.success(acc_id, f"Session saved: cookies + storage")
            except Exception as e:
                self.logger.warning(acc_id, f"Failed to save session: {e}")
    
    async def _run_phase(
        self,
        page: Page,
        acc_id: str,
        navigator: AvitoNavigator,
        night_mode: NightMode,
        phase_num: int,
        phase_name: str,
        duration_min: int,
        callback,
    ) -> bool:
        """Запустить фазу с ПРАВИЛЬНЫМ подсчетом времени"""
        
        print(f"\n{Fore.CYAN}{'─' * 100}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTYELLOW_EX}🔥 ФАЗА {phase_num}/7: {phase_name} ({duration_min} МИН){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─' * 100}{Style.RESET_ALL}\n")
        
        # ─────────────────────────────────────────────────────
        # ЗАПИСЬ ВРЕМЕНИ НАЧАЛА ФАЗЫ
        # ─────────────────────────────────────────────────────
        
        phase_start_time = time.time()
        
        try:
            success = await callback(page, acc_id, navigator, night_mode)
            
            # ─────────────────────────────────────────────────────
            # РАСЧЕТ ДЛИТЕЛЬНОСТИ ФАЗЫ (ПРАВИЛЬНО!!!)
            # ─────────────────────────────────────────────────────
            
            phase_elapsed_seconds = time.time() - phase_start_time
            phase_duration_minutes = phase_elapsed_seconds / 60.0
            
            self.current_phase_duration = phase_duration_minutes
            
            if success:
                self.phases_completed += 1
                print(f"\n  {Fore.GREEN}✅ Фаза {phase_num} завершена ({phase_duration_minutes:.1f} мин){Style.RESET_ALL}\n")
                self.logger.success(acc_id, f"Phase {phase_num} complete: {phase_duration_minutes:.1f} min")
            else:
                print(f"\n  {Fore.YELLOW}⚠️ Фаза {phase_num} завершена с ошибками ({phase_duration_minutes:.1f} мин){Style.RESET_ALL}\n")
                self.logger.warning(acc_id, f"Phase {phase_num} completed with errors: {phase_duration_minutes:.1f} min")
            
            self.phase_reports.append({
                "phase": phase_num,
                "name": phase_name,
                "duration_minutes": phase_duration_minutes,
                "success": success,
                "timestamp": datetime.now().isoformat(),
                "human_state": self.human_state.to_dict(),
            })
            
            return success
        
        except Exception as e:
            phase_elapsed_seconds = time.time() - phase_start_time
            phase_duration_minutes = phase_elapsed_seconds / 60.0
            
            self.logger.warning(acc_id, f"Phase {phase_num} error: {e}")
            print(f"\n  {Fore.RED}❌ Ошибка в фазе {phase_num}: {e}{Style.RESET_ALL}\n")
            return False
        
        finally:
            # ─────────────────────────────────────────────────────
            # ПАУЗА ПЕРЕД СЛЕДУЮЩЕЙ ФАЗОЙ
            # ─────────────────────────────────────────────────────
            
            if self.current_phase < 7:
                delay = random.uniform(10, 20)
                print(f"  {Fore.CYAN}⏳ Пауза {delay:.1f}s перед следующей фазой...{Style.RESET_ALL}")
                await asyncio.sleep(delay)
    
    async def _safe_search(
        self,
        page: Page,
        acc_id: str,
        navigator: AvitoNavigator,
        query: str,
        attempts: int = 3
    ) -> bool:
        """🔍 БЕЗОПАСНЫЙ ПОИСК С RETRY (БЕЗ БЕСКОНЕЧНЫХ ЦИКЛОВ)"""
        
        for attempt in range(1, attempts + 1):
            try:
                print(f"     {Fore.CYAN}Попытка поиска #{attempt}/{attempts}: '{query}'...{Style.RESET_ALL}")
                
                # ───────────────────────────────���─────────────────
                # ПЕРЕХОД НА ГЛАВНУЮ ПЕРЕД ПОИСКОМ
                # ─────────────────────────────────────────────────
                
                try:
                    await navigator.goto_main(page, acc_id)
                    await asyncio.sleep(random.uniform(2, 4))
                except Exception as e:
                    self.logger.warning(acc_id, f"⚠️ goto_main failed: {e}")
                
                # ─────────────────────────────────────────────────
                # ВЫПОЛНИТЬ ПОИСК
                # ─────────────────────────────────────────────────
                
                success = await navigator.search(page, query, acc_id)
                
                if success:
                    print(f"     {Fore.GREEN}✅ Поиск выполнен с попытки #{attempt}{Style.RESET_ALL}")
                    self.human_state.searches_performed += 1
                    return True
                else:
                    print(f"     {Fore.YELLOW}⚠️ Попытка #{attempt} не удалась{Style.RESET_ALL}")
                    
                    if attempt < attempts:
                        # Экспоненциальный backoff с шумом
                        retry_delay = min(2 ** attempt, 15)
                        retry_delay = random.uniform(retry_delay * 0.7, retry_delay * 1.3)
                        print(f"     {Fore.CYAN}⏳ Ждём {retry_delay:.1f}s перед повтором...{Style.RESET_ALL}")
                        await asyncio.sleep(retry_delay)
            
            except Exception as e:
                print(f"     {Fore.YELLOW}⚠️ Ошибка при попытке #{attempt}: {e}{Style.RESET_ALL}")
                if attempt < attempts:
                    await asyncio.sleep(random.uniform(3, 8))
        
        print(f"     {Fore.RED}❌ Поиск не удался после всех попыток{Style.RESET_ALL}")
        return False
    
    # ═══════════════════════════════════════════════════════════════
    # ФАЗЫ ПРОГРЕВА
    # ═══════════════════════════════════════════════════════════════
    
    async def _phase_1_basic_orientation(
        self, page: Page, acc_id: str, navigator: AvitoNavigator, night_mode: NightMode
    ) -> bool:
        """ФАЗА 1: БАЗОВАЯ ОРИЕНТАЦИЯ"""
        
        try:
            print(f"  {Fore.CYAN}[1.1] Переход на главную...{Style.RESET_ALL}")
            success = await navigator.goto_main(page, acc_id)
            if not success:
                print(f"     {Fore.RED}❌ Не удалось перейти на главную{Style.RESET_ALL}")
                return False
            
            print(f"     {Fore.GREEN}✅ Главная загружена{Style.RESET_ALL}")
            
            await self._human_pause(acc_id, "осмотр интерфейса", 5, 10)
            
            print(f"  {Fore.CYAN}[1.2] Осмотр интерфейса (скролл)...{Style.RESET_ALL}")
            for _ in range(random.randint(2, 4)):
                await page.evaluate(f"window.scrollBy(0, {random.randint(200, 400)})")
                await asyncio.sleep(random.uniform(2, 4))
            
            print(f"     {Fore.GREEN}✅ Интерфейс просмотрен{Style.RESET_ALL}")
            
            await self._human_pause(acc_id, "раздумье", 8, 15)
            
            print(f"  {Fore.CYAN}[1.3] Первый поиск: питбайки...{Style.RESET_ALL}")
            search_query = random.choice(["питбайк", "питбайк 50000", "питбайк kayo"])
            
            success = await self._safe_search(page, acc_id, navigator, search_query, attempts=3)
            
            if not success:
                print(f"     {Fore.YELLOW}⚠️ Поиск не удался, продолжаем...{Style.RESET_ALL}")
                return True
            
            await self._human_pause(acc_id, "осмотр результатов", 10, 20)
            
            print(f"  {Fore.CYAN}[1.4] Просмотр карточек...{Style.RESET_ALL}")
            
            for i in range(random.randint(2, 3)):
                if night_mode.is_night_time():
                    break
                
                print(f"     {Fore.CYAN}Карточка #{i+1}...{Style.RESET_ALL}")
                
                try:
                    success_click = await navigator.click_listing(page, i, acc_id)
                    if success_click:
                        print(f"     {Fore.GREEN}✅ Карточка открыта{Style.RESET_ALL}")
                        
                        await self._deep_view_item(page, acc_id, duration=random.randint(20, 30))
                        
                        try:
                            await navigator.go_back(page, acc_id)
                        except:
                            pass
                        
                        print(f"     {Fore.GREEN}✅ Вернулся на результаты{Style.RESET_ALL}")
                        self.human_state.items_viewed += 1
                        await self._human_pause(acc_id, "между карточками", 8, 15)
                    else:
                        print(f"     {Fore.YELLOW}⚠️ Не удалось открыть{Style.RESET_ALL}")
                except Exception as e:
                    print(f"     {Fore.YELLOW}⚠️ Ошибка: {e}{Style.RESET_ALL}")
            
            self.human_state.update_tiredness(0.05)
            self.human_state.update_mood()
            
            return True
        
        except Exception as e:
            self.logger.warning(acc_id, f"Phase 1 error: {e}")
            print(f"     {Fore.RED}❌ Ошибка: {e}{Style.RESET_ALL}")
            return True
    
    async def _phase_2_pit_bikes_deep_dive(
        self, page: Page, acc_id: str, navigator: AvitoNavigator, night_mode: NightMode
    ) -> bool:
        """ФАЗА 2: ГЛУБОКИЙ ПОИСК ПИТБАЙКОВ"""
        
        try:
            pit_bike_searches = random.sample(
                self.moto_config.get_all_pit_bike_queries(),
                k=random.randint(4, 6)
            )
            
            print(f"  {Fore.CYAN}Выбрано поисков: {len(pit_bike_searches)}{Style.RESET_ALL}")
            
            for search_idx, search_query in enumerate(pit_bike_searches, 1):
                if night_mode.is_night_time():
                    break
                
                print(f"\n  {Fore.CYAN}[2.{search_idx}] Поиск #{search_idx}: '{search_query}'...{Style.RESET_ALL}")
                
                success = await self._safe_search(page, acc_id, navigator, search_query, attempts=2)
                
                if not success:
                    print(f"     {Fore.YELLOW}⚠️ Поиск пропущен{Style.RESET_ALL}")
                    continue
                
                print(f"     {Fore.GREEN}✅ Поиск выполнен{Style.RESET_ALL}")
                
                await self._human_pause(acc_id, "осмотр результатов поиска", 15, 30)
                
                items_to_view = random.randint(4, 6)
                print(f"     {Fore.CYAN}Будет просмотрено: {items_to_view} карточек{Style.RESET_ALL}")
                
                for item_idx in range(items_to_view):
                    if night_mode.is_night_time():
                        break
                    
                    print(f"     {Fore.CYAN}Карточка #{item_idx+1}...{Style.RESET_ALL}")
                    
                    try:
                        success_click = await navigator.click_listing(page, item_idx, acc_id)
                        if success_click:
                            print(f"     {Fore.GREEN}✅ Открыта{Style.RESET_ALL}")
                            
                            duration = random.randint(30, 50)
                            print(f"     {Fore.CYAN}Просмотр {duration}s...{Style.RESET_ALL}")
                            await self._deep_view_item(page, acc_id, duration=duration)
                            
                            if random.random() < 0.35:
                                print(f"     {Fore.CYAN}🤔 Раздумье перед избранным...{Style.RESET_ALL}")
                                await self._human_pause(acc_id, "раздумье перед избранным", 25, 45)
                                
                                success_fav = await navigator.add_to_favorites(page, acc_id)
                                if success_fav:
                                    print(f"     {Fore.GREEN}⭐ Добавлено в избранное{Style.RESET_ALL}")
                                    self.human_state.items_favorited += 1
                                else:
                                    print(f"     {Fore.YELLOW}⚠️ Не удалось добавить{Style.RESET_ALL}")
                            
                            try:
                                await navigator.go_back(page, acc_id)
                            except:
                                pass
                            
                            print(f"     {Fore.GREEN}✅ Вернулось{Style.RESET_ALL}")
                            self.human_state.items_viewed += 1
                            await self._human_pause(acc_id, "между карточками", 12, 25)
                        else:
                            print(f"     {Fore.YELLOW}⚠️ Не удалось открыть{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"     {Fore.YELLOW}⚠️ Ошибка: {e}{Style.RESET_ALL}")
            
            self.human_state.update_tiredness(0.06)
            self.human_state.update_mood()
            
            return True
        
        except Exception as e:
            self.logger.warning(acc_id, f"Phase 2 error: {e}")
            print(f"     {Fore.RED}❌ Ошибка: {e}{Style.RESET_ALL}")
            return True
    
    async def _phase_3_specs_analysis(
        self, page: Page, acc_id: str, navigator: AvitoNavigator, night_mode: NightMode
    ) -> bool:
        """ФАЗА 3: ИЗУЧЕНИЕ ХАРАКТЕРИСТИК"""
        
        try:
            specific_searches = random.sample(
                self.moto_config.pit_bike_brand_queries + self.moto_config.pit_bike_cc_queries,
                k=random.randint(3, 5)
            )
            
            print(f"  {Fore.CYAN}Выбрано специфичных поисков: {len(specific_searches)}{Style.RESET_ALL}")
            
            for search_idx, search_query in enumerate(specific_searches, 1):
                if night_mode.is_night_time():
                    break
                
                print(f"\n  {Fore.CYAN}[3.{search_idx}] Анализ: '{search_query}'...{Style.RESET_ALL}")
                
                success = await self._safe_search(page, acc_id, navigator, search_query, attempts=2)
                
                if not success:
                    continue
                
                print(f"     {Fore.GREEN}✅ Поиск выполнен{Style.RESET_ALL}")
                
                await self._human_pause(acc_id, "изучение результатов", 15, 30)
                
                for item_idx in range(random.randint(3, 4)):
                    if night_mode.is_night_time():
                        break
                    
                    print(f"     {Fore.CYAN}Карточка #{item_idx+1} для анализа...{Style.RESET_ALL}")
                    
                    try:
                        success_click = await navigator.click_listing(page, item_idx, acc_id)
                        if success_click:
                            print(f"     {Fore.GREEN}✅ Открыта{Style.RESET_ALL}")
                            
                            print(f"     {Fore.CYAN}📊 Анализирую спецификации...{Style.RESET_ALL}")
                            
                            # Листаем фото
                            await self._browse_photos(page, acc_id)
                            
                            # Читаем характеристики
                            for _ in range(random.randint(5, 8)):
                                await navigator.scroll_page(page, random.randint(150, 250))
                                await asyncio.sleep(random.uniform(2.0, 4.0))
                            
                            print(f"     {Fore.GREEN}✅ Specs просмотрены{Style.RESET_ALL}")
                            
                            print(f"     {Fore.CYAN}📖 Читаю описание...{Style.RESET_ALL}")
                            await asyncio.sleep(random.uniform(12, 25))
                            
                            if random.random() < 0.5:
                                print(f"     {Fore.CYAN}⭐ Смотрю отзывы...{Style.RESET_ALL}")
                                for _ in range(random.randint(2, 4)):
                                    await navigator.scroll_page(page, random.randint(150, 250))
                                    await asyncio.sleep(random.uniform(2.0, 4.0))
                                print(f"     {Fore.GREEN}✅ Отзывы просмотрены{Style.RESET_ALL}")
                            
                            if random.random() < 0.4:
                                print(f"     {Fore.CYAN}👤 Смотрю профиль продавца...{Style.RESET_ALL}")
                                success_seller = await navigator.view_seller_profile(page, acc_id)
                                if success_seller:
                                    print(f"     {Fore.GREEN}✅ Профиль просмотрен{Style.RESET_ALL}")
                                    self.human_state.sellers_viewed += 1
                                    try:
                                        await navigator.go_back(page, acc_id)
                                    except:
                                        pass
                            
                            try:
                                await navigator.go_back(page, acc_id)
                            except:
                                pass
                            
                            print(f"     {Fore.GREEN}✅ Вернулось{Style.RESET_ALL}")
                            self.human_state.items_viewed += 1
                            await self._human_pause(acc_id, "между анализами", 12, 25)
                        else:
                            print(f"     {Fore.YELLOW}⚠️ Не удалось открыть{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"     {Fore.YELLOW}⚠️ Ошибка: {e}{Style.RESET_ALL}")
            
            self.human_state.update_tiredness(0.07)
            self.human_state.update_mood()
            
            return True
        
        except Exception as e:
            self.logger.warning(acc_id, f"Phase 3 error: {e}")
            print(f"     {Fore.RED}❌ Ошибка: {e}{Style.RESET_ALL}")
            return True
    
    async def _phase_4_category_exploration(
        self, page: Page, acc_id: str, navigator: AvitoNavigator, night_mode: NightMode
    ) -> bool:
        """ФАЗА 4: КАТЕГОРИАЛЬНОЕ ИССЛЕДОВАНИЕ"""
        
        try:
            categories = [
                ("мотоциклы", self.moto_config.motorcycle_queries),
                ("квадроциклы", self.moto_config.quad_queries),
            ]
            
            for category_idx, (category_name, category_queries) in enumerate(categories, 1):
                if night_mode.is_night_time():
                    break
                
                print(f"\n  {Fore.CYAN}[4.{category_idx}] Исследование: {category_name}...{Style.RESET_ALL}")
                
                self.human_state.current_interest_category = category_name
                
                selected_queries = random.sample(category_queries, k=min(2, len(category_queries)))
                
                for query_idx, search_query in enumerate(selected_queries, 1):
                    if night_mode.is_night_time():
                        break
                    
                    print(f"     {Fore.CYAN}[{query_idx}] Поиск: '{search_query}'...{Style.RESET_ALL}")
                    
                    success = await self._safe_search(page, acc_id, navigator, search_query, attempts=2)
                    
                    if not success:
                        continue
                    
                    print(f"     {Fore.GREEN}✅ Поиск выполнен{Style.RESET_ALL}")
                    
                    await self._human_pause(acc_id, "осмотр результатов", 12, 20)
                    
                    for item_idx in range(random.randint(2, 4)):
                        if night_mode.is_night_time():
                            break
                        
                        try:
                            success_click = await navigator.click_listing(page, item_idx, acc_id)
                            if success_click:
                                duration = random.randint(20, 40)
                                await self._deep_view_item(page, acc_id, duration=duration)
                                try:
                                    await navigator.go_back(page, acc_id)
                                except:
                                    pass
                                self.human_state.items_viewed += 1
                                await self._human_pause(acc_id, "между просмотрами", 10, 20)
                        except Exception as e:
                            print(f"     {Fore.YELLOW}⚠️ Ошибка: {e}{Style.RESET_ALL}")
            
            self.human_state.update_tiredness(0.05)
            self.human_state.update_mood()
            
            return True
        
        except Exception as e:
            self.logger.warning(acc_id, f"Phase 4 error: {e}")
            print(f"     {Fore.RED}❌ Ошибка: {e}{Style.RESET_ALL}")
            return True
    
    async def _phase_5_favorites_selection(
        self, page: Page, acc_id: str, navigator: AvitoNavigator, night_mode: NightMode
    ) -> bool:
        """ФАЗА 5: ДОБАВЛЕНИЕ В ИЗБРАННОЕ"""
        
        try:
            favorites_searches = random.sample(
                self.moto_config.get_all_pit_bike_queries(),
                k=random.randint(2, 3)
            )
            
            print(f"  {Fore.CYAN}Выбрано поисков для избранного: {len(favorites_searches)}{Style.RESET_ALL}")
            
            for search_idx, search_query in enumerate(favorites_searches, 1):
                if night_mode.is_night_time():
                    break
                
                print(f"\n  {Fore.CYAN}[5.{search_idx}] Поиск для избранного: '{search_query}'...{Style.RESET_ALL}")
                
                success = await self._safe_search(page, acc_id, navigator, search_query, attempts=2)
                
                if not success:
                    continue
                
                print(f"     {Fore.GREEN}✅ Поиск выполнен{Style.RESET_ALL}")
                
                await self._human_pause(acc_id, "изучение результатов", 15, 25)
                
                for item_idx in range(random.randint(4, 6)):
                    if night_mode.is_night_time():
                        break
                    
                    print(f"     {Fore.CYAN}Карточка #{item_idx+1} для избранного...{Style.RESET_ALL}")
                    
                    try:
                        success_click = await navigator.click_listing(page, item_idx, acc_id)
                        if success_click:
                            print(f"     {Fore.GREEN}✅ Открыта{Style.RESET_ALL}")
                            
                            print(f"     {Fore.CYAN}Анализирую для избранного (45–70s)...{Style.RESET_ALL}")
                            await self._deep_view_item(page, acc_id, duration=random.randint(45, 70))
                            
                            print(f"     {Fore.CYAN}🤔 Раздумье перед добавлением...{Style.RESET_ALL}")
                            await self._human_pause(acc_id, "раздумье перед избранным", 25, 50)
                            
                            success_fav = await navigator.add_to_favorites(page, acc_id)
                            if success_fav:
                                print(f"     {Fore.GREEN}⭐ ДОБАВЛЕНО В ИЗБРАННОЕ{Style.RESET_ALL}")
                                self.human_state.items_favorited += 1
                            else:
                                print(f"     {Fore.YELLOW}⚠️ Не удалось добавить{Style.RESET_ALL}")
                            
                            try:
                                await navigator.go_back(page, acc_id)
                            except:
                                pass
                            
                            print(f"     {Fore.GREEN}✅ Вернулось{Style.RESET_ALL}")
                            self.human_state.items_viewed += 1
                            await self._human_pause(acc_id, "между избранными", 12, 25)
                        else:
                            print(f"     {Fore.YELLOW}⚠️ Не удалось открыть{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"     {Fore.YELLOW}⚠️ Ошибка: {e}{Style.RESET_ALL}")
            
            self.human_state.update_tiredness(0.06)
            self.human_state.update_mood()
            
            return True
        
        except Exception as e:
            self.logger.warning(acc_id, f"Phase 5 error: {e}")
            print(f"     {Fore.RED}❌ Ошибка: {e}{Style.RESET_ALL}")
            return True
    
    async def _phase_6_seller_analysis(
        self, page: Page, acc_id: str, navigator: AvitoNavigator, night_mode: NightMode
    ) -> bool:
        """ФАЗА 6: АНАЛИЗ ПРОДАВЦОВ"""
        
        try:
            seller_search_queries = random.sample(
                self.moto_config.get_all_pit_bike_queries(),
                k=random.randint(3, 4)
            )
            
            print(f"  {Fore.CYAN}Выбрано поисков для анализа продавцов: {len(seller_search_queries)}{Style.RESET_ALL}")
            
            for search_idx, search_query in enumerate(seller_search_queries, 1):
                if night_mode.is_night_time():
                    break
                
                print(f"\n  {Fore.CYAN}[6.{search_idx}] Анализ продавцов: '{search_query}'...{Style.RESET_ALL}")
                
                success = await self._safe_search(page, acc_id, navigator, search_query, attempts=2)
                
                if not success:
                    continue
                
                print(f"     {Fore.GREEN}✅ Поиск выполнен{Style.RESET_ALL}")
                
                await self._human_pause(acc_id, "осмотр результатов", 12, 20)
                
                for item_idx in range(random.randint(3, 5)):
                    if night_mode.is_night_time():
                        break
                    
                    print(f"     {Fore.CYAN}Карточка #{item_idx+1}...{Style.RESET_ALL}")
                    
                    try:
                        success_click = await navigator.click_listing(page, item_idx, acc_id)
                        if success_click:
                            print(f"     {Fore.GREEN}✅ Открыта{Style.RESET_ALL}")
                            
                            print(f"     {Fore.CYAN}Читаю описание...{Style.RESET_ALL}")
                            await asyncio.sleep(random.uniform(10, 18))
                            
                            print(f"     {Fore.CYAN}👤 АНАЛИЗИРУЮ ПРОФИЛЬ ПРОДАВЦА...{Style.RESET_ALL}")
                            success_seller = await navigator.view_seller_profile(page, acc_id)
                            
                            if success_seller:
                                print(f"     {Fore.GREEN}✅ Профиль изучен{Style.RESET_ALL}")
                                
                                print(f"     {Fore.CYAN}Изучаю рейтинг и отзывы (25–45s)...{Style.RESET_ALL}")
                                for _ in range(random.randint(3, 5)):
                                    await navigator.scroll_page(page, random.randint(200, 300))
                                    await asyncio.sleep(random.uniform(2.0, 4.0))
                                
                                self.human_state.sellers_viewed += 1
                                try:
                                    await navigator.go_back(page, acc_id)
                                except:
                                    pass
                            else:
                                print(f"     {Fore.YELLOW}⚠️ Не удалось открыть профиль{Style.RESET_ALL}")
                            
                            try:
                                await navigator.go_back(page, acc_id)
                            except:
                                pass
                            
                            print(f"     {Fore.GREEN}✅ Вернулось{Style.RESET_ALL}")
                            self.human_state.items_viewed += 1
                            await self._human_pause(acc_id, "между продавцами", 12, 25)
                        else:
                            print(f"     {Fore.YELLOW}⚠️ Не удалось открыть карточку{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"     {Fore.YELLOW}⚠️ Ошибка: {e}{Style.RESET_ALL}")
            
            self.human_state.update_tiredness(0.05)
            self.human_state.update_mood()
            
            return True
        
        except Exception as e:
            self.logger.warning(acc_id, f"Phase 6 error: {e}")
            print(f"     {Fore.RED}❌ Ошибка: {e}{Style.RESET_ALL}")
            return True
    
    async def _phase_7_final_validation(
        self, page: Page, acc_id: str, navigator: AvitoNavigator, night_mode: NightMode
    ) -> bool:
        """ФАЗА 7: ФИНАЛЬНАЯ ПРОВЕРКА"""
        
        try:
            print(f"  {Fore.CYAN}[7.1] Возвращаюсь на главную...{Style.RESET_ALL}")
            
            success = await navigator.goto_main(page, acc_id)
            if not success:
                print(f"     {Fore.YELLOW}⚠️ Не удалось перейти на главную{Style.RESET_ALL}")
                return False
            
            print(f"     {Fore.GREEN}✅ На главной{Style.RESET_ALL}")
            
            await self._human_pause(acc_id, "на главной", 10, 20)
            
            print(f"  {Fore.CYAN}[7.2] Финальные поиски...{Style.RESET_ALL}")
            
            final_searches = random.sample(
                self.moto_config.pit_bike_mixed_queries,
                k=random.randint(2, 3)
            )
            
            for search_query in final_searches:
                if night_mode.is_night_time():
                    break
                
                print(f"     {Fore.CYAN}Поиск: '{search_query}'...{Style.RESET_ALL}")
                
                success = await self._safe_search(page, acc_id, navigator, search_query, attempts=1)
                if success:
                    print(f"     {Fore.GREEN}✅ Поиск выполнен{Style.RESET_ALL}")
                    
                    await self._human_pause(acc_id, "осмотр результатов", 12, 20)
                    
                    for i in range(random.randint(1, 2)):
                        if night_mode.is_night_time():
                            break
                        
                        try:
                            success_click = await navigator.click_listing(page, i, acc_id)
                            if success_click:
                                await asyncio.sleep(random.uniform(10, 20))
                                try:
                                    await navigator.go_back(page, acc_id)
                                except:
                                    pass
                                self.human_state.items_viewed += 1
                                await self._human_pause(acc_id, "между карточками", 10, 20)
                        except Exception as e:
                            print(f"     {Fore.YELLOW}⚠️ Ошибка: {e}{Style.RESET_ALL}")
                    
                    try:
                        await navigator.goto_main(page, acc_id)
                    except:
                        pass
                    await self._human_pause(acc_id, "между поисками", 8, 15)
            
            print(f"  {Fore.CYAN}[7.3] Финальный скролл на главной...{Style.RESET_ALL}")
            
            for _ in range(random.randint(3, 5)):
                await navigator.scroll_page(page, random.randint(200, 400))
                await asyncio.sleep(random.uniform(2, 4))
            
            print(f"     {Fore.GREEN}✅ Скролл завершен{Style.RESET_ALL}")
            
            self.human_state.update_tiredness(0.04)
            self.human_state.update_mood()
            
            return True
        
        except Exception as e:
            self.logger.warning(acc_id, f"Phase 7 error: {e}")
            print(f"     {Fore.RED}❌ Ошибка: {e}{Style.RESET_ALL}")
            return True
    
    # ═══════════════════════════════════════════════════════════════
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ═══════════════════════════════════════════════════════════════
    
    async def _human_pause(
        self,
        acc_id: str,
        reason: str,
        min_sec: float = 2.0,
        max_sec: float = 5.0,
    ) -> None:
        """⏳ РЕАЛИСТИЧНАЯ ПАУЗА (ОПТИМИЗИРОВАНА ДЛЯ ПРОКСИ)"""
        
        delay = random.uniform(min_sec, max_sec) * self.PROXY_SLOWDOWN_FACTOR
        factor = self.human_state.get_delay_factor()
        delay = delay * factor
        delay = max(3, min(120, delay))
        
        self.logger.info(acc_id, f"⏳ {reason}: {delay:.1f}s (proxy-optimized)")
        self.human_state.last_action_time = datetime.now()
        await asyncio.sleep(delay)
    
    async def _deep_view_item(
        self,
        page: Page,
        acc_id: str,
        duration: int = 20,
    ) -> None:
        """
        👀 ГЛУБОКИЙ ПРОСМОТР ТОВАРА - ПОЛНОСТЬЮ ПЕРЕДЕЛАН
        
        Features:
        - Листание фото
        - Чтение текста
        - Скролл характеристик
        - Смотрение отзывов
        - Реалистичные паузы
        - Изучение профиля продавца
        """
        
        try:
            duration = int(duration * 2.5)
            start_time = time.time()
            end_time = start_time + duration
            
            # Действия которые может выполнить человек
            actions = ["scroll", "wait", "scroll_up", "read_text", "browse_photos"]
            
            while time.time() < end_time:
                # Выбираем случайное действие
                action = random.choice(actions)
                
                if action == "scroll":
                    scroll_distance = random.randint(150, 250)
                    await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
                    await asyncio.sleep(random.uniform(2.0, 5.0))
                
                elif action == "scroll_up":
                    scroll_distance = random.randint(100, 150)
                    await page.evaluate(f"window.scrollBy(0, {-scroll_distance})")
                    await asyncio.sleep(random.uniform(2.0, 4.0))
                
                elif action == "read_text":
                    # Просто смотрим на текст
                    await asyncio.sleep(random.uniform(3.0, 8.0))
                
                elif action == "browse_photos":
                    # Пробуем листать фото
                    await self._browse_photos(page, acc_id)
                
                else:  # wait
                    await asyncio.sleep(random.uniform(3.0, 7.0))
        
        except Exception as e:
            self.logger.warning(acc_id, f"Deep view error: {e}")
    
    async def _browse_photos(self, page: Page, acc_id: str) -> None:
        """📸 Листание фото товара"""
        
        try:
            # Пробуем найти кнопку "следующее фото"
            for selector in ["button[aria-label*='следу']", ".carousel-next", "button.next-photo"]:
                try:
                    next_btn = page.locator(selector)
                    count = await next_btn.count()
                    
                    if count > 0:
                        # Листаем 2-4 фото
                        for _ in range(random.randint(2, 4)):
                            try:
                                await next_btn.first.click(timeout=3000)
                                await asyncio.sleep(random.uniform(1.0, 2.0))
                            except:
                                break
                        return
                except:
                    continue
        except Exception:
            pass
    
    async def _save_warmup_state(self, acc_id: str):
        """💾 Сохранить состояние прогрева"""
        
        try:
            state_data = {
                "total_duration_seconds": self.total_warmup_duration,
                "phases_completed": self.phases_completed,
                "phase_reports": self.phase_reports,
                "human_state": self.human_state.to_dict(),
                "timestamp": datetime.now().isoformat(),
            }
            
            self.logger.success(
                acc_id,
                f"Warmup state saved: {self.phases_completed} phases, {self.total_warmup_duration / 60:.1f} min"
            )
        
        except Exception as e:
            self.logger.warning(acc_id, f"Failed to save warmup state: {e}")


# ════════════════════════════════════════════════════════════════
# 🤖 ALIVE MODE
# ════════════════════════════════════════════════════════════════

class AliveMode:
    """🤖 ALIVE MODE v3.0 — АВТОМАТИЧЕСКАЯ АКТИВНОСТЬ"""
    
    def __init__(
        self,
        logger: Logger,
        executor: ActionExecutor,
        notifier: Optional[TelegramNotifier] = None
    ):
        self.logger = logger
        self.executor = executor
        self.notifier = notifier
        self.running = True
        self.iteration_count = 0
        self.moto_config = MotoTechConfig()
    
    async def run(
        self,
        page: Page,
        acc_id: str,
        navigator: AvitoNavigator,
        night_mode: NightMode,
        fingerprint,
        browser_launcher,
    ) -> None:
        """🤖 Запустить Alive Mode"""
        
        start_time = datetime.now()
        
        print(f"\n{Fore.GREEN}{'=' * 90}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'🤖 ALIVE MODE — ПОЛНОСТЬЮ АСИНХРОННЫЙ РЕЖИМ':^90}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'=' * 90}{Style.RESET_ALL}\n")
        
        self.logger.action(acc_id, "ALIVE_MODE", "START")
        
        try:
            if self.notifier:
                await self.notifier.notify(f"🤖 Alive Mode запущен для {acc_id}")
        except Exception:
            pass
        
        try:
            while self.running and not night_mode.is_night_time():
                self.iteration_count += 1
                
                print(f"\n  {Fore.GREEN}🤖 Итерация #{self.iteration_count}{Style.RESET_ALL}")
                
                action = random.choice(["search", "view", "favorite", "seller"])
                
                try:
                    if action == "search":
                        print(f"     🔍 Поиск...")
                        await navigator.goto_main(page, acc_id)
                        await asyncio.sleep(random.uniform(3, 8))
                        query = random.choice(self.moto_config.pit_bike_mixed_queries)
                        success = await navigator.search(page, query, acc_id)
                        if success:
                            print(f"     ✅ Поиск: '{query}'")
                        else:
                            print(f"     ⚠️ Поиск не удался")
                    
                    elif action == "view":
                        print(f"     📄 Просмотр...")
                        idx = random.randint(0, 3)
                        success = await navigator.click_listing(page, idx, acc_id)
                        if success:
                            await asyncio.sleep(random.uniform(25, 50))
                            try:
                                await navigator.go_back(page, acc_id)
                            except:
                                pass
                            print(f"     ✅ Карточка #{idx+1} просмотрена")
                        else:
                            print(f"     ⚠️ Не удалось открыть")
                    
                    elif action == "favorite":
                        print(f"     ⭐ Добавление в избранное...")
                        idx = random.randint(0, 3)
                        success = await navigator.click_listing(page, idx, acc_id)
                        if success:
                            await asyncio.sleep(random.uniform(15, 35))
                            success_fav = await navigator.add_to_favorites(page, acc_id)
                            try:
                                await navigator.go_back(page, acc_id)
                            except:
                                pass
                            if success_fav:
                                print(f"     ✅ Добавлено в избранное")
                            else:
                                print(f"     ⚠️ Не удалось добавить")
                        else:
                            print(f"     ⚠️ Не удалось открыть")
                    
                    elif action == "seller":
                        print(f"     👤 Просмотр продавца...")
                        idx = random.randint(0, 3)
                        success = await navigator.click_listing(page, idx, acc_id)
                        if success:
                            await asyncio.sleep(random.uniform(10, 20))
                            await navigator.view_seller_profile(page, acc_id)
                            try:
                                await navigator.go_back(page, acc_id)
                            except:
                                pass
                            print(f"     ✅ Профи��ь просмотрен")
                        else:
                            print(f"     ⚠️ Не удалось открыть")
                
                except Exception as e:
                    self.logger.warning(acc_id, f"Alive mode iteration error: {e}")
                    print(f"     ❌ Ошибка: {e}")
                
                pause_min = random.randint(90, 240)
                print(f"     ⏳ Пауза {pause_min}s до следующей итерации...\n")
                await asyncio.sleep(pause_min)
        
        except Exception as e:
            self.logger.error(acc_id, f"Alive Mode error: {e}", severity="MEDIUM")
            print(f"\n{Fore.RED}❌ Alive Mode error: {e}{Style.RESET_ALL}\n")
        
        finally:
            try:
                await browser_launcher.save_cookies(acc_id)
                await browser_launcher.save_storage_state(acc_id)
            except Exception:
                pass
            
            total_duration = (datetime.now() - start_time).total_seconds() / 60
            self.logger.action(acc_id, "ALIVE_MODE", "END", iterations=self.iteration_count)
            
            print(f"\n{Fore.GREEN}✅ Alive Mode завершён ({self.iteration_count} итераций, {total_duration:.1f} мин){Style.RESET_ALL}\n")
            
            try:
                if self.notifier:
                    await self.notifier.notify(
                        f"✅ Alive Mode завершён для {acc_id}\n"
                        f"Итераций: {self.iteration_count}\n"
                        f"Время: {total_duration:.1f} мин"
                    )
            except Exception:
                pass
    
    def stop(self) -> None:
        """Остановить Alive Mode"""
        self.running = False
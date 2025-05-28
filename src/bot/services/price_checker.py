import asyncio
import logging
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session
from aiogram import Bot

from src.bot.database.main import get_db
from src.bot.database.models.track import Track
from src.driver.browser import ChromeDriver
from src.page_objects.price import OzonPrice, WildberriesPrice

logger = logging.getLogger(__name__)

class PriceChecker:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.driver = None

    async def start(self):
        """Запускает периодическую проверку цен"""
        while True:
            try:
                await self.check_prices()
            except Exception as e:
                logger.error(f"Ошибка в price checker: {str(e)}")
            await asyncio.sleep(3600)  # Проверяем каждый час

    async def check_prices(self):
        """Проверяет цены для всех активных отслеживаний"""
        try:
            # Получаем сессию базы данных
            db = next(get_db())
            try:
                # Получаем все активные отслеживания
                tracks = self._get_active_tracks(db)
                
                if not tracks:
                    logger.info("Нет активных отслеживаний для проверки")
                    return
                
                logger.info(f"Найдено {len(tracks)} активных отслеживаний")
                
                # Инициализируем драйвер
                self.driver = ChromeDriver.get()
                
                try:
                    # Проверяем цены для каждого отслеживания
                    for track in tracks:
                        await self._check_track_price(track, db)
                finally:
                    # Закрываем драйвер
                    if self.driver:
                        self.driver.quit()
                        self.driver = None
            finally:
                # Закрываем сессию базы данных
                db.close()
                        
        except Exception as e:
            logger.error(f"Ошибка при проверке цен: {str(e)}")
            if self.driver:
                self.driver.quit()
                self.driver = None

    def _get_active_tracks(self, db: Session) -> List[Track]:
        """Получает список активных отслеживаний"""
        return db.query(Track).filter(Track.is_active == True).all()

    async def _check_track_price(self, track: Track, db: Session):
        """Проверяет цену для одного отслеживания"""
        try:
            logger.info(f"Проверка цены для отслеживания {track.id}")
            logger.info(f"Переход по URL: {track.product_url}")
            
            # Переходим на страницу товара
            self.driver.get(track.product_url)
            
            # Получаем цену в зависимости от маркетплейса
            if track.marketplace == "ozon":
                price = OzonPrice(self.driver).get_price()
            elif track.marketplace == "wildberries":
                price = WildberriesPrice(self.driver).get_price()
            else:
                logger.error(f"Неизвестный маркетплейс: {track.marketplace}")
                return
            
            # Обновляем текущую цену
            track.current_price = price
            track.last_check = datetime.now()
            
            # Если цена достигла целевой, деактивируем отслеживание и уведомляем
            if price <= track.target_price:
                track.is_active = False
                logger.info(f"Цена достигла целевой для отслеживания {track.id}")
                await self.notify_price_drop(track, price)
            
            db.commit()
            logger.info(f"Цена обновлена для отслеживания {track.id}: {price}")
            
        except Exception as e:
            logger.error(f"Ошибка при проверке цены для отслеживания {track.id}: {str(e)}")
            db.rollback()

    async def notify_price_drop(self, track: Track, current_price: float):
        """Отправляет уведомление о падении цены"""
        user = track.user
        message = (
            f"🎉 Цена на товар упала!\n\n"
            f"🛍 Товар: {track.product_url}\n"
            f"💰 Текущая цена: {current_price}₽\n"
            f"🎯 Ваша целевая цена: {track.target_price}₽\n"
            f"🏪 Магазин: {track.marketplace}\n\n"
            f"ℹ️ Отслеживание цены автоматически удалено, так как цена достигла целевой.\n"
            f"Вы можете добавить новый товар для отслеживания, используя команду /add"
        )
        
        await self.bot.send_message(user.user_id, message) 
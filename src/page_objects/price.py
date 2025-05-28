from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OzonPrice:
    _SEARCHBOX = "div[data-widget='webPrice']"

    def __init__(self, driver):
        self.driver = driver

    def get_price(self) -> float:
        try:
            logger.info("🔍 Ищу цену на Ozon...")
            # Ждем появления элемента до 30 секунд
            wait = WebDriverWait(self.driver, 30)
            
            logger.info("⏳ Ожидаю загрузку элемента цены...")
            
            element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self._SEARCHBOX))
            )
            
            price_text = element.text
            
            logger.info(f"📝 Найден текст цены: {price_text}")
            
            price = re.sub(r'[^\d]', '', price_text)
            result = float(price) if price else 0.0
            
            logger.info(f"💰 Обработанная цена: {result}")

            return result
        except (TimeoutException, NoSuchElementException, ValueError) as e:
            logger.error(f"❌ Ошибка при получении цены Ozon: {str(e)}")
            return 0.0


class WildberriesPrice:
    _PRICE_XPATH = "/html/body/div[1]/main/div[2]/div[2]/div[3]/div/div[3]/div[13]/div/div[1]/div[2]/div/div/div/p/span/ins"

    def __init__(self, driver):
        self.driver = driver

    def get_price(self) -> float:
        try:
            logger.info("🔍 Ищу цену на Wildberries...")
            # Ждем появления элемента до 30 секунд
            wait = WebDriverWait(self.driver, 30)
            
            logger.info("⏳ Ожидаю загрузку элемента цены...")
            
            element = wait.until(
                EC.presence_of_element_located((By.XPATH, self._PRICE_XPATH))
            )
            
            price_text = element.text
            
            logger.info(f"📝 Найден текст цены: {price_text}")
            
            # Удаляем все символы кроме цифр
            price = re.sub(r'[^\d]', '', price_text)
            result = float(price) if price else 0.0
            
            logger.info(f"💰 Обработанная цена: {result}")
            
            return result
        except (TimeoutException, NoSuchElementException, ValueError) as e:
            logger.error(f"❌ Ошибка при получении цены Wildberries: {str(e)}")
            return 0.0
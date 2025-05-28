import undetected_chromedriver as uc
import logging

logger = logging.getLogger(__name__)

class ChromeDriver:
    @staticmethod
    def get() -> uc.Chrome:
        try:
            logger.info("🚀 Инициализация Chrome драйвера...")
            
            # Создаем драйвер с базовыми настройками
            driver = uc.Chrome(
                version_main=136,
                headless=False,
                driver_executable_path=None  # Пусть undetected_chromedriver сам найдет драйвер
            )
            
            # Базовые настройки
            driver.maximize_window()
            driver.implicitly_wait(30)
            
            logger.info("✅ Chrome драйвер успешно инициализирован")
            return driver
            
        except Exception as e:
            logger.error(f"❌ Ошибка при инициализации Chrome драйвера: {str(e)}")
            raise
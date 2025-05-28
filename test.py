import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.driver.browser import ChromeDriver
from src.page_objects.price import OzonPrice, WildberriesPrice


def get_ozon_price(driver: uc.Chrome) -> int:
    driver.get("https://www.ozon.ru/product/solntsezashchitnyy-krem-dlya-litsa-i-tela-7days-spf-30-200-ml-930525870/")

    ozon_price = OzonPrice(driver)
    price = ozon_price.get_price()

    return price


def get_wildberries_price(driver: uc.Chrome) -> int:
    driver.get("https://www.wildberries.ru/catalog/303240677/detail.aspx")

    wildberries_price = WildberriesPrice(driver)
    price = wildberries_price.get_price()

    return price


def main():
    driver = ChromeDriver.get()
    get_wildberries_price(driver)
    time.sleep(5)
    driver.quit()


def test_wildberries_price():
    # Настраиваем Chrome
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options, version_main=136)
    
    try:
        # Открываем страницу товара
        url = "https://www.wildberries.ru/catalog/303240677/detail.aspx"
        print("🌐 Открываю страницу товара...")
        driver.get(url)
        
        print("\n⏳ Ожидаю загрузку элемента цены (до 30 секунд)...")
        xpath = "/html/body/div[1]/main/div[2]/div[2]/div[3]/div/div[3]/div[13]/div/div[1]/div[2]/div/div/div/p/span/ins"
        
        try:
            # Ждем появления элемента до 30 секунд
            wait = WebDriverWait(driver, 30)
            element = wait.until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            
            print(f"\n✅ Элемент найден:")
            print(f"Текст: {element.text}")
            print(f"HTML: {element.get_attribute('outerHTML')}")
        except Exception as e:
            print(f"❌ Ошибка при поиске элемента: {str(e)}")
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
    finally:
        driver.quit()


if __name__ == "__main__":
    test_wildberries_price()
    
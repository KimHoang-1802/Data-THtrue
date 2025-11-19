from services.selenium_service import SeleniumService
from services.parser_service import ParserService
from services.database_service import DatabaseService
from utils.logger import get_logger
import time
from selenium.webdriver.common.by import By

logger = get_logger("controller")

class ProductController:

    def __init__(self, headless=True):
        self.selenium = SeleniumService(headless=headless)
        self.parser = ParserService()
        self.db = DatabaseService()

    def crawl_category(self, url):
        logger.info(f"Truy cập URL: {url}")
        self.selenium.get_page(url, wait=2)

        products = []

        # --- Trang 1 ---
        logger.info("Scroll trang 1...")
        self.selenium.scroll_to_bottom(pause=1.0, max_scrolls=8)

        html1 = self.selenium.driver.page_source
        page1_products = self.parser.parse_products_from_html(html1)
        products.extend(page1_products)

        # --- Page 2 ---
        logger.info("Tìm nút trang 2...")
        try:
            page_buttons = self.selenium.driver.find_elements(
                By.CSS_SELECTOR,
                "button.tile-module__root___Oo1HI, button[class*='tile-module__root']"
            )

            page2_btn = None
            for btn in page_buttons:
                if btn.text.strip() == "2":
                    page2_btn = btn
                    break

            if page2_btn:
                self.selenium.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", page2_btn
                )
                time.sleep(1)
                try:
                    page2_btn.click()
                except:
                    self.selenium.driver.execute_script("arguments[0].click();", page2_btn)

                time.sleep(3)
                self.selenium.scroll_to_bottom(pause=1.0, max_scrolls=6)

                html2 = self.selenium.driver.page_source
                page2_products = self.parser.parse_products_from_html(html2)
                products.extend(page2_products)

        except Exception as e:
            logger.error(f"Lỗi phân trang: {e}")

        self.selenium.quit()

        # Lọc trùng
        unique = {p.name.lower(): p for p in products}
        result = list(unique.values())

        logger.info(f"Tổng sản phẩm: {len(result)}")

        # Lưu database
        for p in result:
            self.db.insert_product(p)

        self.db.close()

        return result

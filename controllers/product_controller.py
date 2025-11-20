# Vai trò: Orchestrator - điều phối toàn bộ luồng crawl
# Khởi tạo 3 services: Selenium, Parser, Database
# 1. Mở trang 1 → Scroll → Parse → Lưu tạm
# 2. Click nút "2" → Mở trang 2 → Scroll → Parse → Lưu tạm
# 3. Lọc trùng lặp (theo tên sản phẩm)
# 4. Batch insert vào database
# 5. Đóng tất cả kết nối
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
        self.selenium.get_page(url, wait=3)

        products = []

        # --- Trang 1 ---
        logger.info("Đang crawl trang 1...")
        self.selenium.scroll_to_bottom(pause=1.5, max_scrolls=10)
        time.sleep(2)  # Đợi load hết

        html1 = self.selenium.driver.page_source
        page1_products = self.parser.parse_products_from_html(html1)
        products.extend(page1_products)
        logger.info(f"✓ Trang 1: {len(page1_products)} sản phẩm")

        # --- Page 2 ---
        logger.info("Đang tìm và chuyển sang trang 2...")
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
                time.sleep(1.5)
                try:
                    page2_btn.click()
                except:
                    self.selenium.driver.execute_script("arguments[0].click();", page2_btn)

                time.sleep(4)  # Tăng thời gian đợi
                logger.info("Đang crawl trang 2...")
                self.selenium.scroll_to_bottom(pause=1.5, max_scrolls=10)
                time.sleep(2)  # Đợi load hết

                html2 = self.selenium.driver.page_source
                page2_products = self.parser.parse_products_from_html(html2)
                products.extend(page2_products)
                logger.info(f"✓ Trang 2: {len(page2_products)} sản phẩm")
            else:
                logger.warning("Không tìm thấy nút trang 2")

        except Exception as e:
            logger.error(f"Lỗi phân trang: {e}")

        self.selenium.quit()

        # Lọc trùng
        unique = {p.name.lower(): p for p in products}
        result = list(unique.values())

        logger.info(f"═══════════════════════════════════════")
        logger.info(f"Tổng sản phẩm: {len(result)}")
        logger.info(f"═══════════════════════════════════════")

        # Lưu database batch (một lần thay vì nhiều lần)
        if result:
            self.db.insert_products_batch(result)

        self.db.close()

        return result
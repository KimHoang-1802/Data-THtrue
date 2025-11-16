from services.selenium_service import SeleniumService
from services.parser_service import ParserService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ProductController:
    def __init__(self, headless=True):
        self.selenium = SeleniumService(headless=headless)
        self.parser = ParserService()

    def crawl_category(self, url):
        print(f"Đang truy cập: {url}")
        
        # 1. Load trang đầu tiên
        self.selenium.get_page(url, wait=3)

        # 2. Scroll để load sản phẩm
        self.selenium.scroll_to_bottom(pause=1.0, max_scrolls=10)

        # 3. Parse trang 1
        products = self.parser.parse_products_from_html(self.selenium.driver.page_source)
        print(f"Trang 1: {len(products)} sản phẩm")

        # 4. Xử lý phân trang - Attempt to load page 2
        try:
            print("Đang tìm nút chuyển trang...")

            # Tìm tất cả các nút phân trang
            page_buttons = self.selenium.driver.find_elements(
                By.CSS_SELECTOR,
                "button.tile-module__root___Oo1HI, button[class*='tile-module__root']"
            )

            # Lọc nút có text == "2"
            next_page_button = None
            for btn in page_buttons:
                if btn.text.strip() == "2":
                    next_page_button = btn
                    break

            if not next_page_button:
                print("ℹ Không tìm thấy trang 2")
            else:
                print("Đang chuyển sang trang 2...")

                # 1. Scroll nút vào giữa màn hình
                self.selenium.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    next_page_button
                )
                time.sleep(1)

                # 2. Chờ clickable
                try:
                    WebDriverWait(self.selenium.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[text()='2']"))
                    )
                except:
                    pass  # Không sao, vẫn thử click

                # 3. Thử click bình thường trước
                try:
                    next_page_button.click()
                    print("Đã click bằng Selenium (thường)")
                except:
                    print("Click thường bị chặn → dùng JavaScript click")
                    self.selenium.driver.execute_script(
                        "arguments[0].click();",
                        next_page_button
                    )

                time.sleep(3)

                # Scroll trang 2
                self.selenium.scroll_to_bottom(pause=1.0, max_scrolls=5)

                # Parse trang 2
                page2_products = self.parser.parse_products_from_html(
                    self.selenium.driver.page_source
                )

                print(f"Trang 2: {len(page2_products)} sản phẩm")
                products.extend(page2_products)

        except Exception as e:
            print(f"⚠ Lỗi khi xử lý phân trang: {e}")

        # 5. Đóng trình duyệt
        self.selenium.quit()

        # 6. Loại trùng (unique theo tên)
        unique = {}
        for p in products:
            key = p.name.strip().lower()
            if key:
                unique[key] = p

        result = list(unique.values())
        print(f"Tổng cộng: {len(result)} sản phẩm (sau loại trùng)")
        return result

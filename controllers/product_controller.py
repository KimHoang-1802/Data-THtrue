from services.selenium_service import SeleniumService
from services.parser_service import ParserService
from selenium.webdriver.common.by import By
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

        # 4. Xử lý phân trang - Lấy trang 2
        try:
            # Tìm nút trang 2
            page_buttons = self.selenium.driver.find_elements(
                By.CSS_SELECTOR, 
                "button.tile-module__root___Oo1HI, button[class*='tile-module__root']"
            )
            
            # Tìm nút có text là "2"
            next_page_button = None
            for btn in page_buttons:
                if btn.text.strip() == "2":
                    next_page_button = btn
                    break
            
            if next_page_button:
                print(" Đang chuyển sang trang 2...")
                next_page_button.click()
                time.sleep(3)  # Đợi trang load
                
                # Scroll trang 2
                self.selenium.scroll_to_bottom(pause=1.0, max_scrolls=5)
                
                # Parse trang 2
                page2_products = self.parser.parse_products_from_html(self.selenium.driver.page_source)
                print(f"Trang 2: {len(page2_products)} sản phẩm")
                products.extend(page2_products)
            else:
                print("ℹ Không tìm thấy trang 2")
                
        except Exception as e:
            print(f"⚠ Lỗi khi xử lý phân trang: {e}")

        # 5. Đóng trình duyệt
        self.selenium.quit()
        
        # 6. Loại trùng (unique by name)
        unique = {}
        for p in products:
            key = p.name.strip().lower()
            if key:
                unique[key] = p
        
        result = list(unique.values())
        print(f"Tổng cộng: {len(result)} sản phẩm (sau loại trùng)")
        return result
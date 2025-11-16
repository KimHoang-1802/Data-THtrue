# services/selenium_service.py
# Tầng Service – điều khiển Selenium load HTML, click trang, scroll…
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException
import time

class SeleniumService:
    def __init__(self, headless=True):
        options = Options()
        if headless:
            options.add_argument("--headless=new")  # new headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        # nếu chromedriver nằm ở PATH thì không cần Service(path)
        self.driver = webdriver.Chrome(options=options)

    def get_page(self, url, wait=3):
        self.driver.get(url)
        time.sleep(wait)
        return self.driver.page_source

    def click_all_tabs(self, tab_selector, wait_after_click=2):
        """
        tab_selector: CSS selector cho các nút tab (list)
        Ví dụ: ".tab-menu li" hoặc "ul.some-class li"
        """
        elems = self.driver.find_elements(By.CSS_SELECTOR, tab_selector)
        results = []
        for i, el in enumerate(elems):
            try:
                el.click()
            except (ElementClickInterceptedException, StaleElementReferenceException):
                # try JS click
                self.driver.execute_script("arguments[0].click();", el)
            time.sleep(wait_after_click)
            results.append(self.driver.page_source)
        return results

    def go_through_pagination(self, page_button_selector, parser_callback, wait_after_click=2, max_pages=50):
        """
        Click theo các nút phân trang (nếu có). parser_callback nhận driver.page_source để lấy dữ liệu.
        page_button_selector: CSS cho các nút page (ví dụ ".pagination li a" hoặc ".page-btn")
        Trả về list dữ liệu (parser_callback sẽ parse HTML và return list)
        """
        data = []
        # lấy danh sách nút hiện có
        while True:
            # parse current page
            data.extend(parser_callback(self.driver.page_source))
            # find next button (selector needs to point to the "Tiếp" or number)
            try:
                next_btn = self.driver.find_element(By.CSS_SELECTOR, page_button_selector + ".next")  # if site has .next
                if "disabled" in next_btn.get_attribute("class"):
                    break
                next_btn.click()
                time.sleep(wait_after_click)
            except Exception:
                # fallback: try to find "active" then next sibling
                try:
                    pages = self.driver.find_elements(By.CSS_SELECTOR, page_button_selector)
                    active_index = None
                    for idx, p in enumerate(pages):
                        cls = p.get_attribute("class") or ""
                        if "active" in cls or "current" in cls:
                            active_index = idx
                            break
                    if active_index is None:
                        break
                    if active_index + 1 >= len(pages):
                        break
                    pages[active_index + 1].click()
                    time.sleep(wait_after_click)
                except Exception:
                    break
        return data

    def scroll_to_bottom(self, pause=1.0, max_scrolls=30):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        while scrolls < max_scrolls:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scrolls += 1

    def quit(self):
        self.driver.quit()


# services/parser_service.py
# ==============================
# Service này chịu trách nhiệm phân tích HTML (BeautifulSoup), Vai trò: Trích xuất thông tin sản phẩm từ HTML
# để lấy: tên sản phẩm, giá, đơn vị tính, ảnh.

from bs4 import BeautifulSoup
from models.product_model import Product
from utils.logger import get_logger
import re

logger = get_logger("parser")

class ParserService:

    def parse_products_from_html(self, html):
        logger.info("Bắt đầu parse HTML")

        soup = BeautifulSoup(html, "html.parser")
        products = []

        gallery_items = soup.select_one("div.gallery-module__items___YTUpR") \
            or soup.select_one("div[class*='gallery-module__items']")

        if not gallery_items:
            logger.warning("Không tìm thấy gallery container")
            return products

        items = gallery_items.select("div.item-module__root___hJBdd") \
            or gallery_items.select("div[class*='item-module__root']")

        logger.info(f"Tìm thấy {len(items)} product items")

        for it in items:
            name_elem = (
                it.select_one("span.item-module__name__IP_3e")
                or it.select_one("span[class*='item-module__name']")
                or it.select_one("a > span")
                or it.select_one("h3")
            )

            price_wrapper = it.select_one("div[class*='item-module__price']")
            price_text = ""
            unit_text = ""

            if price_wrapper:
                final_price = price_wrapper.select_one("div[class*='finalPrice']")
                if final_price:
                    full_text = final_price.get_text("", strip=True)
                    if "/" in full_text:
                        parts = full_text.split("/", 1)
                        price_text = parts[0].strip()
                        unit_text = parts[1].strip()
                    else:
                        match = re.search(r'([\d,\.]+\s*₫)', full_text)
                        if match:
                            price_text = match.group(1).strip()

            if price_text:
                price_text = re.sub(r"[^\d]", "", price_text)
                price_text = int(price_text) if price_text.isdigit() else 0

            # image
            img = (
                it.select_one("img.item-module__image___SWy-z")
                or it.select_one("img[class*='item-module__image']")
                or it.select_one("img")
            )
            image_url = img.get("src") if img else ""

            product = Product(
                name=name_elem.get_text(strip=True) if name_elem else "",
                price=price_text,
                unit=unit_text,
                image=image_url
            )

            if product.name:
                products.append(product)

        logger.info(f"Đã parse {len(products)} sản phẩm")
        return products

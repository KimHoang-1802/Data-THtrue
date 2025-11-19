# services/parser_service.py
# ==============================
# Service này chịu trách nhiệm phân tích HTML (BeautifulSoup)
# để lấy: tên sản phẩm, giá, đơn vị tính, ảnh.
# ==============================

# from bs4 import BeautifulSoup
# from models.product_model import Product
# import re

# class ParserService:
#     def __init__(self):
#         pass

#     def parse_products_from_html(self, html):
#         """
#         Nhận vào HTML (đã được Selenium lấy về)
#         Trả về danh sách Product
#         """
#         soup = BeautifulSoup(html, "html.parser")
#         products = []

#         # === TÌM CONTAINER CHỨA DANH SÁCH SẢN PHẨM ===
#         gallery_items = soup.select_one("div.gallery-module__items___YTUpR")

#         if not gallery_items:
#             gallery_items = soup.select_one("div[class*='gallery-module__items']")

#         if not gallery_items:
#             print("⚠ Không tìm thấy gallery container")
#             return products

#         # Mỗi item = 1 sản phẩm
#         items = gallery_items.select("div.item-module__root___hJBdd")

#         if not items:
#             items = gallery_items.select("div[class*='item-module__root']")

#         print(f"✓ Tìm thấy {len(items)} sản phẩm trong gallery")

#         # ==========================================================
#         #  DUYỆT QUA TỪNG SẢN PHẨM
#         # ==========================================================
#         for it in items:

#             # --------------------------------------
#             # 1. LẤY TÊN SẢN PHẨM
#             # --------------------------------------
#             name_elem = (
#                 it.select_one("span.item-module__name__IP_3e")
#                 or it.select_one("span[class*='item-module__name']")
#                 or it.select_one("a > span")
#                 or it.select_one("h3")
#             )

#             # --------------------------------------
#             # 2. LẤY GIÁ + ĐƠN VỊ TÍNH
#             # --------------------------------------
#             price_wrapper = (
#                 it.select_one("div.item-module__price__BV2pL")
#                 or it.select_one("div[class*='item-module__price']")
#             )

#             price_text = ""
#             unit_text = ""

#             if price_wrapper:
#                 # Lấy phần finalPrice (chỗ chứa giá cuối)
#                 final_price = (
#                     price_wrapper.select_one("div.item-module__finalPrice__zqAf5")
#                     or price_wrapper.select_one("div[class*='finalPrice']")
#                 )

#                 if final_price:
#                     full_text = final_price.get_text(separator="", strip=True)

#                     # ▶ Nếu dạng "34,500₫ / Hộp"
#                     if "/" in full_text:
#                         parts = full_text.split("/", 1)
#                         price_text = parts[0].strip()
#                         unit_text = parts[1].strip()
#                     else:
#                         # ▶ Nếu không có "/", tìm giá theo regex
#                         match = re.search(r'([\d,\.]+\s*₫)', full_text)
#                         if match:
#                             price_text = match.group(1).strip()
#                             remaining = full_text.replace(price_text, "").strip()
#                             if remaining:
#                                 unit_text = remaining
#                         else:
#                             price_text = full_text

#             # Backup nếu vẫn chưa lấy được giá
#             if not price_text:
#                 price_elem = it.select_one("div[class*='finalPrice']") or it.select_one(".price")
#                 if price_elem:
#                     price_text = price_elem.get_text(strip=True)

#             # --------------------------------------
#             # CLEAN GIÁ → bỏ ký tự ₫ và giữ lại số
#             # --------------------------------------
#             if price_text:
#                 # Ví dụ: "34,500₫" → "34,500"
#                 price_text = price_text.replace("₫", "").strip()

#                 # Loại bỏ mọi ký tự không phải số
#                 # "34,500" → "34500"
#                 clean_price_number = re.sub(r"[^\d]", "", price_text)

#                 # Chuyển về số (int)
#                 if clean_price_number.isdigit():
#                     price_text = int(clean_price_number)
#                 else:
#                     price_text = 0  # fallback

#             # --------------------------------------
#             # 3. TÌM ĐƠN VỊ NẾU CHƯA LẤY ĐƯỢC
#             # --------------------------------------
#             if not unit_text:
#                 unit_candidates = it.select("span")
#                 for sp in unit_candidates:
#                     txt = sp.get_text(strip=True)
#                     if txt and any(u in txt for u in ["Lốc", "Hộp", "kg", "Chai", "Viên", "g", "ml", "l", "Bịch", "Túi"]):
#                         unit_text = txt.replace("/", "").strip()
#                         break

#             # --------------------------------------
#             # 4. ẢNH SẢN PHẨM
#             # --------------------------------------
#             image_url = ""
#             img = (
#                 it.select_one("img.item-module__image___SWy-z")
#                 or it.select_one("img[class*='item-module__image']")
#                 or it.select_one("img")
#             )

#             if img:
#                 image_url = img.get("src", "") or img.get("data-src", "") or ""
#                 if not image_url or "placeholder" in image_url.lower():
#                     srcset = img.get("srcset", "")
#                     if srcset:
#                         first_url = srcset.split(",")[0].strip().split()[0]
#                         if first_url:
#                             image_url = first_url

#                 # Chuẩn hóa URL
#                 if image_url.startswith("//"):
#                     image_url = "https:" + image_url
#                 elif image_url.startswith("/"):
#                     image_url = "https://online.mmvietnam.com" + image_url
#                 elif not image_url.startswith("http"):
#                     image_url = "https://online.mmvietnam.com/" + image_url

#             # --------------------------------------
#             # 5. TẠO OBJECT PRODUCT
#             # --------------------------------------
#             product = Product(
#                 name=name_elem.get_text(strip=True) if name_elem else "",
#                 price=price_text,
#                 unit=unit_text,
#                 image=image_url
#             )

#             if product.name:
#                 products.append(product)

#         print(f"Đã parse được {len(products)} sản phẩm")
#         return products

# services/parser_services.py 
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

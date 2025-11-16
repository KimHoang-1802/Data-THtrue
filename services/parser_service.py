from bs4 import BeautifulSoup
from models.product_model import Product
import re

class ParserService:
    def __init__(self):
        pass

    def parse_products_from_html(self, html):
        """
        Trả về list[Product]
        """
        soup = BeautifulSoup(html, "html.parser")
        products = []

        # Tìm chính xác container chứa danh sách sản phẩm
        # Từ HTML: <section class="category-module__gallery___YJ2Ig">
        #   <div class="gallery-module__root___OtCA8">
        #     <div class="gallery-module__items___YTUpR">
        gallery_items = soup.select_one("div.gallery-module__items___YTUpR")
        
        if not gallery_items:
            # Fallback
            gallery_items = soup.select_one("div[class*='gallery-module__items']")
        
        if not gallery_items:
            print("⚠ Không tìm thấy gallery container")
            return products
        
        # Lấy tất cả item trong gallery
        items = gallery_items.select("div.item-module__root___hJBdd")
        
        if not items:
            items = gallery_items.select("div[class*='item-module__root']")
        
        print(f"✓ Tìm thấy {len(items)} sản phẩm trong gallery")

        for it in items:
            # 1. TÊN SẢN PHẨM
            name_elem = it.select_one("span.item-module__name__IP_3e") or \
                        it.select_one("span[class*='item-module__name']") or \
                        it.select_one("a > span") or \
                        it.select_one("h3")
            
            # 2. GIÁ - Quan trọng nhất!
            # Tìm container giá
            price_wrapper = it.select_one("div.item-module__price__BV2pL") or \
                           it.select_one("div[class*='item-module__price']")
            
            price_text = ""
            unit_text = ""
            
            if price_wrapper:
                # Tìm div chứa giá cuối cùng (finalPrice)
                final_price = price_wrapper.select_one("div.item-module__finalPrice__zqAf5") or \
                             price_wrapper.select_one("div[class*='finalPrice']")
                
                if final_price:
                    # Lấy toàn bộ text (bao gồm cả text ngoài span)
                    full_text = final_price.get_text(separator="", strip=True)
                    
                    # Tách giá và đơn vị theo dấu /
                    if "/" in full_text:
                        # Ví dụ: "34,500₫/ Hộp" hoặc "59,000₫ / Lốc"
                        parts = full_text.split("/", 1)
                        price_text = parts[0].strip()
                        unit_text = parts[1].strip()
                    else:
                        # Nếu không có /, lấy phần có chứa số và ₫
                        # Tách giá và text khác
                        match = re.search(r'([\d,\.]+\s*₫)', full_text)
                        if match:
                            price_text = match.group(1).strip()
                            # Phần còn lại là đơn vị
                            remaining = full_text.replace(price_text, "").strip()
                            if remaining:
                                unit_text = remaining
                        else:
                            price_text = full_text
            
            # Nếu vẫn chưa có giá, thử tìm trực tiếp
            if not price_text:
                price_elem = it.select_one("div[class*='finalPrice']") or \
                            it.select_one(".price")
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
            
            # 3. ĐƠN VỊ TÍNH - nếu chưa lấy được từ phần giá
            if not unit_text:
                # Thử tìm trong text của finalPrice (text ngoài span)
                if price_wrapper:
                    final_price = price_wrapper.select_one("div[class*='finalPrice']")
                    if final_price:
                        # Lấy text nodes (không phải từ span)
                        for content in final_price.contents:
                            if isinstance(content, str):
                                text = content.strip()
                                if text and text != "/" and text != " ":
                                    unit_text = text.replace("/", "").strip()
                                    break
                
                # Nếu vẫn chưa có, tìm trong các span
                if not unit_text:
                    unit_candidates = it.select("span")
                    for sp in unit_candidates:
                        txt = sp.get_text(strip=True)
                        if txt and any(keyword in txt for keyword in 
                                      ["Lốc", "Hộp", "Bộ", "kg", "Chai", "Vi", "Viên", "g", "ml", "l"]):
                            unit_text = txt.replace("/", "").strip()
                            break
            
            # 4. ẢNH SẢN PHẨM
            image_url = ""
            img = it.select_one("img.item-module__image___SWy-z") or \
                  it.select_one("img[class*='item-module__image']") or \
                  it.select_one("img")
            
            if img:
                # Ưu tiên src, nếu không có thì data-src (lazy loading)
                image_url = img.get("src", "") or img.get("data-src", "") or ""
                
                # Nếu image bị lazy load, có thể trong srcset
                if not image_url or "placeholder" in image_url.lower():
                    srcset = img.get("srcset", "")
                    if srcset:
                        # Lấy URL đầu tiên từ srcset
                        first_url = srcset.split(",")[0].strip().split()[0]
                        if first_url:
                            image_url = first_url
                
                # Xử lý URL
                if image_url:
                    if image_url.startswith("//"):
                        image_url = "https:" + image_url
                    elif image_url.startswith("/") and not image_url.startswith("//"):
                        image_url = "https://online.mmvietnam.com" + image_url
                    elif not image_url.startswith("http"):
                        image_url = "https://online.mmvietnam.com/" + image_url
            
            # Tạo Product object
            product = Product(
                name=name_elem.get_text(strip=True) if name_elem else "",
                price=price_text if price_text else "",
                unit=unit_text if unit_text else "",
                image=image_url
            )
            
            # Chỉ thêm nếu có tên sản phẩm
            if product.name:
                products.append(product)
            
        print(f"✓ Đã parse được {len(products)} sản phẩm")
        return products
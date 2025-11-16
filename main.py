# main.py
# Điểm chạy chính của chương trình.
# python3 main.py


from controllers.product_controller import ProductController
from export.excel_exporter import ExcelExporter

URL = "https://online.mmvietnam.com/category/bo-bo-thuc-vat.html"

def main():
    print("Bắt đầu crawl...")
    controller = ProductController(headless=True)  # headless=False để xem trình duyệt mở
    products = controller.crawl_category(URL)
    print(f"Đã thu thập được {len(products)} sản phẩm (sau dedup).")
    ExcelExporter.export(products)

if __name__ == "__main__":
    main()

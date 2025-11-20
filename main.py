
# main.py 
# Vai trò: File chính để chạy toàn bộ chương trình
from controllers.product_controller import ProductController
from export.excel_exporter import ExcelExporter
from utils.logger import get_logger

logger = get_logger("main")

URL = "https://online.mmvietnam.com/category/bo-bo-thuc-vat.html"

def main():
    logger.info("Bắt đầu chương trình")

    controller = ProductController(headless=True)
    products = controller.crawl_category(URL)

    ExcelExporter.export(products)

if __name__ == "__main__":
    main()
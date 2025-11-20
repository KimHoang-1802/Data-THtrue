
#Vai trò: Kết nối và lưu dữ liệu vào PostgreSQL
import psycopg2
from config import Config
from utils.logger import get_logger

logger = get_logger("database")

class DatabaseService:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                host=Config.POSTGRES_HOST,
                port=Config.POSTGRES_PORT,
                database=Config.POSTGRES_DB,
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD
            )
            self.cursor = self.conn.cursor()

            logger.info("Kết nối PostgreSQL thành công!")

            self.create_tables()

        except Exception as e:
            logger.error(f"Lỗi kết nối PostgreSQL: {e}")
            raise

    def create_tables(self):
        """Tạo bảng nếu chưa tồn tại"""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    price TEXT,
                    image TEXT,
                    crawl_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            self.conn.commit()
            logger.info("Bảng products đã sẵn sàng.")

        except Exception as e:
            logger.error(f"Lỗi tạo bảng: {e}")
            self.conn.rollback()

    def insert_product(self, p):
        """Chèn sản phẩm vào DB - không log chi tiết"""
        try:
            query = """
                INSERT INTO products (name, price, image, crawl_date)
                VALUES (%s, %s, %s, %s)
            """

            values = (
                getattr(p, "name", None),
                getattr(p, "price", None),
                getattr(p, "image", None),
                getattr(p, "date", None)  # Sử dụng date từ object Product
            )

            self.cursor.execute(query, values)
            self.conn.commit()

        except Exception as e:
            logger.error(f"Lỗi insert_product: {e}")
            self.conn.rollback()
            raise

    def insert_products_batch(self, products):
        """Chèn nhiều sản phẩm cùng lúc - tối ưu hơn"""
        if not products:
            return 0

        try:
            query = """
                INSERT INTO products (name, price, image, crawl_date)
                VALUES (%s, %s, %s, %s)
            """

            values_list = [
                (
                    getattr(p, "name", None),
                    getattr(p, "price", None),
                    getattr(p, "image", None),
                    getattr(p, "date", None)
                )
                for p in products
            ]

            self.cursor.executemany(query, values_list)
            self.conn.commit()

            inserted_count = len(values_list)
            logger.info(f"✓ Đã lưu {inserted_count} sản phẩm vào database")
            
            return inserted_count

        except Exception as e:
            logger.error(f"Lỗi insert_products_batch: {e}")
            self.conn.rollback()
            raise

    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            logger.info("Đã đóng kết nối Database.")
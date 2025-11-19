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
        """Chèn sản phẩm vào DB"""
        try:
            query = """
                INSERT INTO products (name, price, image, crawl_date)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            """

            values = (
                getattr(p, "name", None),
                getattr(p, "price", None),
                getattr(p, "image", None),
            )

            self.cursor.execute(query, values)
            self.conn.commit()

            logger.info(f"Đã lưu sản phẩm: {p.name}")

        except Exception as e:
            logger.error(f"Lỗi insert_product: {e}")
            self.conn.rollback()

    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            logger.info("Đã đóng kết nối Database.")

# models/product_model.py

# Class Product đại diện cho 1 sản phẩm
from datetime import datetime

class Product:
    def __init__(self, name="", price=0, unit="", image="", date=None):
        self.name = name
        self.price = price
        self.unit = unit
        self.image = image
        self.date = date or datetime.now()

    def to_dict(self):
        return {
            "Tên sản phẩm": self.name,
            "Giá (VND)": self.price,
            "Đơn vị tính": self.unit,
            "Ảnh": self.image,
            "Ngày crawl": self.date.strftime("%Y-%m-%d %H:%M:%S")
        }
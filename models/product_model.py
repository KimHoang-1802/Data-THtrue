# models/product_model.py

# Class Product đại diện cho 1 sản phẩm
class Product:
    def __init__(self, name="", price="", unit="", image=""):
        self.name = name
        self.price = price
        self.unit = unit
        self.image = image

    def to_dict(self):
        return {
            "Tên sản phẩm": self.name,
            "Giá": self.price,
            "Đơn vị tính": self.unit,
            "Ảnh": self.image
        }
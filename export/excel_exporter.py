# export/excel_exporter.py

# import pandas as pd
# import os

# class ExcelExporter:
#     @staticmethod
#     def export(products, file_path="data/products.xlsx"):
#         os.makedirs(os.path.dirname(file_path), exist_ok=True)
#         rows = [p.to_dict() for p in products]
#         df = pd.DataFrame(rows)
#         df.to_excel(file_path, index=False)
#         print(f"Đã xuất Excel: {file_path}")


# excel_export.py
import logging
import pandas as pd
import os

logger = logging.getLogger(__name__)

class ExcelExporter:
    @staticmethod
    def export(products, file_path="data/products.xlsx"):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df = pd.DataFrame([p.to_dict() for p in products])
        df.to_excel(file_path, index=False)
        logger.info(f"Đã xuất Excel: {file_path}")

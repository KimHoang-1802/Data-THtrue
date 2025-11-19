#logger.py

import logging
import os

def get_logger(name="crawler"):
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # tránh double logging
    if not logger.handlers:
        file_handler = logging.FileHandler("logs/crawler.log", encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

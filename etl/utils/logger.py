import logging
import sys


def get_logger(name: str = "etl"):
    """
    Logger dùng CHUNG cho toàn bộ ETL:
    - crawler
    - normalize
    - importer
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    level = logging.INFO
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "[%(levelname)s] %(asctime)s - %(message)s",
        datefmt="%H:%M:%S"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

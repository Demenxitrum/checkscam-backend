# etl/crawler_all.py
from utils.logger import get_logger

from sources import (
    crawl_facebook,
    crawl_tiktok,
    crawl_news,
    crawl_ncsc_news,
    crawl_police,
    crawl_phishtank,
)

logger = get_logger("crawler_all")

CRAWLERS = [
    ("Facebook", crawl_facebook),
    ("TikTok", crawl_tiktok),
    ("News", crawl_news),
    ("NCSC", crawl_ncsc_news),
    ("Police", crawl_police),
    ("PhishTank", crawl_phishtank),
]


def main():
    for name, module in CRAWLERS:
        try:
            logger.info(f"🚀 Start {name} crawler")
            module.run()
            logger.info(f"✅ Done {name}")
        except Exception as e:
            logger.error(f"❌ {name} failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()

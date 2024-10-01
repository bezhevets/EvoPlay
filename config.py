import logging
import sys


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s]: %(message)s",
        handlers=[logging.FileHandler("log.log"), logging.StreamHandler(sys.stdout)],
    )

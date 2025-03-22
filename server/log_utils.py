import logging

from config import LOG_LEVEL, LOGGING_HANDLERS


def init_logger() -> None:
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=LOGGING_HANDLERS,
    )

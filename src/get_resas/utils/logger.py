from logging import INFO, Formatter, StreamHandler, getLogger


def get_my_logger(name: str) -> getLogger:
    logger = getLogger(name)
    if not logger.hasHandlers():
        handler = StreamHandler()
        handler.setFormatter(
            Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
    logger.setLevel(INFO)
    return logger

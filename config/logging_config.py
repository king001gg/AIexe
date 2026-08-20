import logging
import logging.handlers
import os

from config.settings import AppSettings


def setup_logging(level: str = None) -> logging.Logger:
    """配置并返回全局 logger（控制台 + 滚动文件）。

    幂等：多次调用不会重复添加 handler。
    """
    level = (level or AppSettings.LOG_LEVEL).upper()
    AppSettings.ensure_dirs()

    logger = logging.getLogger("aura")
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level, logging.INFO))
    logger.propagate = False

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)

    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(AppSettings.LOGS_DIR, "app.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger

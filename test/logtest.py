import logging
import colorlog


def init_logger(logfile, loglevel):
    """初始化日志记录器

    Args:
        logfile: 日志文件名，不写入日志文件则传入None
        loglevel: 日志级别，可选值为debug、info、warning、error、critical

    Returns:
        logger: 返回初始化后的logger对象
    """
    # 创建logger对象
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # 创建控制台输出handler
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s[%(asctime)s %(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )
    logger.addHandler(console_handler)

    if logfile:
        # 创建文件输出handler
        file_handler = logging.FileHandler(logfile, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        logger.addHandler(file_handler)

    # 设置日志级别
    if loglevel == "debug":
        logger.setLevel(logging.DEBUG)
    elif loglevel == "info":
        logger.setLevel(logging.INFO)
    elif loglevel == "warning":
        logger.setLevel(logging.WARNING)
    elif loglevel == "error":
        logger.setLevel(logging.ERROR)
    elif loglevel == "critical":
        logger.setLevel(logging.CRITICAL)

    return logger


if __name__ == "__main__":
    # 初始化日志记录器，不写文件
    logger = init_logger(None, "debug")
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")

    # 初始化日志记录器，写文件
    logger = init_logger("test.log", "info")
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")

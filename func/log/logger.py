import logging
import colorlog


def getLogger(fileName, logName):
    # 日志工具
    logger = logging.getLogger(logName)
    logger.setLevel(logging.DEBUG)

    # 创建控制台处理程序并设置颜色
    console = colorlog.StreamHandler()
    color_format = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",  # 将INFO的颜色设置为白色
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
    console.setFormatter(color_format)
    logger.addHandler(console)

    # 文件日志
    handler = logging.FileHandler(fileName, encoding="utf-8", mode="a+")
    format_str = logging.Formatter(
        "%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s"
    )
    handler.setFormatter(format_str)
    logger.addHandler(handler)

    return logger


if __name__ == "__main__":
    log = getLogger(f"./logs/log_11.txt", "bilibili-live")
    log.error("测试")

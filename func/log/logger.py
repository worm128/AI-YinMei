import logging
import colorlog
import datetime

class Logger:

    def __init__(self, fileName, encoding, logName):
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
        handler = logging.FileHandler(fileName, encoding=encoding, mode="a+")
        format_str = logging.Formatter("%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        handler.setFormatter(format_str)
        logger.addHandler(handler)

        self.logger=logger

    def getLogger(self):
        return self.logger


if __name__ == "__main__":
    log = Logger(f"log_11.txt","utf-8", "bilibili-live1").getLogger()
    log.error("测试")
    log = Logger(f"log_22.txt","utf-8", "bilibili-live2").getLogger()
    log.error("测试2")

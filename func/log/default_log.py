import datetime
from func.log.logger_base import LoggerBase

def singleton(cls):
    instances = {}
    def getInstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getInstance

@singleton
class DefaultLog:
      def __init__(self):
          # 设置控制台日志
          today = datetime.date.today().strftime("%Y-%m-%d")
          self.logger = LoggerBase(f"./logs/log_{today}.txt","utf-8", "defaultLog").getLogger()

      def getLogger(self):
          return self.logger
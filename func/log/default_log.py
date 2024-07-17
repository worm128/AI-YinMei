import datetime
from func.log.logger_base import LoggerBase
from func.tools.singleton_mode import singleton
import logging

@singleton
class DefaultLog:
      def __init__(self):
          # 设置控制台日志
          today = datetime.date.today().strftime("%Y-%m-%d")
          self.logger = LoggerBase(f"./logs/log_{today}.txt","utf-8", "defaultLog").getLogger()

          # 定时器只输出error
          logging.getLogger("apscheduler.executors.default").setLevel("ERROR")
          # 关闭页面访问日志
          logging.getLogger("werkzeug").setLevel("ERROR")
          # 设置asyncio日志级别
          logging.getLogger('asyncio').setLevel("ERROR")

      def getLogger(self):
          return self.logger
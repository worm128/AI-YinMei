import logging
import os
import time
class LogsBase():

    def __init__(self,name):
        # 日志配置
        root_dir=os.path.dirname(os.path.abspath(__file__))
        log_dir=os.path.join(root_dir,"logs")
        if not os.path.exists(log_dir):
           os.mkdir(log_dir)
        
        #指定输出的格式
        formatStr='%(asctime)s %(levelname)s %(name)s %(message)s'
        formatter = logging.Formatter(formatStr)

        # 控制台日志
        logging.basicConfig(level=logging.INFO, format=formatStr)
        self.my_logging = logging.getLogger(name)#创建日志收集器

        # 控制台
        ch = logging.StreamHandler()#输出到控制台
        ch.setLevel('INFO')#设置日志输出级别
        ch.setFormatter(formatter)
        self.my_logging.addHandler(ch)#对接，添加渠道

        #创建文件处理器fh，log_file为日志存放的文件夹
        log_file=os.path.join(log_dir,"{}_log.txt".format(time.strftime("%Y-%m-%d",time.localtime())))
        fh = logging.FileHandler(log_file,encoding="UTF-8")
        fh.setLevel('INFO')#设置日志输出级别
        fh.setFormatter(formatter)
        self.my_logging.addHandler(fh)#对接，添加渠道

    def debug(self, message):
        self.my_logging.debug(message)
    
    def info(self, message):
        self.my_logging.info(message)
    
    def warning(self, message):
        self.my_logging.warning(message)
    
    def error(self, message):
        self.my_logging.error(message)
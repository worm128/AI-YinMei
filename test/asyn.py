# 异步线程测试
import asyncio
import time
from threading import Thread


import threading


def draw(a, b, c):
    print(f"1{a}{c}.另外开始一个子线程做任务啦\n")
    time.sleep(10)  # 用time.sleep模拟任务耗时
    print(f"1{b}.子线程任务结束啦\n")


def my_thread_func(arg1, arg2):
    print(f"Thread function with arguments:{arg1},{arg2}\n")


# 创建线程，并传递参数
t = threading.Thread(target=my_thread_func, args=("Hello", "World"))

# 启动线程
t.start()

t2 = threading.Thread(target=draw, args=("Hello1", "Hello2", "Hello3"))

# 启动线程
t2.start()

print("test end")

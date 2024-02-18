# 键盘控制vtuber表情测试
from pynput.keyboard import Key, Controller
import time


def is_array_contain_string(string_array, target_string):
    i = 0
    num = 0
    arr = list()
    for s in string_array:
        i = i + 1
        if s in target_string:
            arr.append(i)
            num = num + 1
    return arr


def emote_do(text, response, keyboard, startTime, key):
    nums = is_array_contain_string(text, response)
    length = len(nums)
    if length > 0:
        for num in range(length):
            start = num * startTime
            time.sleep(start)
            keyboard.press(key)
            time.sleep(1)
            keyboard.release(key)


if __name__ == "__main__":
    text = ["认同", "点头", "啊", "嗯", "哦", "女仆"]
    keyboard = Controller()
    target = emote_do(text, "我是你的专属女仆小美啊，你忘记了吗?", keyboard, 0.2, Key.f5)

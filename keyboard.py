# 键盘测试
import time
from pynput.keyboard import Key, Controller
from pykeyboard import PyKeyboard  # 模拟键盘

if __name__ == "__main__":
    # keyboard = PyKeyboard()
    # keyboard.press_key('1')
    # time.sleep(5)
    # keyboard.release_key('1')
    keyboard = Controller()
    keyboard.press(Key.f2)
    time.sleep(15)
    keyboard.release(Key.f2)

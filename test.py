import glob
import os
import re
import chardet
import random
import queue
from urllib import parse

# song_name="Kiss Me Goodbye [Originally Performed by Angela Aki]"
# my_dir_=""
# for c in song_name:
#     if c == '[':
#         c = '[[]'
#     elif c == ']':
#         c = '[]]'
#     else:
#         c = c
#     my_dir_ = my_dir_ + c
# search_pattern = os.path.join(f"output\\{my_dir_}\\" + my_dir_ + '*.wav')
# list = glob.glob(search_pattern)
# print(list)
# name = re.sub(r'[\[\]<>:"/\\|?*]', '', "[孤高の浮き雲]..../雲[雀恭]弥 (BGM Ver.)....").rstrip('. ')
# print(name)

# def check_encoding(text):
#     result = chardet.detect(text)
#     encoding = result['encoding']
    
#     if encoding is None or 'ascii' in encoding.lower():
#         print("该文本没有明显的非ASCII字符")
#     else:
#         print("该文本的编码为:", encoding)

# check_encoding('å\x8f\x88æ\x98¯æ¸\x85æ\x98\x8eé\x9b¨ä¸\x8a æ\x8a\x98è\x8f\x8aå¯\x84å\x88°ä½\xa0èº«æ\x97\x81')

# 判断字符位置（不含搜索字符）- 如，搜索“画画女孩”，则输出“女孩”位置
def is_index_contain_string(string_array, target_string):
    i = 0
    for s in string_array:
        i = i + 1
        if s in target_string:
            num = target_string.find(s)
            return num + len(s)
    return 0

# text = ["唱一下", "唱一首", "唱歌", "唱"]
# num = is_index_contain_string(text, "又是这个高端歌，吟美唱死")
# print(num)
# text=parse.quote("你好")
# print(text)

# random_number = random.randrange(0, 2)
# print(random_number)

# jsonstr =[]
# SongQueueList = queue.Queue()
# SongQueueList.put("ab")
# SongQueueList.put("b")
# SongQueueList.put("x")
# SongQueueList.put("d")

# for i in range(SongQueueList.qsize()):
#     print(SongQueueList.queue[i])
#     jsonstr.append({"songname":SongQueueList.queue[i]})
# print(jsonstr)
# print(SongQueueList.queue)

user_name="test"
wenhou=[f"{user_name}，恭喜发财，龙年大吉"]
wenhou_num = random.randrange(0, len(wenhou))
print(wenhou[wenhou_num])

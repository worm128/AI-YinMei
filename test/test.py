import glob
import os
import re
import time
# import chardet
# import random
# import queue
from urllib import parse
now = time.strftime("%Y%m%d", time.localtime())
print(f"今天是{now}年月日")
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
import yaml
f = open('config-prod.yml','r',encoding='utf-8')
cont = f.read()
config = yaml.load(cont,Loader=yaml.FullLoader)
welcome_not_allow = config["welcome"]["welcome_not_allow"]
if all([333472479!=not_allow_userid for not_allow_userid in welcome_not_allow]):
       # 加入欢迎列表
       print("fff")

# 判断字符位置（不含搜索字符）- 如，搜索“画画女孩”，则输出“女孩”位置
def is_index_contain_string(string_array, target_string):
    i = 0
    for s in string_array:
        i = i + 1
        if s in target_string:
            num = target_string.find(s)
            return num + len(s)
    return 0

# 判断字符位置（不含搜索字符）- 如，搜索“画画女孩”，则输出“女孩”位置
def rfind_index_contain_string(string_array, target_string):
    i = 0
    for s in string_array:
        i = i + 1
        num = target_string.rfind(s)
        if num>0:
           return num + len(s)
    return 0

def has_string_reg(regx,s):
    return re.search(regx, s)

pattern = r'\[.*?\]|<.*?>|\(.*?\)|\n'
ss=re.sub(pattern, '', "dsf(三国演义)123")
print(ss)

pattern="(三国演义\d+|粤剧|京剧|易经)"
ss=re.search(pattern,  "dsf三国演义123")
if ss:
    print("xxx")


str=",\"winlone\",说渣渣美"
split_flag=",|，|。|!|！|?|？|\n"
text = split_flag.split("|")
num = rfind_index_contain_string(text, str)
print(num)
split_content = str[0 : num]
print(split_content)
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

# user_name="test"
# wenhou=[f"{user_name}，恭喜发财，龙年大吉"]
# wenhou_num = random.randrange(0, len(wenhou))
# print(wenhou[wenhou_num])
# content= "有一只,超爱干净的猫咪"
# num = is_index_contain_string(",", content)
# temp = content[num : len(content)]
# content = content[0 : num]
# print(temp)
# print(content)

import uuid

for i in range(100):
    uuid_value = uuid.uuid4()
    timestamp = time.time()
    print(uuid_value)

str = "Hello, World!"
char = "o"
split_flag=",|，|。|!|！|?|？|\n"
text = split_flag.split("|")

last_index = str.rfind(text)
print(f"The last occurrence of '{char}' is at index {last_index}.")

if re.search("[,|，|。|!|！|。|?|？]", "\""):
   print("match")

# 过滤html标签
def filter_html_tags(text):
    pattern = r'\[.*?\]|<.*?>|\(.*?\)'  # 匹配尖括号内的所有内容(.*?)
    return re.sub(pattern, '', text)


str="你[啊哈大]啊(搞笑)，你丫的兔崽子<死人呢>搞大幅度"
end=filter_html_tags(str)
print(end)
# 正则判断[集合判断]
def has_string_reg_list(regxlist,s):
    regx = regxlist.replace("[","(").replace("]",")").replace(",","|").replace("'","").replace(" ","")
    return re.search(regx, s)

# text = ["跳舞", "跳一下", "舞蹈"]
# print(text)
# ok = has_string_reg_list(f"^{text}","舞蹈ddfg 嘻嘻嘻")
# print(ok.regs[0](1))
# jsonstr=[]
# press_arry = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
# userlist = str(press_arry).replace("['","").replace("']","")
# # press = random.randrange(0, len(press_arry))
# # jsonstr.append({"content":"happy","key":press_arry[press],"num":1})
# print(jsonstr)
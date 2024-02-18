from flask import Flask, jsonify, request, render_template
import queue
import json

app = Flask(__name__)

content=1
# 聊天回复弹框处理
@app.route("/chatreply", methods=["GET"])
def chatreply():
    global content
    CallBackForTest=request.args.get('CallBack')
    print(CallBackForTest)
    content=content+1
    temp = "({\"status\": \"成功\",\"content\": \""+str(content)+"画画鬼灭之刃的美女似懂非懂是否第三方的身份画画鬼灭之刃的美女似懂非懂是否第三方的身份画画鬼灭之刃的美女似懂非懂是否第三方的身份画画鬼灭之刃的美女似懂非懂是否第三方的身份画画鬼灭之刃的美女似懂非懂是否第三方的身份画画鬼灭之刃的美女似懂非懂是否第三方的身份画画鬼灭之刃的美女似懂非懂是否第三方的身份画画鬼灭之刃的美女似懂非懂是否第三方的身份\"})"
    if CallBackForTest is not None:
       temp=CallBackForTest+temp
    return temp

SongQueueList = queue.Queue()
SongQueueList.put("测试喜欢你")
SongQueueList.put("十分的舒服的事")
SongQueueList.put("广泛的过分低估")
SongQueueList.put("二十五分第三方的身份")
SongQueueList.put("二十五分第三方的身份")
SongQueueList.put("二十五分第三方的身份")
SongQueueList.put("二十五分第三方的身份")
SongQueueList.put("二十五分第三方的身份")
SongQueueList.put("二十五分第三方的身份")
SongQueueList.put("二十五分第三方的身份")
# 点播歌曲列表
@app.route("/songlist", methods=["GET"])
def songlist():
    jsonstr =[]
    CallBackForTest=request.args.get('CallBack')
    print(CallBackForTest)
    for i in range(SongQueueList.qsize()):
        jsonstr.append({"songname":SongQueueList.queue[i]})
    temp = jsonstr
    if CallBackForTest is not None:
       temp = CallBackForTest+"({\"status\": \"成功\",\"content\": "+json.dumps(jsonstr)+"})"
    return temp

if __name__ == "__main__":
    # 开启web
    app.run(host="0.0.0.0", port=1800)
import sys
import os
import time
from obswebsocket import obsws, events, requests


def get_child_file_paths(directory):
    child_file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            child_file_paths.append(os.path.join(root, file))
    return child_file_paths

# 连接到OBS
host = '192.168.2.198'  # OBS服务器地址
port = 4455         # obs-websocket插件设置的端口
password = '123456'  # obs-websocket插件设置的密码
 
ws = obsws(host, port, password)
ws.connect()

#ws.call(requests.SetTextAsync(source_name="ttt",text="你好啊", duration=5000))
#ws.call(requests.SetTextGDIPlusProperties(source_name="text",text="text"))

# 使用例子
directory = 'J:\\ai\\跳舞视频'
child_files = get_child_file_paths(directory)
for file in child_files:
    print(file)

print(child_files[0])
#影片输出
ws.call(requests.SetInputSettings(
    inputName="video",
    inputSettings={
        "local_file": child_files[0],
    }
))
ws.call(requests.TriggerMediaInputAction(inputName="video",mediaAction="OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART"))
status = ws.call(requests.GetMediaInputStatus(inputName="video"))
print(status)
#ws.call(requests.SetMediaInputCursor(inputName="video",mediaCursor=50000))
# ws.call(requests.SetInputSettings(
#     inputName="video",
#     inputSettings={
#         "mediaAction": "OBS_MEDIA_STATE_STOPPED",
#     }
# )) 
ws.call(requests.TriggerMediaInputAction(inputName="video",mediaAction="OBS_WEBSOCKET_MEDIA_INPUT_ACTION_STOP"))

#图片输出
# ws.call(requests.SetInputSettings(
#     inputName="image",
#     inputSettings={
#         "file": "J:\\ai\\ai-yinmei\\images\\黄图.jpg",
#     }
# ))
#文字输出
# ws.call(requests.SetInputSettings(inputName="ttt",inputSettings={
#         "text": "你好啊",
#     }))

#场景切换
#ws.call(requests.SetCurrentProgramScene(sceneName="本地电脑"))

#obs版本打印
# ver = ws.call(requests.GetVersion()).getObsVersion()
# print(ver)

# 场景切换
# try:
#     scenes = ws.call(requests.GetSceneList())
#     for s in scenes.getScenes():
#         name = s['sceneName']
#         print("Switching to {}".format(name))
#         ws.call(requests.SetCurrentProgramScene(sceneName=name))
#         time.sleep(2)
#     print("End of list")
# except KeyboardInterrupt:
#     pass

ws.disconnect()


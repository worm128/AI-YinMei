import websocket
import json

# OBS服务器连接信息
host = '127.0.0.1'  # OBS服务器主机名或IP地址
port = 4455  # OBS WebSocket API默认端口号为4444
password = ''  # OBS密码（如果有设置）

def send_danmaku(message):
    # 建立WebSocket连接
    ws = websocket.create_connection('ws://{}:{}'.format(host, port))
    
    # 发送弹幕消息
    danmaku_message = {
        "source": "Vtuber",
        "type": "text",
        "text": message,
        "position": {
            "x": 0,
            "y": 0,
            "z": 0
        },
        "size": 28,
        "color": {
            "r": 255,
            "g": 255,
            "b": 255,
            "a": 255
        },
        "duration": 5000,  # 持续时间（单位：毫秒）
        "sourceName": "Python弹幕",  # 源名称（可自定义）
        "alignment": 3  # 对齐方式（1：左对齐；2：右对齐；3：居中对齐）
    }
    danmaku_json = json.dumps(danmaku_message)
    ws.send('{"jsonrpc":"2.0","method":"SendCaption","params":{"caption": "' + message + '"},"id":1}')
    
    # 关闭WebSocket连接
    ws.close()

if __name__ == "__main__":
    send_danmaku("你哈啊的范德萨范德萨水电费")
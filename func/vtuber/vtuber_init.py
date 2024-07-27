import json
import websocket
from threading import Thread
from func.log.default_log import DefaultLog
from func.tools.singleton_mode import singleton
from func.gobal.data import VtuberData

@singleton
class VtuberInit:
    # 设置控制台日志
    log = DefaultLog().getLogger()

    vtuberData = VtuberData()  # vtuber数据

    def __init__(self):
        if self.vtuberData.switch == True:
            self.ws = websocket.WebSocketApp(f"ws://{self.vtuberData.vtuber_websocket}", on_open=self.on_open)
            # ws表情服务心跳包
            run_forever_thread = Thread(target=self.run_forever)
            run_forever_thread.start()
            self.log.info(f"VtuberStudio皮肤链接成功")
        else:
            self.log.warning(f"VtuberStudio皮肤开关已关闭")

    def get_ws(self):
        return self.ws

    def stop(self):
        return self.ws.close()

    # ============= Vtuber表情 =====================
    def run_forever(self):
        self.ws.run_forever(ping_timeout=1)

    # 注意：on_open是websocket服务的重载函数，必须有ws链接对象传入参数
    def on_open(self,ws):
        self.auth()

    # 授权Vtuber服务
    def auth(self):
        # 授权码
        authstr = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeID",
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": self.vtuberData.vtuber_pluginName,
                "pluginDeveloper": self.vtuberData.vtuber_pluginDeveloper,
                "authenticationToken": self.vtuberData.vtuber_authenticationToken,
            },
        }
        data = json.dumps(authstr)
        self.ws.send(data)
    # ============================================
from obswebsocket import obsws, events, requests
from enum import Enum

class VideoControl(Enum):
    RESTART = "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART"
    STOP = "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_STOP"
    PAUSE = "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PAUSE"
    PLAY = "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PLAY"
    NEXT = "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_NEXT"
    PREVIOUS = "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PREVIOUS"

class VideoStatus(Enum):
    STOP = "OBS_MEDIA_STATE_STOPPED"
    PAUSE = "OBS_MEDIA_STATE_PAUSED"
    PLAY = "OBS_MEDIA_STATE_PLAYING"
    END = "OBS_MEDIA_STATE_ENDED"

class ObsWebSocket:
      
      def __init__(self,host,port,password):
          self.host = host
          self.port = port
          self.password = password
          self.ws = obsws(self.host, self.port, self.password)
          print(self.ws)
      
      def connect(self):
          self.ws.connect()
      
      def disconnect(self):
          self.ws.disconnect()
    
      #影片输出
      def play_video(self,inputName,file_path):
          return self.ws.call(requests.SetInputSettings(
                    inputName=inputName,
                    inputSettings={
                        "local_file": file_path,
                    },
                ))
      
      #影片控制
      def control_video(self,inputName,videoStatus):
          return self.ws.call(requests.TriggerMediaInputAction(inputName=inputName,mediaAction=videoStatus))

      #获取影片播放状态
      def get_video_status(self,inputName):
          data = self.ws.call(requests.GetMediaInputStatus(inputName=inputName))
          return data.datain["mediaState"]

      #场景切换
      def change_scene(self,sceneName):
          return self.ws.call(requests.SetCurrentProgramScene(sceneName=sceneName))
      
      #图片输出
      def show_image(self,inputName,file_path):
          return self.ws.call(requests.SetInputSettings(
                    inputName=inputName,
                    inputSettings={
                        "file": file_path,
                    }
                 ))
      
      #文字输出
      def show_text(self,inputName,text):
          return self.ws.call(requests.SetInputSettings(inputName=inputName,inputSettings={
                      "text": text,
                 }))
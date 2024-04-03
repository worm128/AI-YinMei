import time
from func.obs.obs_websocket import ObsWebSocket,VideoStatus,VideoControl

if __name__ == "__main__":
    obs = ObsWebSocket(host="192.168.2.198",port=4455,password="123456")
    obs.connect()
    now_time = time.strftime("%H:%M:%S", time.localtime())
    print(now_time) 
    if "18:00:00" < now_time <= "24:00:00" or "00:00:00" < now_time < "06:00:00":
        print("现在是晚上") 
        obs.show_image("海岸花坊","J:\\ai\\vup背景\\海岸花坊\\夜晚.jpg")
        obs.play_video("神社背景","J:\\ai\\vup背景\\神社夜晚\\夜动态.mp4")


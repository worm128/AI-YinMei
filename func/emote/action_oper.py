import threading
from threading import Thread
import datetime
import logging
from func.log import logger

class ActionOper:
    # 设置控制台日志
    today = datetime.date.today().strftime("%Y-%m-%d")
    log = logger.getLogger(f"./logs/log_{today}.txt", "ttsCore")

    # 摇摆
    swing_motion = 2  # 1.摇摆中 2.停止摇摆
    auto_swing_lock = threading.Lock()

    def __init__(self):
        pass

    def auto_swing(self):
        self.auto_swing_lock.acquire()
        global swing_motion
        # 触发器-设置开始摇摆: 停止摇摆+（唱歌中 或者 聊天中）= 可以设置摇摆动作
        if swing_motion == 2 and (is_singing == 1 or is_tts_ready == False):
            self.log.info(f"进入摇摆状态:{swing_motion},{is_singing},{is_tts_ready}")
            swing_motion = 1
        else:
            self.auto_swing_lock.release()
            return
        # 监听停止摇摆线程
        stop_emote_thread = Thread(target=stop_motion)
        stop_emote_thread.start()
        self.auto_swing_lock.release()

        # 执行器-循环摇摆：唱歌中 或者 说话中 都会摇摆
        while swing_motion == 1 and (is_singing == 1 or is_tts_ready == False):
            jsonstr = []
            jsonstr.append({"content": "happy", "key": "摇摆1", "num": 1, "timesleep": 0, "donum": 0, "endwait": 24})
            jsonstr.append({"content": "happy", "key": "摇摆2", "num": 1, "timesleep": 0, "donum": 0, "endwait": 21})
            jsonstr.append({"content": "happy", "key": "摇摆3", "num": 1, "timesleep": 0, "donum": 0, "endwait": 30})
            jsonstr.append({"content": "happy", "key": "摇摆4", "num": 1, "timesleep": 0, "donum": 0, "endwait": 19})
            jsonstr.append({"content": "happy", "key": "摇摆5", "num": 1, "timesleep": 0, "donum": 0, "endwait": 30})
            jsonstr.append({"content": "happy", "key": "摇摆6", "num": 1, "timesleep": 0, "donum": 0, "endwait": 30})
            # 随机一个【摇摆动作】
            num = random.randrange(0, len(jsonstr))
            emote_show_json = []
            emote_show_json.append(jsonstr[num])
            # 执行【摇摆动作】
            self.log.info(f"执行摇摆：{emote_show_json}")
            emote_show_thread = Thread(target=emote_show, args=(emote_show_json,))
            emote_show_thread.start()
            # 当前【摇摆动作】等待结束时间
            endwait = emote_show_json[0]["endwait"]
            while endwait > 0:
                time.sleep(1)
                endwait = endwait - 1
                # 唱歌完毕并且聊天完毕：停止摇摆动作
                if is_singing == 2 and is_tts_ready == True:
                    swing_motion = 2
                    self.log.info(f"强制停止摇摆：{swing_motion}")
                    break
        swing_motion = 2
        self.log.info(f"结束摇摆：{emote_show_json}")

    # 停止动作
    def stop_motion():
        while swing_motion == 1:
            time.sleep(1)
        self.log.info(f"静止：{swing_motion}")
        emote_ws(1, 0, "静止")
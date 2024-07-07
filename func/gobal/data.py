from func.config.default_config import defaultConfig
import queue
import threading
from func.tools.singleton_mode import singleton

# 加载配置
config = defaultConfig().get_config()

@singleton
class LLmData:
    Ai_Name: str = config["AiName"]  # Ai名称

    # ============= LLM参数 =====================
    QuestionList = queue.Queue()  # LLM回复问题
    QuestionName = queue.Queue()
    AnswerList = queue.Queue()  # Ai回复队列
    history = []
    is_ai_ready = True  # 定义ai回复是否转换完成标志
    is_stream_out = False  # 标识LLM流式处理是同一段回复，True：正在同一段回复中 False：结束同一段流式回复
    split_flag = config["llm"]["split_flag"]
    split_str = split_flag.split("|")
    split_limit = config["llm"]["split_limit"]  # 分割的最小字符数量
    # ============================================

    # ============= 本地模型加载 =====================
    # 模型加载方式
    local_llm_type: str = config["llm"]["local_llm_type"]
    public_sentiment_key: str = config["llm"]["public_sentiment_key"]
    # ============================================

@singleton
class TTsData:
    SayCount = 0
    say_lock = threading.Lock()
    ReplyTextList = queue.Queue()  # Ai回复框文本队列
    is_tts_ready = True  # 定义语音是否生成完成标志
    # 选择语音
    select_vists = config["speech"]["select"]

@singleton
class VtuberData:
    # ============= vtuber studio连接参数 =====================
    vtuber_websocket = config["emote"]["vtuber_websocket"]
    vtuber_pluginName = config["emote"]["vtuber_pluginName"]
    vtuber_pluginDeveloper = config["emote"]["vtuber_pluginDeveloper"]
    vtuber_authenticationToken = config["emote"]["vtuber_authenticationToken"]
    # ========================================

    # ============= 场景 =====================
    song_background = config["obs"]["song_background"]
    # ========================================

    # ============= 摇摆 =====================
    swing_motion = 2  # 1.摇摆中 2.停止摇摆
    auto_swing_lock = threading.Lock()
    # ========================================

    mood_num = 0  # 感情值

@singleton
class SingData:
    # ============= 唱歌参数 =====================
    singUrl = config["sing"]["singUrl"]
    SongQueueList = queue.Queue()  # 唱歌队列
    SongMenuList = queue.Queue()  # 唱歌显示
    SongNowName = {}  # 当前歌曲
    is_singing = 2  # 1.唱歌中 2.唱歌完成
    is_creating_song = 2  # 1.生成中 2.生成完毕
    sing_play_flag = 0  # 1.正在播放唱歌 0.未播放唱歌 【用于监听歌曲播放器是否停止】
    song_not_convert = config["sing"]["song_not_convert"]  # 不需要学习的歌曲【支持正则】
    create_song_timout = config["sing"]["create_song_timout"]  # 超时生成歌曲
    # ============================================
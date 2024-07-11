from func.config.default_config import defaultConfig
import queue
import threading
from func.tools.singleton_mode import singleton
from func.tools.file_util import FileUtil

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

    # ============= 欢迎列表 =====================
    WelcomeList = []  # welcome欢迎列表
    # ========================================

    # ============= 进入房间的欢迎语 =====================
    is_llm_welcome = config["welcome"]["is_llm_welcome"]
    welcome_not_allow = config["welcome"]["welcome_not_allow"]
    # ============================================

@singleton
class TTsData:
    SayCount = 0
    say_lock = threading.Lock()
    ReplyTextList = queue.Queue()  # Ai回复框文本队列
    is_tts_ready = True  # 定义语音是否生成完成标志
    # 选择语音
    select_vists = config["speech"]["select"]
    # 语音合成线程池
    speech_max_threads = config["speech"]["speech_max_threads"]

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
    now_clothes = "便衣"
    # ========================================

    # ============= 摇摆 =====================
    swing_motion = 2  # 1.摇摆中 2.停止摇摆
    auto_swing_lock = threading.Lock()
    # ========================================

    mood_num = 0  # 感情值

@singleton
class SingData:
    create_song_lock = threading.Lock()
    play_song_lock = threading.Lock()

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

@singleton
class DrawData:
    # ============= 绘画参数 =====================
    drawUrl = config["draw"]["drawUrl"]
    is_drawing = 3  # 1.绘画中 2.绘画完成 3.绘画任务结束
    width = config["draw"]["width"]  # 图片宽度
    height = config["draw"]["height"]  # 图片高度
    DrawQueueList = queue.Queue()  # 画画队列
    physical_save_folder = config["draw"]["physical_save_folder"]  # 绘画保存图片物理路径
    # ============================================

@singleton
class NsfwData:
    # ============= 鉴黄 =====================
    nsfw_server = config["nsfw"]["nsfw_server"]
    filterEn = config["nsfw"]["filterEn"]
    filterCh = config["nsfw"]["filterCh"]
    progress_limit = config["nsfw"]["progress_limit"]  # 绘图大于多少百分比进行鉴黄，这里设置了1%
    nsfw_limit = config["nsfw"]["nsfw_limit"]  # nsfw黄图值大于多少进行绘画屏蔽【值越大越是黄图，值范围0~1】
    nsfw_progress_limit = config["nsfw"]["nsfw_progress_limit"]  # nsfw黄图-绘画进度鉴黄【值越大越是黄图，值范围0~1】
    nsfw_lock = threading.Lock()
    # ============================================

@singleton
class ImageData:
    SearchImgList = queue.Queue()
    is_SearchImg = 2  # 1.搜图中 2.搜图完成
    physical_save_folder = config["draw"]["physical_save_folder"]  # 绘画保存图片物理路径
    width = config["draw"]["width"]  # 图片宽度
    height = config["draw"]["height"]  # 图片高度

@singleton
class SearchData:
    # ============= 搜文参数 =====================
    SearchTextList = queue.Queue()
    is_SearchText = 2  # 1.搜文中 2.搜文完成
    # ============================================

@singleton
class DanceData:
    dance_path = config["obs"]["dance_path"]
    dance_video = FileUtil.get_child_file_paths(dance_path)  # 跳舞视频
    emote_path = config["obs"]["emote_path"]
    emote_font = config["obs"]["emote_font"]
    emote_video = FileUtil.get_child_file_paths(emote_path)  # 表情视频
    emote_list = FileUtil.get_subfolder_names(emote_font)  # 表情清单显示
    DanceQueueList = queue.Queue()  # 跳舞队列
    is_dance = 2  # 1.正在跳舞 2.跳舞完成
    emote_video_lock = threading.Lock()
    emote_now_path = ""
    dance_now_path = ""
    singdance_now_path = ""

@singleton
class BiliDanmakuData:
    # ============= B站直播间 =====================
    room_id = config["danmaku"]["blivedm"]["room_id"]  # 输入直播间编号
    # ******** blivedm ********
    # b站直播身份验证：
    SESSDATA = config["danmaku"]["blivedm"]["sessdata"]

    # 在B站开放平台申请的开发者密钥
    ACCESS_KEY_ID = config["danmaku"]["blivedm"]["ACCESS_KEY_ID"]
    ACCESS_KEY_SECRET = config["danmaku"]["blivedm"]["ACCESS_KEY_SECRET"]
    # 在B站开放平台创建的项目ID
    APP_ID = config["danmaku"]["blivedm"]["APP_ID"]
    # 在B站主播身份码
    ROOM_OWNER_AUTH_CODE = config["danmaku"]["blivedm"]["ROOM_OWNER_AUTH_CODE"]
    # ============================================

@singleton
class CommonData:
    # 1.b站直播间 2.api web
    mode = config["danmaku"]["mode"]
    Ai_Name: str = config["AiName"]  # Ai名称
    # 代理
    proxies = config["proxies"]["HttpProxies"]
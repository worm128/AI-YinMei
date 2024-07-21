# B站弹幕
from threading import Thread
import datetime
import uuid
from func.log.default_log import DefaultLog
from func.entrance.entrance_core import EntranceCore
from func.obs.obs_init import ObsInit
from func.tools.singleton_mode import singleton
from func.gobal.data import CommonData
from func.gobal.data import LLmData
from func.gobal.data import BiliDanmakuData

from func.tts.tts_core import TTsCore
import func.danmaku.blivedm as blivedm
import func.danmaku.blivedm.models.open_live as open_models
import func.danmaku.blivedm.models.web as web_models

import http.cookies
import asyncio, aiohttp
from typing import *

@singleton
class BlivedmCore:
    # 设置控制台日志
    log = DefaultLog().getLogger()

    session: Optional[aiohttp.ClientSession] = None

    commonData = CommonData() #公共数据
    biliDanmakuData = BiliDanmakuData()  #b站弹幕数据
    llmData = LLmData()  # llm数据
    ttsCore = TTsCore()  # 语音核心

    entranceCore = EntranceCore()  #入口操作

    def __init__(self):
        self.obs = ObsInit().get_ws()

    # blivedm弹幕监听
    async def blivedm_start(self):
        await self.run_single_client()

    # SessData会话监听
    async def blivedm_start2(self):
        global session
        self.init_session()
        try:
            await self.run_single_client2()
        finally:
            await session.close()

    def init_session(self):
        cookies = http.cookies.SimpleCookie()
        cookies["SESSDATA"] = self.biliDanmakuData.SESSDATA
        cookies["SESSDATA"]["domain"] = "bilibili.com"

        global session
        session = aiohttp.ClientSession()
        session.cookie_jar.update_cookies(cookies)

    # sessData方式监听
    async def run_single_client2(self):
        """
        演示监听一个直播间
        """
        global session

        client = blivedm.BLiveClient(self.biliDanmakuData.room_id, session=session)
        handler = self.MyHandler2(self)
        client.set_handler(handler)

        client.start()
        try:
            await client.join()
        finally:
            await client.stop_and_close()

    # 开放平台方式监听
    async def run_single_client(self):
        """
        演示监听一个直播间
        """
        client = blivedm.OpenLiveClient(
            access_key_id=self.biliDanmakuData.ACCESS_KEY_ID,
            access_key_secret=self.biliDanmakuData.ACCESS_KEY_SECRET,
            app_id=self.biliDanmakuData.APP_ID,
            room_owner_auth_code=self.biliDanmakuData.ROOM_OWNER_AUTH_CODE,
        )
        handler = self.MyHandler(self)
        client.set_handler(handler)

        client.start()
        try:
            await client.join()
        finally:
            await client.stop_and_close()

    # 监听B站直播间两个监听组合【开放平台+SessData会话】
    async def listen_blivedm_task(self):
        task1 = asyncio.create_task(self.blivedm_start())
        task2 = asyncio.create_task(self.blivedm_start2())
        results = await asyncio.gather(task1, task2)

    class MyHandler2(blivedm.BaseHandler):
        # 演示如何添加自定义回调
        _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()

        def __init__(self,BlivedmCore):
            self.BlivedmCore = BlivedmCore

        # 入场消息回调
        def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
            self.BlivedmCore.log.info(f"[{client.room_id}] INTERACT_WORD: self_type={type(self).__name__}, room_id={client.room_id},"
                     f" uname={command['data']['uname']}")
            user_name = command["data"]["uname"]  # 获取用户昵称
            user_id = command["data"]["uid"]  # 获取用户uid
            time1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.BlivedmCore.log.info(f"{time1}:粉丝[{user_name}]进入了直播间")
            # 46130941：老爸  333472479：吟美
            if all([user_id != not_allow_userid for not_allow_userid in self.BlivedmCore.llmData.welcome_not_allow]):
                # 加入欢迎列表
                self.BlivedmCore.llmData.WelcomeList.append(user_name)

        _CMD_CALLBACK_DICT['INTERACT_WORD'] = __interact_word_callback  # noqa

        def _on_heartbeat(self, client: blivedm.BLiveClient, message: web_models.HeartbeatMessage):
            self.BlivedmCore.log.info(f'[{client.room_id}] 心跳2')

    class MyHandler(blivedm.BaseHandler):

        def __init__(self,BlivedmCore):
            self.BlivedmCore = BlivedmCore

        # 心跳
        def _on_heartbeat(self, client: blivedm.BLiveClient, message: web_models.HeartbeatMessage):
            self.BlivedmCore.log.info(f'[{client.room_id}] 心跳1')

        # 弹幕获取
        def _on_open_live_danmaku(self, client: blivedm.OpenLiveClient, message: open_models.DanmakuMessage):
            self.BlivedmCore.log.info(f'{message.uname}：{message.msg}')
            traceid = str(uuid.uuid4())
            self.BlivedmCore.entranceCore.msg_deal(traceid, message.msg, message.open_id, message.uname)

        # 赠送礼物
        def _on_open_live_gift(self, client: blivedm.OpenLiveClient, message: open_models.GiftMessage):
            coin_type = '金瓜子' if message.paid else '银瓜子'
            total_coin = message.price * message.gift_num
            self.BlivedmCore.log.info(f'[{message.room_id}] {message.uname} 赠送{message.gift_name}x{message.gift_num}'
                     f' （{coin_type}x{total_coin}）')
            username = message.uname
            giftname = message.gift_name
            num = message.gift_num
            text = f"谢谢‘{username}’赠送的{num}个{giftname}"
            self.BlivedmCore.log.info(text)
            tts_say_thread = Thread(target=self.BlivedmCore.ttsCore.tts_say, args=(text,))
            tts_say_thread.start()

        def _on_open_live_buy_guard(self, client: blivedm.OpenLiveClient, message: open_models.GuardBuyMessage):
            self.BlivedmCore.log.info(f'[{message.room_id}] {message.user_info.uname} 购买 大航海等级={message.guard_level}')
            username = message.user_info.uname
            level = message.guard_level
            text = f"非常谢谢‘{username}’购买 大航海等级{level},{self.commonData.Ai_Name}大小姐在这里给你跪下了"
            self.BlivedmCore.log.info(text)
            tts_say_thread = Thread(target=self.BlivedmCore.BlivedmCore.ttsCore.tts_say, args=(text,))
            tts_say_thread.start()

        def _on_open_live_super_chat(
                self, client: blivedm.OpenLiveClient, message: open_models.SuperChatMessage
        ):
            self.BlivedmCore.log.info(f'[{message.room_id}] 醒目留言 ¥{message.rmb} {message.uname}：{message.message}')
            username = message.uname
            rmb = message.rmb
            text = f"谢谢‘{username}’赠送的¥{rmb}元,她留言说\"{message.message}\""
            self.BlivedmCore.log.info(text)
            tts_say_thread = Thread(target=self.BlivedmCore.ttsCore.tts_say, args=(text,))
            tts_say_thread.start()

        def _on_open_live_super_chat_delete(
                self, client: blivedm.OpenLiveClient, message: open_models.SuperChatDeleteMessage
        ):
            self.BlivedmCore.log.info(f'[{message.room_id}] 删除醒目留言 message_ids={message.message_ids}')

        def _on_open_live_like(self, client: blivedm.OpenLiveClient, message: open_models.LikeMessage):
            self.BlivedmCore.log.info(f'{message.uname} 点赞')
            username = message.uname
            text = f"谢谢‘{username}’点赞,{self.BlivedmCore.commonData.Ai_Name}大小姐最爱你了"
            self.BlivedmCore.log.info(text)
            tts_say_thread = Thread(target=self.BlivedmCore.ttsCore.tts_say, args=(text,))
            tts_say_thread.start()

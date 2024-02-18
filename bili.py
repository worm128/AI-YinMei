# b站直播弹幕测试
from bilibili_api import live, sync, Credential

cred = Credential(
    sessdata="",
    buvid3="",
)
room = live.LiveDanmaku("3033646", credential=cred)


@room.on("DANMU_MSG")
async def on_danmaku(event):
    # 收到弹幕
    print(event)


@room.on("SEND_GIFT")
async def on_gift(event):
    # 收到礼物
    print(event)


sync(room.connect())

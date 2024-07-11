# 搜图功能
from func.tools.singleton_mode import singleton
from func.tools.string_util import StringUtil

from func.image import search_image_util
from func.log.default_log import DefaultLog
from func.obs.obs_init import ObsInit
from func.tts.tts_core import TTsCore
from func.nsfw.nsfw_core import NsfwCore

from func.gobal.data import ImageData
from func.gobal.data import CommonData

import time
import requests
import base64
import random
from PIL import Image
from io import BytesIO

@singleton
class ImageCore:
    # 设置控制台日志
    log = DefaultLog().getLogger()

    imageData = ImageData()  #绘图数据
    commonData = CommonData()  # 公共数据

    ttsCore = TTsCore()  # 语音核心
    nsfwCore = NsfwCore()  # 鉴黄

    def __init__(self):
        self.obs = ObsInit().get_ws()

    # 搜图任务
    def check_img_search(self):
        if not self.imageData.SearchImgList.empty() and self.imageData.is_SearchImg == 2:
            self.imageData.is_SearchImg = 1
            img_search_json = self.imageData.SearchImgList.get()
            # 开始搜图任务
            self.output_img_thead(img_search_json)
            self.imageData.is_SearchImg = 2  # 搜图完成

    # 输出图片到虚拟摄像头
    def searchimg_output(self,img_search_json):
        try:
            prompt = img_search_json["prompt"]
            username = img_search_json["username"]
            # 百度搜图
            imgUrl = self.baidu_search_img(prompt)
            img_search_json2 = {"prompt": prompt, "username": username, "imgUrl": imgUrl}
            self.log.info(f"搜图内容:{img_search_json2}")
            if imgUrl is not None:
                image = self.output_search_img(imgUrl, prompt, username)
                # 虚拟摄像头输出
                if image is not None:
                    # 保存图片
                    timestamp = int(time.time())
                    path = f"{self.imageData.physical_save_folder}{prompt}_{username}_{timestamp}.jpg"
                    # 转换图像模式为RGB
                    image_rgb = image.convert("RGB")
                    image_rgb.save(path, "JPEG")
                    self.obs.show_image("绘画图片", path)
                    return 1
            return 0
        except Exception as e:
            self.log.exception(f"【searchimg_output】发生了异常：{e}")
            return 0

    # 搜索引擎-搜图任务
    def output_img_thead(self,img_search_json):
        prompt = img_search_json["prompt"]
        username = img_search_json["username"]
        try:
            img_search_json = {"prompt": prompt, "username": username}
            self.obs.show_text("状态提示", f"{self.commonData.Ai_Name}在搜图《{prompt}》")
            # 搜索并且输出图片到虚拟摄像头
            status = self.searchimg_output(img_search_json)
            self.obs.show_text("状态提示", "")
            if status == 1:
                # 加入回复列表，并且后续合成语音
                self.ttsCore.tts_say(f"回复{username}：我给你搜了一张图《{prompt}》")
            else:
                self.ttsCore.tts_say(f"回复{username}：搜索图片《{prompt}》失败")
        except Exception as e:
            self.log.exception(f"【output_img_thead】发生了异常：{e}")
        finally:
            self.log.info(f"‘{username}’搜图《{prompt}》结束")

    # 图片转换字节流
    def output_search_img(self,imgUrl, prompt, username):
        response = requests.get(imgUrl, timeout=(5, 60))
        img_data = response.content

        imgb64 = base64.b64encode(img_data)
        # ===============最终图片鉴黄====================
        status, nsfw = self.nsfwCore.nsfw_fun(imgb64, prompt, username, 5, "搜图", 0.6)
        # 鉴黄失败
        if status == -1:
            outputTxt = f"回复{username}：搜图鉴黄失败《{prompt}》-nsfw:{nsfw}，禁止执行"
            self.log.info(outputTxt)
            self.ttsCore.tts_say(outputTxt)
            return
        # 黄图情况
        if status == 0:
            outputTxt = (
                f"回复{username}：搜图发现一张黄图《{prompt}》-nsfw:{nsfw}，禁止执行"
            )
            self.log.info(outputTxt)
            self.ttsCore.tts_say(outputTxt)
            return
        outputTxt = f"回复{username}：搜图为绿色图片《{prompt}》-nsfw:{nsfw}，输出显示"
        self.log.info(outputTxt)
        # ========================================================

        # 读取二进制字节流
        img = Image.open(BytesIO(img_data))
        img = img.resize((self.imageData.width, self.imageData.height), Image.LANCZOS)
        # 字节流转换为cv2图片对象
        # image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        # 转换为RGB：由于 cv2 读出来的图片默认是 BGR，因此需要转换成 RGB
        # image = image[:, :, [2, 1, 0]]
        return img

    # 百度搜图
    def baidu_search_img(self,query):
        imageNum = 10
        # 第一次搜图
        img_search_json = {"query": query, "width": 800, "height": 600}
        images = search_image_util.baidu_get_image_url_regx(img_search_json, imageNum)
        count = len(images)
        self.log.info(f"1.搜图《{query}》数量：{count}")

        # 第二次搜图
        if count < imageNum:
            img_search_json = {"query": query, "width": 800, "height": 0}
            sec = search_image_util.baidu_get_image_url_regx(img_search_json, imageNum)
            sec_count = len(sec)
            count = count + sec_count
            images += sec
            self.log.info(f"2.搜图《{query}》数量：{sec_count}")

        if count > 0:
            random_number = random.randrange(0, count)
            return images[random_number]
        return

    # 搜图入口处理
    def msg_deal(self, traceid, query, uid, user_name):
        text = ["搜图", "搜个图", "搜图片", "搜一下图片"]
        is_contain = StringUtil.has_string_reg_list(f"^{text}", query)
        if is_contain is not None:
            num = StringUtil.is_index_contain_string(text, query)
            queryExtract = query[num: len(query)]  # 提取提问语句
            queryExtract = queryExtract.strip()
            self.log.info(f"[{traceid}]搜索图：" + queryExtract)
            if queryExtract == "":
                return True
            img_search_json = {"traceid": traceid, "prompt": queryExtract, "username": user_name}
            self.imageData.SearchImgList.put(img_search_json)
            return True
        return False
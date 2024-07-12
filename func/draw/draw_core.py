# 绘图功能
from func.tools.singleton_mode import singleton
from threading import Thread
from func.log.default_log import DefaultLog
from func.tts.tts_core import TTsCore
from func.nsfw.nsfw_core import NsfwCore

from func.gobal.data import DrawData
from func.gobal.data import NsfwData
from func.gobal.data import CommonData

from func.obs.obs_init import ObsInit
from func.tools.string_util import StringUtil
from func.translate.duckduckgo_translate import DuckduckgoTranslate

import requests
import time
import io
import base64
import random
from PIL import Image

@singleton
class DrawCore:
    # 设置控制台日志
    log = DefaultLog().getLogger()

    nsfwData = NsfwData()  #nsfw数据

    drawData = DrawData()  #绘画数据
    commonData = CommonData()  # 公共数据
    duckduckgoTranslate = DuckduckgoTranslate()  # 翻译

    ttsCore = TTsCore()  # 语音核心
    nsfwCore = NsfwCore()  #鉴黄

    def __init__(self):
        self.obs = ObsInit().get_ws()

    # 绘画任务队列
    def check_draw(self):
        if not self.drawData.DrawQueueList.empty() and self.drawData.is_drawing == 3:
            draw_json = self.drawData.DrawQueueList.get()
            self.log.info(f"启动绘画:{draw_json}")
            # 开始绘画
            draw_thread = Thread(target=self.draw, args=(draw_json["prompt"], draw_json["drawcontent"], draw_json["username"], draw_json["isExtend"]))
            draw_thread.start()


    # 绘画
    def draw(self,prompt, drawcontent, username, isExtend):
        self.drawData.is_drawing = 1

        drawName = prompt
        steps = 35
        sampler = "DPM++ SDE Karras"
        seed = -1
        cfgScale = 7
        negativePrompt = ""
        jsonPrompt = ""
        flag = 1  # 1.默认 2.特殊模型
        try:
            # 绘画标题
            if prompt != "":
                trans_json = self.duckduckgoTranslate.translate(prompt, "zh-Hans", "en")  # 翻译
                if StringUtil.has_field(trans_json, "translated"):
                    prompt = trans_json["translated"]
            # 绘画详细描述
            if drawcontent != "":
                trans_json2 = self.duckduckgoTranslate.translate(drawcontent, "zh-Hans", "en")  # 翻译
                if StringUtil.has_field(trans_json2, "translated"):
                    drawcontent = trans_json2["translated"]

            if isExtend == True:
                # C站抽取提示词：扩展提示词-扩大Ai想象力
                jsonPrompt = self.draw_prompt(prompt, 0, 50)
                if jsonPrompt == "":
                    self.log.info(f"《{drawName}》没找到绘画扩展提示词")
                    jsonPrompt = {"prompt":"","negativePrompt":"","cfgScale":cfgScale,"steps":steps,"sampler":sampler,"seed":seed}
                self.log.info(f"绘画扩展提示词:{jsonPrompt}")

            # 女孩
            # text = ["漫画", "女"]
            # num = StringUtil.is_index_contain_string(text, drawName)
            # if num>0:
            #     checkpoint = "aingdiffusion_v13"
            #     prompt = f"(({prompt})),"+jsonPrompt["prompt"]+f",{prompt},<lora:{prompt}>"
            #     if jsonPrompt!="":
            #         prompt=jsonPrompt["prompt"]+prompt
            #     negativePrompt = f"EasyNegative, (worst quality, low quality:1.4), [:(badhandv4:1.5):27],(nsfw:1.3)"
            #     flag = 2

            # 迪迦奥特曼
            # text = ["迪迦", "奥特曼"]
            # num = StringUtil.is_index_contain_string(text, drawName)
            # if num>0:
            #     checkpoint = "chilloutmix_NiPrunedFp32Fix"
            #     prompt = f"(({prompt})),masterpiece, best quality, 1boy, alien, male focus, solo, 1boy, tokusatsu,full body, (giant), railing, glowing eyes, glowing, from below , white eyes,night,  <lora:dijia:1> ,city,building,(Damaged buildings:1.3),tiltshift,(ruins:1.4),<lora:{prompt}>"
            #     if jsonPrompt!="":
            #         prompt=jsonPrompt["prompt"]+prompt
            #     flag = 2

            # 绘画扩展提示词 {"prompt":prompt,"negativePrompt":negativePrompt,"cfgScale":cfgScale,"steps":steps,"sampler":sampler,"seed":seed}
            if flag == 1:
                # 默认模型
                checkpoint = "realvisxlV30Turbo_v30TurboBakedvae"
                if jsonPrompt != "":
                    prompt = f"(({prompt},{drawcontent})),"+jsonPrompt["prompt"]+","+f"<lora:{prompt}>"
                    negativePrompt = StringUtil.isNone(jsonPrompt["negativePrompt"])
                    cfgScale = jsonPrompt["cfgScale"]
                    steps = jsonPrompt["steps"]
                    sampler = jsonPrompt["sampler"]
                    # seed = jsonPrompt["seed"]
                else:
                    prompt = f"{prompt},{drawcontent}" + f"<lora:{prompt}>"
                    negativePrompt = self.nsfwData.filterEn

            payload = {
                "prompt": prompt,
                "negative_prompt": negativePrompt,
                "hr_checkpoint_name": checkpoint,
                "refiner_checkpoint": checkpoint,
                "sampler_index": sampler,
                "steps": steps,
                "cfg_scale": cfgScale,
                "seed": seed,
                "width": self.drawData.width,
                "height": self.drawData.height,
            }
            self.log.info(f"画画参数：{payload}")

            # stable-diffusion绘图
            # 绘画进度
            progress_thread = Thread(target=self.progress, args=(drawName, username))
            progress_thread.start()
            # 生成绘画
            response = requests.post(url=f"http://{self.drawData.drawUrl}/sdapi/v1/txt2img", json=payload, timeout=(5, 60))
            self.drawData.is_drawing = 2
            r = response.json()
            # 错误码跳出
            if StringUtil.has_field(r, "error") and r["error"] != "":
                self.log.info(f"绘画生成错误:{r}")
                return
            # 读取二进制字节流
            imgb64 = r["images"][0]
            # ===============最终图片鉴黄====================
            status, nsfw = self.nsfwCore.nsfw_fun(imgb64, drawName, username, 3, "绘画", self.nsfwData.nsfw_limit)
            # 鉴黄失败
            if status == -1:
                outputTxt = f"回复{username}：绘画鉴黄失败《{drawName}》，禁止执行"
                self.log.info(outputTxt)
                self.ttsCore.tts_say(outputTxt)
                return
            # 黄图情况
            if status == 0:
                outputTxt = f"回复{username}：绘画发现一张黄图《{drawName}》，禁止执行"
                self.log.info(outputTxt)
                self.ttsCore.tts_say(outputTxt)
                return
            # ========================================================

            # ============== PIL图片对象 ==============
            img = Image.open(io.BytesIO(base64.b64decode(imgb64)))
            img = img.resize((self.drawData.width, self.drawData.height), Image.LANCZOS)
            # 保存图片-留底观察
            timestamp = int(time.time())
            path = f"{self.drawData.physical_save_folder}{drawName}_{username}_{nsfw}_{timestamp}.jpg"
            img.save(path)
            # ================= end =================

            self.obs.show_image("绘画图片", path)
            # 播报绘画
            outputTxt = f"回复{username}：我给你画了一张画《{drawName}》"
            self.log.info(outputTxt)
            self.ttsCore.tts_say(outputTxt)
        except Exception as e:
            self.log.exception(f"【draw】发生了异常：{e}")
        finally:
            self.drawData.is_drawing = 3


    # 图片生成进度
    def progress(self,prompt, username):
        while True:
            # 绘画中：输出进度图
            if self.drawData.is_drawing == 1:
                # stable-diffusion绘图进度
                response = requests.get(url=f"http://{self.drawData.drawUrl}/sdapi/v1/progress", timeout=(5, 60))
                r = response.json()
                imgb64 = r["current_image"]
                if imgb64 != "" and imgb64 is not None:
                    p = round(r["progress"] * 100, 2)
                    # ===============鉴黄, 大于**%进度进行鉴黄====================
                    try:
                        if p > self.nsfwData.progress_limit:
                            status, nsfw = self.nsfwCore.nsfw_fun(imgb64, prompt, username, 1, "绘画进度", self.nsfwData.nsfw_progress_limit)
                            # 异常鉴黄
                            if status == -1:
                                self.log.info(f"《{prompt}》进度{p}%鉴黄失败，图片不明确跳出")
                                continue
                                # 发现黄图
                            if status == 0:
                                self.log.info(f"《{prompt}》进度{p}%发现黄图-nsfw:{nsfw},进度跳过")
                                continue
                            self.log.info(f"《{prompt}》进度{p}%绿色图片-nsfw:{nsfw},输出进度图")
                            self.obs.show_text("状态提示", f"{self.commonData.Ai_Name}正在绘图《{prompt}》,进度{p}%")
                        else:
                            self.log.info(f"《{prompt}》输出进度：{p}%")
                    except Exception as e:
                        self.log.exception(f"【鉴黄】发生了异常：{e}")
                        continue
                    # ========================================================
                    # 读取二进制字节流
                    img = Image.open(io.BytesIO(base64.b64decode(imgb64)))
                    # 拉伸图片
                    img = img.resize((self.drawData.width, self.drawData.height), Image.LANCZOS)
                    # 保存图片
                    timestamp = int(time.time())
                    path = (f"{self.drawData.physical_save_folder}{prompt}_{username}_{nsfw}_{timestamp}.jpg")
                    img.save(path)
                    self.obs.show_image("绘画图片", path)
                time.sleep(1)
            elif self.drawData.is_drawing >= 2:
                self.log.info(f"《{prompt}》输出进度：100%")
                self.obs.show_text("状态提示", f"{self.commonData.Ai_Name}绘图《{prompt}》完成")
                break


    # 抽取固定扩展提示词：limit:限制条数  num:抽取次数
    def draw_prompt_do(self, query, limit, num):
        offset = 0
        jsonEnd = []
        for i in range(num):
            json = self.draw_prompt(query, 0, 100)
            jsonEnd = jsonEnd.append(json)
            if len(jsonEnd) >= limit:
                jsonEnd = json[:limit]
                return jsonEnd
            self.log.info(f"{query}抽取:" + len(jsonEnd))
            i = i + 1
            offset = offset + limit
        return jsonEnd

    # 扩展提示词
    def draw_prompt(self, query, offset, limit):
        url = "http://meilisearch-v1-6.civitai.com/multi-search"
        headers = {
            "Authorization": "Bearer 102312c2b83ea0ef9ac32e7858f742721bbfd7319a957272e746f84fd1e974af"
        }
        # 排序："stats.commentCountAllTime:desc","stats.collectedCountAllTime:desc"
        payload = {
            "queries": [
                {
                    "attributesToHighlight": [],
                    "facets": [
                        "aspectRatio",
                        "baseModel",
                        "createdAtUnix",
                        "generationTool",
                        "tagNames",
                        "user.username",
                    ],
                    "filter": ["nsfwLevel=1"],
                    "highlightPostTag": "__/ais-highlight__",
                    "highlightPreTag": "__ais-highlight__",
                    "indexUid": "images_v6",
                    "limit": limit,
                    "offset": offset,
                    "q": query,
                }
            ]
        }
        try:
            response = requests.post(url, headers=headers, json=payload, verify=False, timeout=60,
                                     proxies=self.commonData.proxies)
            r = response.json()
            hits_temp = r["results"][0]["hits"]
            hits = []
            # ========== 过滤18禁提示词: ==========
            # 参数"txt2imgHiRes"是18禁图片，"txt2img"是绿色图片；nsfw为禁黄标识：None是安全
            for json in hits_temp:
                if json["generationProcess"] == "txt2img":
                    hits.append(json)
            if len(hits) <= 0:
                return ""
            # ===================================

            # 条数处理
            count = len(hits)
            self.log.info(f"{query}>>条数：{count}")
            if count > limit:
                hits = hits[:limit]

            steps = 25
            sampler = "DPM++ SDE Karras"
            seed = -1
            cfgScale = 7
            prompt = query
            negativePrompt = ""
            if count > 0:
                num = random.randrange(0, count)
                prompt = StringUtil.filter(hits[num]["meta"]["prompt"], self.nsfwData.filterEn)
                if StringUtil.has_field(hits[num]["meta"], "negativePrompt"):
                    negativePrompt = hits[num]["meta"]["negativePrompt"]
                if StringUtil.has_field(hits[num]["meta"], "cfgScale"):
                    cfgScale = hits[num]["meta"]["cfgScale"]
                if StringUtil.has_field(hits[num]["meta"], "steps"):
                    steps = hits[num]["meta"]["steps"]
                if StringUtil.has_field(hits[num]["meta"], "sampler"):
                    sampler = hits[num]["meta"]["sampler"]
                if StringUtil.has_field(hits[num]["meta"], "seed"):
                    seed = hits[num]["meta"]["seed"]
                jsonStr = {"prompt": StringUtil.isNone(prompt),"negativePrompt": StringUtil.isNone(negativePrompt),"cfgScale": cfgScale,"steps": steps,"sampler": StringUtil.isNone(sampler),"seed": seed}
                logstr = hits[num]
                self.log.info(f"C站提示词:{logstr}")
                return jsonStr
        except Exception as e:
            self.log.exception(f"draw_prompt信息回复异常{e}")
            return ""
        return ""

    # http接口：绘画接口处理
    def http_draw(self,drawname,drawcontent,username):
        self.log.info(f'http绘画接口处理："{username}"绘画《{drawname}》，{drawcontent}')
        draw_json = {"prompt": drawname, "drawcontent":drawcontent, "username": username, "isExtend": False}
        self.drawData.DrawQueueList.put(draw_json)
        return

    # 绘画入口处理
    def msg_deal(self, traceid, query, uid, user_name):
        text = ["画画", "画一个", "画一下", "画个"]
        is_contain = StringUtil.has_string_reg_list(f"^{text}", query)
        if is_contain is not None:
            num = StringUtil.is_index_contain_string(text, query)
            queryExtract = query[num: len(query)]  # 提取提问语句
            queryExtract = queryExtract.strip()
            self.log.info(f"[{traceid}]绘画提示：" + queryExtract)
            if queryExtract == "":
                return True
            draw_json = {"traceid": traceid, "prompt": queryExtract, "drawcontent": "", "username": user_name,
                         "isExtend": True}
            # 加入绘画队列
            self.drawData.DrawQueueList.put(draw_json)
            return True
        return False
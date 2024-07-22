# 聊天功能
from func.log.default_log import DefaultLog
import re
import random
import json
import uuid
from threading import Thread
from func.tools.singleton_mode import singleton
from func.obs.obs_init import ObsInit
from func.tools.string_util import StringUtil
from func.vtuber.action_oper import ActionOper
from func.tts.tts_core import TTsCore
from func.llm.fastgpt import FastGpt
from func.llm.tgw import Tgw
from func.gobal.data import LLmData
from func.gobal.data import CommonData

@singleton
class LLmCore:
    # 设置控制台日志
    log = DefaultLog().getLogger()
    commonData = CommonData()
    llmData = LLmData()  # llm数据

    actionOper = ActionOper()  # 动作
    ttsCore = TTsCore()  #语音

    # 选择大语言模型
    local_llm_type: str = llmData.local_llm_type
    if local_llm_type == "fastgpt":
        fastGpt = FastGpt()
        llm = fastGpt
    elif local_llm_type == "text-generation-webui":
        tgw = Tgw()
        llm = tgw
    else:
        fastGpt = FastGpt()
        llm = fastGpt

    def __init__(self):
        self.obs = ObsInit().get_ws()

    # LLM回复
    def aiResponseTry(self):
        try:
            self.ai_response()
        except Exception as e:
            self.log.exception(f"【ai_response】发生了异常：")
            self.llmData.is_ai_ready = True

    # LLM回复
    def ai_response(self):
        """
        从问题队列中提取一条，生成回复并存入回复队列中
        :return:
        """
        self.llmData.is_ai_ready = False
        llm_json = self.llmData.QuestionList.get()
        # 参数提取
        uid = llm_json["uid"]
        username = llm_json["username"]
        prompt = llm_json["prompt"]
        traceid = llm_json["traceid"]

        # 用户查询标题
        title = prompt
        # query有值是搜索任务，没有值是聊天任务
        if "query" in llm_json:
            # 搜索任务的查询字符，在query字段
            title = llm_json["query"]
            self.obs.show_text("状态提示", f'{self.llmData.Ai_Name}搜索问题"{title}"')
        else:
            self.obs.show_text("状态提示", f'{self.llmData.Ai_Name}思考问题"{title}"')

        # 身份判定
        if username == "程序猿的退休生活":
            username = "老爸"

        # fastgpt
        if self.local_llm_type == "fastgpt":
            self.log.info(f"[{traceid}]{prompt}")
            # Ai角色判定：后续改成舆情判断，当前是简易字符串判断
            character = "怒怼版"  #character：ai角色、性格
            if re.search(self.llmData.public_sentiment_key, prompt):
                character = "女仆版"
            else:
                random_number = random.randrange(1, 11)
                if random_number > 4:
                    character = "怒怼版"
                else:
                    character = "女仆版"
            # fastgpt聊天
            response = self.llm.chat(prompt, uid, username, character)
        # text-generation-webui
        elif self.local_llm_type == "text-generation-webui":
            self.log.info(f"[{traceid}]{prompt}")
            response = self.llm.chat(prompt, "Winlone", "Winlone", "Aileen Voracious")
            response = response.replace("You", username)
        # obs提示
        self.obs.show_text("状态提示", f'{self.llmData.Ai_Name}思考问题"{title}"完成')

        # 处理流式回复
        all_content = ""
        temp = ""

        chatStatus = "start"
        for line in response.iter_lines():
            if line:
                # 处理收到的JSON响应
                # response_json = json.loads(line)
                str_data = line.decode("utf-8")
                str_data = str_data.replace("data: ", "")
                self.log.info(f"[{traceid}]{str_data}")
                if str_data != "[DONE]":
                    response_json = json.loads(str_data)
                    if response_json["choices"][0]["finish_reason"] != "stop":
                        # 回复内容
                        stream_content = response_json["choices"][0]["delta"]["content"]
                        if stream_content == "":
                            continue
                        # 原始全文本
                        all_content = all_content + stream_content
                        # 过滤特殊符号
                        stream_content = StringUtil.filter_html_tags(stream_content)
                        content = temp + stream_content

                        # 从右边出现的符号开始计算
                        num = StringUtil.rfind_index_contain_string(self.llmData.split_str, content)
                        if num > 0:
                            # 文本分割处理
                            split_content = content[0:num]
                            self.log.info(f"[{traceid}]分割后文本:" + split_content)

                            # 判断字符数量大于x个时候才会切割，字符太短切割音频太碎
                            if len(split_content) > self.llmData.split_limit:
                                temp = content[num: len(content)]
                                # 合成语音：文本碎片化段落
                                jsonStr = {"voiceType": "chat", "traceid": traceid, "chatStatus": chatStatus,
                                           "question": title, "text": split_content, "lanuage": "AutoChange"}
                                self.llmData.AnswerList.put(jsonStr)
                                # 第二行后面就为空
                                chatStatus = ""
                            else:
                                temp = content
                        else:
                            # 拼接到一下轮分割文本输出
                            temp = content
                    else:
                        # 结束把剩余文本输出语音
                        if temp != "":
                            # 结尾：剩余文本
                            jsonStr = {"voiceType": "chat", "traceid": traceid, "chatStatus": "end", "question": title,
                                       "text": temp, "lanuage": "AutoChange"}
                            self.llmData.AnswerList.put(jsonStr)
                        else:
                            # 结尾：空值
                            jsonStr = {"voiceType": "chat", "traceid": traceid, "chatStatus": "end", "question": title,
                                       "text": "", "lanuage": "AutoChange"}
                            self.llmData.AnswerList.put(jsonStr)
                        self.log.info(f"[{traceid}]end:" + temp)
        self.llmData.is_ai_ready = True  # 指示AI已经准备好回复下一个问题

        # 切换场景
        if "粉色" in all_content or "睡觉" in all_content or "粉红" in all_content or "房间" in all_content or "晚上" in all_content:
            self.actionOper.changeScene("粉色房间")
        elif "清晨" in all_content or "早" in all_content or "睡醒" in all_content:
            self.actionOper.changeScene("清晨房间")
        elif "祭拜" in all_content or "神社" in all_content or "寺庙" in all_content:
            self.actionOper.changeScene("神社")
        elif "花房" in all_content or "花香" in all_content:
            self.actionOper.changeScene("花房")
        elif "岸" in all_content or "海" in all_content:
            self.actionOper.changeScene("海岸花坊")

        # 日志输出
        current_question_count = self.llmData.QuestionList.qsize()
        self.log.info(f"[{traceid}][AI回复]{all_content}")
        self.log.info(f"[{traceid}]System>>[{username}]的回复已存入队列，当前剩余问题数:{current_question_count}")

    # 检查LLM回复线程
    def check_answer(self):
        """
        如果AI没有在生成回复且队列中还有问题 则创建一个生成的线程
        :return:
        """
        if not self.llmData.QuestionList.empty() and self.llmData.is_ai_ready:
            self.llmData.is_ai_ready = False
            answers_thread = Thread(target=self.aiResponseTry)
            answers_thread.start()

    # http接口:聊天
    def http_chat(self,text,uid,username):
        status = "成功"
        traceid = str(uuid.uuid4())
        if text is None:
            jsonStr = "({\"traceid\": \"" + traceid + "\",\"status\": \"值为空\",\"content\": \"" + text + "\"})"
            return jsonStr

        # 消息处理
        self.msg_deal(traceid, text, uid, username)

        jsonStr = "({\"traceid\": \"" + traceid + "\",\"status\": \"" + status + "\",\"content\": \"" + text + "\"})"
        return jsonStr

    # 进入直播间欢迎语
    def check_welcome_room(self):
        count = len(self.llmData.WelcomeList)
        numstr = ""
        if count > 1:
            numstr = f"{count}位"
        userlist = str(self.llmData.WelcomeList).replace("['", "").replace("']", "")
        if len(self.llmData.WelcomeList) > 0:
            traceid = str(uuid.uuid4())
            text = f'欢迎"{userlist}"{numstr}同学来到{self.commonData.Ai_Name}的直播间,跪求关注一下{self.commonData.Ai_Name}的直播间'
            self.log.info(f"[{traceid}]{text}")
            self.llmData.WelcomeList.clear()
            if self.llmData.is_llm_welcome == True:
                # 询问LLM
                llm_json = {"traceid": traceid, "prompt": text, "uid": 0, "username": self.commonData.Ai_Name}
                self.llmData.QuestionList.put(llm_json)  # 将弹幕消息放入队列
            else:
                self.ttsCore.tts_say(text)

    # 聊天入口处理
    def msg_deal(self, traceid, query, uid, user_name):
        # 询问LLM
        llm_json = {"traceid": traceid, "prompt": query, "uid": uid, "username": user_name}
        self.llmData.QuestionList.put(llm_json)  # 将弹幕消息放入队列
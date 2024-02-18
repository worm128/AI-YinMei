# lora训练模型加载
from transformers import AutoTokenizer, AutoModel
from peft import PeftModel, PeftConfig
import os
import torch

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
# AI基础模型路径
model_path = "ChatGLM2/THUDM/chatglm2-6b"
# 训练模型路径
# peft_model_id ="ChatGLM2/zero_nlp/chatglm_v2_6b_lora/output/lora3/checkpoint-400"


tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

# GPU运行
# 绝对路径：J:\\ai\\ai-yinmei\\ChatGLM2\\THUDM\\chatglm2-6b  相对路径：ChatGLM2/THUDM/chatglm2-6b
model = AutoModel.from_pretrained(model_path, trust_remote_code=True).cuda()
# cpu运行
# model = AutoModel.from_pretrained("ChatGLM3/THUDM/chatglm3-6b", trust_remote_code=True).float()

# 加载训练模型
model = PeftModel.from_pretrained(
    model, "LLaMA-Factory/saves/ChatGLM2-6B-Chat/lora/yinmei-20231123-ok-last"
)
model = model.merge_and_unload()
# model = PeftModel.from_pretrained(model, "ChatGLM2/zero_nlp/chatglm_v2_6b_lora/output/chatterbot/checkpoint-600")
# model = model.merge_and_unload()
# model = PeftModel.from_pretrained(model, "ChatGLM2/zero_nlp/chatglm_v2_6b_lora/output/yinmei/checkpoint-800")
# model = model.merge_and_unload()
# model = PeftModel.from_pretrained(model, "ChatGLM2/zero_nlp/chatglm_v2_6b_lora/output/yinmei1/checkpoint-1000")
# model = model.merge_and_unload()
# model = PeftModel.from_pretrained(model, "ChatGLM2/zero_nlp/chatglm_v2_6b_lora/output/ptt/checkpoint-1000")
# model = model.merge_and_unload()
model = model.eval()

history_count = 10  # 定义最大对话记忆轮数,请注意这个数值不包括扮演设置消耗的轮数，只有当enable_history为True时生效
history = []


def chat_response(prompt, history, past_key_values, return_past_key_values):
    current_length = 0
    stop_stream = False
    for response, history, past_key_values in model.stream_chat(
        tokenizer,
        prompt,
        history,
        past_key_values=past_key_values,
        return_past_key_values=return_past_key_values,
    ):
        if stop_stream:
            stop_stream = False
            break
        else:
            response[current_length:]
            current_length = len(response)
    return response, history


# 读取扮演设置
def role_set():
    global history
    print("\n开始初始化扮演设定")
    print("请注意：此时会读取并写入Role_setting.txt里的设定，行数越多占用的对话轮数就越多，请根据配置酌情设定\n")
    with open("Role_setting.txt", "r", encoding="utf-8") as f:
        role_setting = f.readlines()
    for setting in role_setting:
        role_response, history = model.chat(tokenizer, setting.strip(), history=history)
        print(f"\033[32m[设定]\033[0m：{setting.strip()}")
        print(f"\033[31m[回复]\033[0m：{role_response}\n")
    return history


if __name__ == "__main__":
    # Role_history = role_set()
    while True:
        qu = input("输入你的问题: ")
        # if len(history) >= len(Role_history)+history_count:
        #    history = Role_history + history[-history_count:]
        response, history = model.chat(tokenizer, qu, history=[])
        print(response)

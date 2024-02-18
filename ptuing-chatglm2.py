# prefix方式加载训练模型
from transformers import AutoTokenizer, AutoModel, AutoConfig
import os
import torch

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
# AI基础模型路径
model_path = "ChatGLM2/THUDM/chatglm2-6b"
# 训练模型路径
ptuning_path = "ChatGLM2/ptuning/lora2/xm7/checkpoint-100"

config = AutoConfig.from_pretrained(model_path, trust_remote_code=True, pre_seq_len=128)
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

# GPU运行
# 绝对路径：J:\\ai\\ai-yinmei\\ChatGLM2\\THUDM\\chatglm2-6b  相对路径：ChatGLM2/THUDM/chatglm2-6b
model = AutoModel.from_pretrained(
    model_path, config=config, trust_remote_code=True
).cuda()
# cpu运行
# model = AutoModel.from_pretrained("ChatGLM3/THUDM/chatglm3-6b", trust_remote_code=True).float()

# 加载训练模型
prefix_state_dict = torch.load(os.path.join(ptuning_path, "pytorch_model.bin"))
new_prefix_state_dict = {}
for k, v in prefix_state_dict.items():
    if k.startswith("transformer.prefix_encoder."):
        new_prefix_state_dict[k[len("transformer.prefix_encoder.") :]] = v
model.transformer.prefix_encoder.load_state_dict(new_prefix_state_dict)
model.transformer.prefix_encoder.float()
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

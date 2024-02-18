# chatglm3聊天测试
from transformers import AutoTokenizer, AutoModel
import os
from peft import PeftModel, PeftConfig

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
tokenizer = AutoTokenizer.from_pretrained(
    "ChatGLM3/THUDM/chatglm3-6b", trust_remote_code=True
)
# GPU运行
model = AutoModel.from_pretrained(
    "ChatGLM3/THUDM/chatglm3-6b", trust_remote_code=True
).cuda()
# cpu运行
# model = AutoModel.from_pretrained("ChatGLM3/THUDM/chatglm3-6b", trust_remote_code=True).float()

# 加载训练模型
model = PeftModel.from_pretrained(
    model, "LLaMA-Factory/saves/ChatGLM2-6B-Chat/lora/test_1/checkpoint-200"
)
model = model.merge_and_unload()
model = model.eval()


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


if __name__ == "__main__":
    history = []
    while True:
        qu = input("输入你的问题: ")
        response, history = chat_response(qu, history, None, True)
        print(response)

import time
import requests
import json

fastgpt_url = "192.168.2.198:3000"
fastgpt_authorization="Bearer fastgpt-5StPybD20P3Ymg2EDZpXe4nCjiP070TINQDRJTgBBWQhMLxDUck6W6Oeio4sx"
# fastgpt知识库接口调用-LLM回复
def chat_fastgpt(content, uid, username):
    url = f"http://{fastgpt_url}/api/v1/chat/completions"
    headers = {"Content-Type": "application/json","Authorization":fastgpt_authorization}
    timestamp = time.time()
    data={
            "chatId": timestamp,
            "stream": True,
            "detail": False,
            "variables": {
                "uid": uid,
                "name": username
            },
            "messages": [
                {
                    "content": content,
                    "role": "user"
                }
            ]
    }
    try:
        response = requests.post(
            url, headers=headers, json=data, verify=False, timeout=(3, 60), stream=True
        )
    except Exception as e:
        print(f"【{content}】信息回复异常")
        return "我听不懂你说什么"
    return response

if __name__ == "__main__":
    response = chat_fastgpt("老爸对你说:\"你丫的\"", 0, "winlone")
    # 处理流式回复
    all_content=""
    for line in response.iter_lines():
        if line:
            # 处理收到的JSON响应
            # response_json = json.loads(line)
            str_data = line.decode('utf-8')
            str_data = str_data.replace("data: ","")
            print(str_data)
            if str_data!="[DONE]":
                response_json = json.loads(str_data)
                if response_json["choices"][0]["finish_reason"]!="stop":
                    print(response_json["choices"][0]["finish_reason"])
                    content = response_json["choices"][0]["delta"]["content"]
                    print(content)
                    all_content = all_content + content
                else:
                    print("end:"+response_json["choices"][0]["finish_reason"])
    print(all_content)
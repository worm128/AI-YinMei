from duckduckgo_search import DDGS
import requests
import json
import random

proxies = {"http": "socks5://127.0.0.1:10806", "https": "socks5://127.0.0.1:10806"}

#翻译
def translate(text):
    with DDGS(proxies="socks5://localhost:10806", timeout=20) as ddgs:
        keywords = text
        r = ddgs.translate(keywords, to="en")
        print(r)
        return r

#提示词
def draw_prompt(query):
    url="http://meilisearch-v1-6.civitai.com/multi-search"
    headers = {"Authorization": "Bearer 102312c2b83ea0ef9ac32e7858f742721bbfd7319a957272e746f84fd1e974af"}
    payload = {
        "queries": [
            {
                "attributesToHighlight": [],
                "facets": [
                    "aspectRatio",
                    "baseModel",
                    "createdAtUnix",
                    "generationTool",
                    "tags.name",
                    "user.username"
                ],
                "highlightPostTag": "__/ais-highlight__",
                "highlightPreTag": "__ais-highlight__",
                "indexUid": "images_v3",
                "limit": 51,
                "offset": 0,
                "q": query
            }
        ]
    }
    try:
        response = requests.post(
            url, headers=headers, json=payload, verify=False, timeout=60, proxies=proxies
        )
        r = response.json()
        hits = r["results"][0]["hits"]
        count = len(hits)
        if count>0 :
            num = random.randrange(1, count)
            prompt = hits[num]["meta"]["prompt"]
            print(prompt)
    except Exception as e:
        print(f"draw_prompt信息回复异常")
    
if __name__ == "__main__":
    query = "jixiefsdfdsdsfren"
    text = translate(query)
    translated = text["translated"]
    draw_prompt(translated)
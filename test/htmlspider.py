import requests
from bs4 import BeautifulSoup
import jieba
import re
 
def crawl_web(url):
    response = requests.get(url)
    return response.text
 
def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()
 
def extract_content(html_content):
    # 使用正则表达式去除HTML标签和多余空格
    content = re.compile('<[^<]+?>').sub('', html_content)
    content = re.compile('[\r\n\t]').sub('', content)
    content = re.compile(' +').sub(' ', content)
    return content.strip()
 
def tokenize(text):
    return ' '.join(jieba.cut(text))
 
def search(query, documents):
    # 使用jieba分词后搜索查询
    query_tokens = tokenize(query)
    results = []
    for doc in documents:
        if query_tokens in doc:
            results.append(doc)
    return results
 
# 示例使用
url = 'https://baike.baidu.com/item/油库里'  # 替换为你想抓取的网站
html_content = crawl_web(url)
parsed_content = parse_html(html_content)
full_text = extract_content(parsed_content)
 
# 添加全文到搜索引擎
documents = [full_text]
 
# 用户输入查询
user_query = ''  # 替换为用户输入的查询
 
# 执行搜索
results = search(user_query, documents)
 
# 输出结果
for result in results:
    print(result)
import sys
import requests
from bs4 import BeautifulSoup
from func.log.default_log import DefaultLog
from func.tools.singleton_mode import singleton

@singleton
class BaiduWebsearch:
    # 设置控制台日志
    log = DefaultLog().getLogger()

    ABSTRACT_MAX_LENGTH = 300  # abstract max length

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
        ' Ubuntu Chromium/49.0.2623.108 Chrome/49.0.2623.108 Safari/537.36',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; pt-BR) AppleWebKit/533.3 '
        '(KHTML, like Gecko)  QtWeb Internet Browser/3.7 http://www.QtWeb.net',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/41.0.2228.0 Safari/537.36',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.2 (KHTML, '
        'like Gecko) ChromePlus/4.0.222.3 Chrome/4.0.222.3 Safari/532.2',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.4pre) '
        'Gecko/20070404 K-Ninja/2.1.3',
        'Mozilla/5.0 (Future Star Technologies Corp.; Star-Blade OS; x86_64; U; '
        'en-US) iNet Browser 4.7',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) '
        'Gecko/20080414 Firefox/2.0.0.13 Pogo/2.0.0.13.6866'
    ]

    # 请求头信息
    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        "Referer": "https://www.baidu.com/",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }

    baidu_host_url = "https://www.baidu.com"
    baidu_search_url = "https://www.baidu.com/s?ie=utf-8&tn=baidu&wd="

    session = requests.Session()
    session.headers = HEADERS

    def __init__(self):
        pass

    def search(self, keyword, num_results=10, debug=0):
        """
        通过关键字进行搜索
        :param keyword: 关键字
        :param num_results： 指定返回的结果个数
        :return: 结果列表
        """
        if not keyword:
            return None

        list_result = []
        page = 1

        # 起始搜索的url
        next_url = self.baidu_search_url + keyword

        # 循环遍历每一页的搜索结果，并返回下一页的url
        while len(list_result) < num_results:
            data, next_url = self.parse_html(next_url, rank_start=len(list_result))
            if data:
                list_result += data
                if debug:
                    print("---searching[{}], finish parsing page {}, results number={}: ".format(keyword, page, len(data)))
                    for d in data:
                        print(str(d))

            if not next_url:
                if debug:
                    print(u"already search the last page。")
                break
            page += 1

        if debug:
            print("\n---search [{}] finished. total results number={}！".format(keyword, len(list_result)))
        return list_result[: num_results] if len(list_result) > num_results else list_result


    def parse_html(self, url, rank_start=0, debug=0):
        """
        解析处理结果
        :param url: 需要抓取的 url
        :return:  结果列表，下一页的url
        """
        try:
            res = self.session.get(url=url)
            res.encoding = "utf-8"
            root = BeautifulSoup(res.text, "lxml")

            list_data = []
            div_contents = root.find("div", id="content_left")
            for div in div_contents.contents:
                if type(div) != type(div_contents):
                    continue

                class_list = div.get("class", [])
                if not class_list:
                    continue

                if "c-container" not in class_list:
                    continue

                title = ''
                url = ''
                abstract = ''
                try:
                    # 遍历所有找到的结果，取得标题和概要内容（50字以内）
                    if "xpath-log" in class_list:
                        if div.h3:
                            title = div.h3.text.strip()
                            url = div.h3.a['href'].strip()
                        else:
                            title = div.text.strip().split("\n", 1)[0]
                            if div.a:
                                url = div.a['href'].strip()

                        if div.find("div", class_="c-abstract"):
                            abstract = div.find("div", class_="c-abstract").text.strip()
                        elif div.div:
                            abstract = div.div.text.strip()
                        else:
                            abstract = div.text.strip().split("\n", 1)[1].strip()
                    elif "result-op" in class_list:
                        if div.h3:
                            title = div.h3.text.strip()
                            url = div.h3.a['href'].strip()
                        else:
                            title = div.text.strip().split("\n", 1)[0]
                            url = div.a['href'].strip()
                        if div.find("div", class_="c-abstract"):
                            abstract = div.find("div", class_="c-abstract").text.strip()
                        elif div.div:
                            abstract = div.div.text.strip()
                        else:
                            # abstract = div.text.strip()
                            abstract = div.text.strip().split("\n", 1)[1].strip()
                    else:
                        if div.get("tpl", "") != "se_com_default":
                            if div.get("tpl", "") == "se_st_com_abstract":
                                if len(div.contents) >= 1:
                                    title = div.h3.text.strip()
                                    if div.find("div", class_="c-abstract"):
                                        abstract = div.find("div", class_="c-abstract").text.strip()
                                    elif div.div:
                                        abstract = div.div.text.strip()
                                    else:
                                        abstract = div.text.strip()
                            else:
                                if len(div.contents) >= 2:
                                    if div.h3:
                                        title = div.h3.text.strip()
                                        url = div.h3.a['href'].strip()
                                    else:
                                        title = div.contents[0].text.strip()
                                        url = div.h3.a['href'].strip()
                                    # abstract = div.contents[-1].text
                                    if div.find("div", class_="c-abstract"):
                                        abstract = div.find("div", class_="c-abstract").text.strip()
                                    elif div.div:
                                        abstract = div.div.text.strip()
                                    else:
                                        abstract = div.text.strip()
                        else:
                            if div.h3:
                                title = div.h3.text.strip()
                                url = div.h3.a['href'].strip()
                            else:
                                title = div.contents[0].text.strip()
                                url = div.h3.a['href'].strip()
                            if div.find("div", class_="c-abstract"):
                                abstract = div.find("div", class_="c-abstract").text.strip()
                            elif div.div:
                                abstract = div.div.text.strip()
                            else:
                                abstract = div.text.strip()
                except Exception as e:
                    if debug:
                        print("catch exception duration parsing page html, e={}".format(e))
                    continue

                if self.ABSTRACT_MAX_LENGTH and len(abstract) > self.ABSTRACT_MAX_LENGTH:
                    abstract = abstract[:self.ABSTRACT_MAX_LENGTH]

                rank_start+=1
                list_data.append({"title": title, "abstract": abstract, "url": url, "rank": rank_start})


            # 找到下一页按钮
            next_btn = root.find_all("a", class_="n")

            # 已经是最后一页了，没有下一页了，此时只返回数据不再获取下一页的链接
            if len(next_btn) <= 0 or u"上一页" in next_btn[-1].text:
                return list_data, None

            next_url = self.baidu_host_url + next_btn[-1]["href"]
            return list_data, next_url
        except Exception as e:
            if debug:
                print(u"catch exception duration parsing page html, e：{}".format(e))
            return None, None


    def run(self):
        """
        主程序入口，支持命令得带参执行或者手动输入关键字
        :return:
        """
        default_keyword = u"长风破浪小武哥"
        num_results = 10
        debug = 0

        prompt = """
        baidusearch: not enough arguments
        [0]keyword: keyword what you want to search
        [1]num_results: number of results
        [2]debug: debug switch, 0-close, 1-open, default-0
        eg: baidusearch NBA
            baidusearch NBA 6
            baidusearch NBA 8 1
        """
        if len(sys.argv) > 3:
            keyword = sys.argv[1]
            try:
                num_results = int(sys.argv[2])
                debug = int(sys.argv[3])
            except:
                pass
        elif len(sys.argv) > 1:
            keyword = sys.argv[1]
        else:
            print(prompt)
            keyword = input("please input keyword: ")
            # sys.exit(1)

        if not keyword:
            keyword = default_keyword

        print("---start search: [{}], expected number of results:[{}].".format(keyword, num_results))
        results = self.search(keyword, num_results=num_results, debug=debug)

        if isinstance(results, list):
            print("search results：(total[{}]items.)".format(len(results)))
            for res in results:
                print("{}. {}\n   {}\n   {}".format(res['rank'], res["title"], res["abstract"], res["url"]))
        else:
            print("start search: [{}] failed.".format(keyword))


    if __name__ == '__main__':
        run()

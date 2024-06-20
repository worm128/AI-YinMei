import re


class StringUtil:
    # 判断集合是否包含字符
    @staticmethod
    def fuzzy_match_list(pattern, string_list):
        matches = []
        pattern = re.compile(pattern)
        for string in string_list:
            if pattern.search(string):
                matches.append(string)
        return matches

    # 判断字符位置（包含搜索字符）- 如，搜索“画画女孩”，则输出“女孩”位置
    @staticmethod
    def is_index_contain_string(string_array, target_string):
        i = 0
        for s in string_array:
            i = i + 1
            if s in target_string:
                num = target_string.find(s)
                return num + len(s)
        return 0

    # 判断字符位置（不含搜索字符）- 如，搜索“画画女孩”，则输出“画画女孩”位置
    @staticmethod
    def is_index_nocontain_string(string_array, target_string):
        i = 0
        for s in string_array:
            i = i + 1
            if s in target_string:
                return i
        return 0

    # 判断字符位置（包含搜索字符）- 如，搜索“画画女孩”，则输出“女孩”位置
    @staticmethod
    def rfind_index_contain_string(string_array, target_string):
        i = 0
        for s in string_array:
            i = i + 1
            num = target_string.rfind(s)
            if num > 0:
                return num + len(s)
        return 0

    # 正则判断[集合判断]
    @staticmethod
    def has_string_reg_list(regxlist, s):
        regx = (
            regxlist.replace("[", "(")
            .replace("]", ")")
            .replace(",", "|")
            .replace("'", "")
            .replace(" ", "")
        )
        return re.search(regx, s)


    # 判断是否none
    @staticmethod
    def isNone(text):
        if text is None:
            return ""
        return text

    # 判断包含字符
    @staticmethod
    def has_field(json_data, field):
        return field in json_data

    # 过滤函数
    def filter(text, filterPromptStr):
        fstr = filterPromptStr.replace("\\n", "")
        fstr = fstr.lower()
        str = fstr.split(",")
        for s in str:
            text = text.lower().replace(s.lower(), "")
        return text

    # 过滤html标签
    def filter_html_tags(text):
        pattern = r"\[.*?\]|<.*?>|\(.*?\)|\n"  # 匹配尖括号内的所有内容
        return re.sub(pattern, "", text)
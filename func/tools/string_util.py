import re
class StringUtil:

    #判断集合是否包含字符
    @staticmethod
    def fuzzy_match_list(pattern, string_list):
        matches = []
        pattern = re.compile(pattern)
        for string in string_list:
            if pattern.search(string):
                matches.append(string)
        return matches
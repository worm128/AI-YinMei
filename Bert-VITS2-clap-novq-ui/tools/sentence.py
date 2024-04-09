import logging

import regex as re

from tools.classify_language import classify_language, split_alpha_nonalpha


def check_is_none(item) -> bool:
    """none -> True, not none -> False"""
    return (
        item is None
        or (isinstance(item, str) and str(item).isspace())
        or str(item) == ""
    )


def markup_language(text: str, target_languages: list = None) -> str:
    pattern = (
        r"[\!\"\#\$\%\&\'\(\)\*\+\,\-\.\/\:\;\<\>\=\?\@\[\]\{\}\\\\\^\_\`"
        r"\！？。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」"
        r"『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘\'\‛\“\”\„\‟…‧﹏.]+"
    )
    sentences = re.split(pattern, text)

    pre_lang = ""
    p = 0

    if target_languages is not None:
        sorted_target_languages = sorted(target_languages)
        if sorted_target_languages in [["en", "zh"], ["en", "ja"], ["en", "ja", "zh"]]:
            new_sentences = []
            for sentence in sentences:
                new_sentences.extend(split_alpha_nonalpha(sentence))
            sentences = new_sentences

    for sentence in sentences:
        if check_is_none(sentence):
            continue

        lang = classify_language(sentence, target_languages)

        if pre_lang == "":
            text = text[:p] + text[p:].replace(
                sentence, f"[{lang.upper()}]{sentence}", 1
            )
            p += len(f"[{lang.upper()}]")
        elif pre_lang != lang:
            text = text[:p] + text[p:].replace(
                sentence, f"[{pre_lang.upper()}][{lang.upper()}]{sentence}", 1
            )
            p += len(f"[{pre_lang.upper()}][{lang.upper()}]")
        pre_lang = lang
        p += text[p:].index(sentence) + len(sentence)
    text += f"[{pre_lang.upper()}]"

    return text


def split_by_language(text: str, target_languages: list = None) -> list:
    pattern = (
        r"[\!\"\#\$\%\&\'\(\)\*\+\,\-\.\/\:\;\<\>\=\?\@\[\]\{\}\\\\\^\_\`"
        r"\！？\。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」"
        r"『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘\'\‛\“\”\„\‟…‧﹏.]+"
    )
    text = change_characters(text)
    text = change_num(text)
    sentences = re.split(pattern, text)

    pre_lang = ""
    start = 0
    end = 0
    sentences_list = []

    if target_languages is not None:
        sorted_target_languages = sorted(target_languages)
        if sorted_target_languages in [["en", "zh"], ["en", "ja"], ["en", "ja", "zh"]]:
            new_sentences = []
            for sentence in sentences:
                deal_str=sentence
                list1 = []
                while deal_str!="":
                    #同类语言字符截取
                    temp_split = split_lang(deal_str)
                    #替换第一段
                    deal_str = deal_str.replace(temp_split,"",1)
                    #加入合成语音片段
                    list1.append(temp_split)
                new_sentences.extend(list1)
                # print("分割字符:"+list1)
                # logging.debug("分割字符:"+list1)
                #new_sentences.extend(split_alpha_nonalpha(sentence))
            sentences = new_sentences

    for sentence in sentences:
        if check_is_none(sentence):
            continue

        lang = classify_language(sentence, target_languages)

        end += text[end:].index(sentence)
        if pre_lang != "" and pre_lang != lang:
            sentences_list.append((text[start:end], pre_lang))
            start = end
        end += len(sentence)
        pre_lang = lang
    sentences_list.append((text[start:], pre_lang))

    return sentences_list

# Unicode 字符编码表:https://blog.csdn.net/m372897500/article/details/37592543
def check_lang(str):
    # 日文
    if ('\u3040' <= str <= '\u309F') or ('\u30A0' <= str <= '\u30FF') or ('\u31F0' <= str <= '\u31FF'):
        return 3
    # 中文
    if '\u4e00' <= str <= '\u9fa5':
        return 1
    # 英文
    if ('\u0061' <= str <= '\u007a') or ('\u0041' <= str <= '\u005A'):
        return 2
    # 特殊字符
    return 0

def check_lang_zhfirst(str):
    # 中文
    if '\u4e00' <= str <= '\u9fa5':
        return 1
    # 英文
    if ('\u0061' <= str <= '\u007a') or ('\u0041' <= str <= '\u005A'):
        return 2
    # 日文
    if ('\u3040' <= str <= '\u309F') or ('\u30A0' <= str <= '\u30FF') or ('\u31F0' <= str <= '\u31FF'):
        return 3
    # 特殊字符
    return 0

# 按语言分割字符
def split_lang(str):
    oldflag=0
    newflag=0
    i = 0
    temp=""
    for s in str:
        newflag = check_lang(s)
        # 判断字符变化其他语言
        if i>0 and oldflag!=newflag and newflag!=0:
            return temp
        temp=temp+s
        if newflag!=0:
           oldflag = newflag
        i=i+1
    return temp

# 特殊字符发音
def change_characters(str):
    str=str.replace("_","下划线")
    str=str.replace("\\","斜杠")
    str=str.replace("/","反斜杠")
    str=str.replace("|","竖线")
    str=str.replace(".","点")
    str=str.replace("*","星号")
    str=str.replace("-","横杠")
    return str

# 替换数字
def change_num(str):
    str=str.replace("1","一")
    str=str.replace("2","二")
    str=str.replace("3","三")
    str=str.replace("4","四")
    str=str.replace("5","五")
    str=str.replace("6","六")
    str=str.replace("7","七")
    str=str.replace("8","八")
    str=str.replace("9","九")
    str=str.replace("0","零")
    return str

def sentence_split(text: str, max: int) -> list:
    pattern = r"[!(),—+\-.:;?？。，、；：]+"
    sentences = re.split(pattern, text)
    discarded_chars = re.findall(pattern, text)

    sentences_list, count, p = [], 0, 0

    # 按被分割的符号遍历
    for i, discarded_chars in enumerate(discarded_chars):
        count += len(sentences[i]) + len(discarded_chars)
        if count >= max:
            sentences_list.append(text[p : p + count].strip())
            p += count
            count = 0

    # 加入最后剩余的文本
    if p < len(text):
        sentences_list.append(text[p:])

    return sentences_list


def sentence_split_and_markup(text, max=50, lang="auto", speaker_lang=None):
    # 如果该speaker只支持一种语言
    if speaker_lang is not None and len(speaker_lang) == 1:
        if lang.upper() not in ["AUTO", "MIX"] and lang.lower() != speaker_lang[0]:
            logging.debug(
                f'lang "{lang}" is not in speaker_lang {speaker_lang},automatically set lang={speaker_lang[0]}'
            )
        lang = speaker_lang[0]

    sentences_list = []
    if lang.upper() != "MIX":
        if max <= 0:
            sentences_list.append(
                markup_language(text, speaker_lang)
                if lang.upper() == "AUTO"
                else f"[{lang.upper()}]{text}[{lang.upper()}]"
            )
        else:
            for i in sentence_split(text, max):
                if check_is_none(i):
                    continue
                sentences_list.append(
                    markup_language(i, speaker_lang)
                    if lang.upper() == "AUTO"
                    else f"[{lang.upper()}]{i}[{lang.upper()}]"
                )
    else:
        sentences_list.append(text)

    for i in sentences_list:
        logging.debug(i)

    return sentences_list


if __name__ == "__main__":
    text = "这几天心里颇不宁静。今晚在院子里坐着乘凉，忽然想起日日走过的荷塘，在这满月的光里，总该另有一番样子吧。月亮渐渐地升高了，墙外马路上孩子们的欢笑，已经听不见了；妻在屋里拍着闰儿，迷迷糊糊地哼着眠歌。我悄悄地披了大衫，带上门出去。"
    print(markup_language(text, target_languages=None))
    print(sentence_split(text, max=50))
    print(sentence_split_and_markup(text, max=50, lang="auto", speaker_lang=None))

    text = "你好，这是一段用来测试自动标注的文本。こんにちは,これは自動ラベリングのテスト用テキストです.Hello, this is a piece of text to test autotagging.你好！今天我们要介绍VITS项目，其重点是使用了GAN Duration predictor和transformer flow,并且接入了Bert模型来提升韵律。Bert embedding会在稍后介绍。"
    print(split_by_language(text, ["zh", "ja", "en"]))

    text = "vits和Bert-VITS2是tts模型。花费3days.花费3天。Take 3 days"

    print(split_by_language(text, ["zh", "ja", "en"]))
    # output: [('vits', 'en'), ('和', 'ja'), ('Bert-VITS', 'en'), ('2是', 'zh'), ('tts', 'en'), ('模型。花费3', 'zh'), ('days.', 'en'), ('花费3天。', 'zh'), ('Take 3 days', 'en')]

    print(split_by_language(text, ["zh", "en"]))
    # output: [('vits', 'en'), ('和', 'zh'), ('Bert-VITS', 'en'), ('2是', 'zh'), ('tts', 'en'), ('模型。花费3', 'zh'), ('days.', 'en'), ('花费3天。', 'zh'), ('Take 3 days', 'en')]

    text = "vits 和 Bert-VITS2 是 tts 模型。花费 3 days. 花费 3天。Take 3 days"
    print(split_by_language(text, ["zh", "en"]))
    # output: [('vits ', 'en'), ('和 ', 'zh'), ('Bert-VITS2 ', 'en'), ('是 ', 'zh'), ('tts ', 'en'), ('模型。花费 ', 'zh'), ('3 days. ', 'en'), ('花费 3天。', 'zh'), ('Take 3 days', 'en')]

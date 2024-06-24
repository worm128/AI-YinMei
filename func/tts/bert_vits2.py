# bert-vists
bert_vists_url = config["speech"]["bert_vists_url"]
speaker_name = config["speech"]["speaker_name"]
sdp_ratio = config["speech"][
    "sdp_ratio"
]  # SDP在合成时的占比，理论上此比率越高，合成的语音语调方差越大
noise = config["speech"]["noise"]  # 控制感情变化程度，默认0.2
noisew = config["speech"]["noisew"]  # 控制音节发音变化程度，默认0.9
speed = config["speech"]["speed"]  # 语速

class bertVis2:

    def __init__(self):
        return

    """
    bert-vits2语音合成
    filename：音频文件名
    text：说话文本
    emotion：情感描述
    """

    def bert_vits2(filename, text, emotion):
        save_path = f".\output\{filename}.mp3"
        text = parse.quote(text)
        response = requests.get(
            url=f"http://{bert_vists_url}/voice?text={text}&model_id=0&speaker_name={speaker_name}&sdp_ratio={sdp_ratio}&noise={noise}&noisew={noisew}&length={speed}&language=AUTO&auto_translate=false&auto_split=true&emotion={emotion}",
            timeout=(5, 60),
        )
        if response.status_code == 200:
            audio_data = response.content  # 获取音频数据
            with open(save_path, "wb") as file:
                filenum = file.write(audio_data)
                if filenum > 0:
                    return 1
        return 0

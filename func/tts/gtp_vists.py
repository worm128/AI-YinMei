from urllib import parse

# gpt-SoVITS
gtp_vists_url = config["speech"]["gtp_vists_url"]

class gtpVists:


    def __init__(self):
        return

    def gtp_vists(filename, text, emotion):
        save_path = f".\output\{filename}.mp3"
        text = parse.quote(text)
        response = requests.get(
            url=f"http://{gtp_vists_url}/?text={text}&text_language=auto", timeout=(5, 60)
        )
        if response.status_code == 200:
            audio_data = response.content  # 获取音频数据
            with open(save_path, "wb") as file:
                filenum = file.write(audio_data)
                if filenum > 0:
                    return 1
        return 0

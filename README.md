# **AI-YinMei**

- AI 虚拟主播 Vtuber 研发(N 卡版本)
- AI 名称：吟美
- 开发者：Winlone
- B 站频道：程序猿的退休生活
- B 站视频教程：https://www.bilibili.com/video/BV18b4y1V7Qm/
- Q 群：27831318
- 版本：1.6
- 详细笔记：
  现在发现有道云笔记网页版本不能查看笔记图片，需要完整教案请进入 Q 群 27831318 获取 pdf 文档<br>
  https://note.youdao.com/s/1k0x7BLt<br>
- 吟美 pdf 完整说明文档：
  在百度网盘->人工智能->吟美说明文档->AI 虚拟主播 Vtuber 研发(N 卡版本)-v1.6.pdf<br>
- 旧版吟美项目【因集成过多内置第三方项目，已废弃】：https://github.com/worm128/AI-YinMei-backup

## **介绍**

- 支持 fastgpt 知识库聊天对话
- 支持 LLM 大语言模型的一整套解决方案：[fastgpt] + [one-api] + [Xinference]
- 支持对接 bilibili 直播间弹幕回复和进入直播间欢迎语
- 支持微软 edge-tts 语音合成
- 支持聊天记忆模式和扮演卡,可以多角色切换
- 支持 AI 训练 LLaMA-Factory
- 支持表情控制 Vtuber Studio
- 支持绘画 stable-diffusion-webui 输出 OBS 直播间
- 支持绘画图片鉴黄 public-NSFW-y-distinguish
- 支持搜索和搜图服务 duckduckgo（需要魔法上网）
- 支持搜图服务 baidu 搜图（不需要魔法上网）
- 支持 AI 回复聊天框【html 插件】
- 支持 AI 唱歌
- 支持歌单【html 插件】

### 软件下载

- 在百度网盘：https://pan.baidu.com/s/1wB1aNTpN5X2WSPCq3GADJw?pwd=1kz2
- 语音播放器 mpv：语音播放、音乐播放使用
  在百度网盘->人工智能->软件->mpv.exe<br>
  注意：项目需要在根目录放两个播放器，分别是：mpv.exe【播放语音】、song.exe【播放音乐】
- 虚拟声卡：虚拟人物口型输出音频<br>
  在百度网盘->人工智能->软件->虚拟声卡 Virtual Audio Cable v4.10 破解版<br>
- ffmpeg：音频解码器，用于语音合成<br>
  在百度网盘->人工智能->软件->ffmpeg<br>

### 运行环境

- Python 3.11.6

### 调用类库

- 轻量安装（推荐-不包含 LLM 语言模型）：requirements.txt
- 全量安装（包含 LLM 语言模型、LLM 训练模型等）：requirements-all.txt
- 对应重要的 py 包<br>
  torch：2.1.0+cu121<br>
  peft：0.6.2<br>
  bilibili-api-python：16.1.1<br>
  edge-tts：6.1.9<br>
  pynput：1.7.6<br>
  APScheduler：3.10.4<br>
  transformers：4.35.2<br>
  websocket-client：1.6.4v<br>
  duckduckgo_search：4.1.1<br>
  pyvirtualcam：0.11.0<br>
  opencv-python：4.8.1.78<br>
  Flask：3.0.0<br>
  Flask-APScheduler：1.13.1<br>
  duckduckgo_search：4.1.1<br>

### 启动方式

#### 1、(必选)启动应用层，在根目录

```bash
#进入虚拟环境
& 盘符:路径/pylib/aivenv/Scripts/Activate.ps1
#安装py包
pip install -r requirements.txt
#启动对接b站直播程序
#一：1.b站直播间 2.api web
#二：1.fastgpt   1.text-generation-webui
#三：输入你的B站直播间编号
python bilibili-live-api.py
```

#### 修改内容须知：

B 站直播间鉴权（B 站浏览器获取 cookie）：sessdata、buvid3<br>
Vtuber Studio 表情 websocket 服务： <br>
ws = websocket.WebSocketApp("ws://127.0.0.1:8001",on_open = on_open)<br>
以下是表情鉴权，详细看文档【十三、Vtuber 表情控制-获取令牌和授权】：<br>
vtuber_pluginName="自定义插件名称"<br>
vtuber_pluginDeveloper="winlone"<br>
vtuber_authenticationToken="这个令牌从获取令牌接口获取"<br>
唱歌服务 Auto-Convert-Music 地址：singUrl = "192.168.2.58:1717"<br>
绘画服务 stable-diffusion-webui 地址：drawUrl = "192.168.2.58:7860"<br>
聊天服务 text-generation-webui 地址：tgwUrl = "192.168.2.58:5000"<br>
聊天服务 fastapi 知识库地址：fastapi_url = "192.168.2.198:3000"<br>
fastapi 令牌：fastapi_authorization="Bearer fastgpt-GNtIO9ApmbiFdC0R5IVkoXN5TGdGyiURh7bJ8i8CTyVINpU3GjN4Wr"<br>
搜索服务代理：duckduckgo_proxies="socks5://127.0.0.1:10806"<br>
搜图服务代理：proxies = {"http": "socks5://127.0.0.1:10806", "https": "socks5://127.0.0.1:10806"}<br>

#### 2-1、(可选)启动 LLM 聊天服务 【fastgpt】+【one-api】+【Xinference】<br>

fastgpt：https://github.com/labring/FastGPT
one-api：https://github.com/songquanpeng/one-api
Xinference：https://github.com/xorbitsai/inference
启动：使用 window WSL 的 docker 启动，启动流程看教程文档第 23 点

#### 2-2、(可选)启动 LLM 聊天服务 text-generation-webui<br>

项目 github：https://github.com/oobabooga/text-generation-webui<br>

```bash
#进入虚拟环境
& 盘符:py虚拟空间路径/Scripts/Activate.ps1
#安装py包
pip install -r requirements.txt
#启动text-generation-webui程序，start.bat是我自定义的window启动脚本
./start.bat
```

window 的 bat 启动命令：

```bash
python server.py --trust-remote-code --listen-host 0.0.0.0 --listen-port 7866 --listen --api --api-port 5000 --model chatglm2-6b --load-in-8bit --bf16
```

API 访问：http://127.0.0.1:5000/

#### 3、(必选)语音合成-Ai 发声<br>

项目地址：https://github.com/fishaudio/Bert-VITS2
启动：使用 Bert-VITS2-clap-novq-ui 里面的 start.bat 启动
定制页面：hiyoriUI.py 包含中英日混合语音合成方法，需要放到对应项目，不一定兼容

#### 4、(可选)启动绘画服务 stable-diffusion-webui<br>

项目地址：https://github.com/AUTOMATIC1111/stable-diffusion-webui<br>

```bash
#进入虚拟环境
& 盘符:py虚拟空间路径/Scripts/Activate.ps1
#安装py包
pip install -r requirements.txt
#配置api服务webui-user.bat
@echo off
set PYTHON=.\pydraw\Scripts\python.exe
set GIT=
set VENV_DIR=.\pydraw\
set COMMANDLINE_ARGS=--api
call webui.bat
#启动text-generation-webui程序，start.bat是我自定义的window启动脚本
./webui-user.bat
```

#### 5、(可选)启动绘画鉴黄服务 public-NSFW-y-distinguish<br>

项目地址：https://github.com/fd-freedom/public-NSFW-y-distinguish<br>

```bash
运行环境（必要）：Python 3.6.13
pip install -r requirements.txt
# 此文件为本人特制
py nsfw_web.py
```

#### 6、(可选)启动唱歌服务 Auto-Convert-Music<br>

原创开发者：木白 Mu_Bai、宫园薰ヾ(≧∪≦\*)ノ〃<br>
项目地址：https://github.com/MuBai-He/Auto-Convert-Music<br>

#### 7、(必选)皮肤启动，安装 steam，安装 VTube Studio<br>

这个自行下载 steam 平台，在平台里面有一个 VTube Studio 软件，它就是启动 live2D 的虚拟主播皮肤<br>

#### 8、(必选)虚拟声卡驱动<br>

安装虚拟声卡：虚拟声卡驱动（Virtual Audio Cable）4.66 官方版<br>

#### 9、(可选)AI 回复框【HTML 插件】<br>

把项目文件：ai-yinmei\html\chatui.html 放入 OBS 浏览器插件展示

#### 10、(可选)歌单显示【HTML 插件】<br>

把项目文件：ai-yinmei\html\songlist.html 放入 OBS 浏览器插件展示

#### 11、(可选)时间显示【HTML 插件】<br>

把项目文件：ai-yinmei\html\time.html 放入 OBS 浏览器插件展示

此外，需要在 text-generation-webui/models 路径放入 LLM 模型，我这里放的是 chatgml2 的模型，大家可以任意选择底层 LLM 模型，例如，千问、百川、chatglm、llama 等<br>
更多详细技术细节，请看技术文档：https://note.youdao.com/s/1k0x7BLt<br>

### 目录说明

- text-generation-webui【第三方工具】：<br>
  LLM 聚合接口，可以放置 chatglm 等大语言模型，然后进行参数配置后，再输入角色卡进行角色扮演聊天<br>
  https://github.com/oobabooga/text-generation-webui<br>
- LLaMA-Factory【AI 训练】：<br>
  AI 聚合训练工具，可以界面化配置训练参数，可视化 ai 训练，相当强大<br>
  https://github.com/hiyouga/LLaMA-Factory<br>
- ChatGLM、ChatGLM2、ChatGLM3【语言模型】：<br>
  放置的是清华大学研发的自然语言模型，可以自行添加如：百川、千问、LLAMA 等其他大语言模型<br>
- SillyTavern【第三方工具】：<br>
  酒馆，强大的 AI 角色扮演，但是该项目没有公开接口调用，而且 TTS 语言合成很缓慢，暂未集成使用<br>
  https://github.com/SillyTavern/SillyTavern<br>
- output【输出路径】：<br>
  输出的文本 txt、语音 mp3 文件都在这里<br>
- ChatGLM2\ptuning【AI 训练】：<br>
  ChatGLM 官方训练例子<br>
- ChatGLM2\ptuning\zero_nlp【AI 训练】：<br>
  ai 的 lora 训练模式

### 特别鸣谢

- 语音合成：木白 Mu_Bai、宫园薰ヾ(≧∪≦\*)ノ〃<br>
  项目地址：https://github.com/MuBai-He/Auto-Convert-Music<br>
- 知识库：FastApi<br>
  项目地址：https://github.com/labring/FastGPT<br>
- 大语言模型框架：one-api + Xinference<br>
  项目地址：https://github.com/songquanpeng/one-api<br>
  项目地址：https://github.com/xorbitsai/inference<br>
- LLM 模型：ChatGLM<br>
  https://github.com/THUDM/ChatGLM2-6B<br>
- 聚合 LLM 调用模型：text-generation-webui<br>
  https://github.com/oobabooga/text-generation-webui<br>
- AI 虚拟主播模型：B 站的·领航员未鸟·<br>
  https://github.com/AliceNavigator/AI-Vtuber-chatglm<br>
- AI 训练模型：LLaMA-Factory<br>
  https://github.com/hiyouga/LLaMA-Factory<br>
- MPV 播放器：MPV<br>
  https://github.com/mpv-player/mpv<br>
- 其他：<br>
  Lora 训练：https://github.com/yuanzhoulvpi2017/zero_nlp<br>
  ChatGLM 训练：https://github.com/hiyouga/ChatGLM-Efficient-Tuning<br>
  SillyTavern 酒馆：https://github.com/SillyTavern/SillyTavern<br>
  LoRA 中文训练：https://github.com/super-wuliao/LoRA-ChatGLM-Chinese-Alpaca<br>
  数据集-训练语料：https://github.com/codemayq/chinese-chatbot-corpus<br>

### 更多关注

- 讨论 Q 群：27831318<br>

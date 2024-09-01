# **AI-YinMei【Ai吟美】**
![Github stars](https://img.shields.io/github/stars/worm128/AI-YinMei.svg) &nbsp; ![发布版本](https://img.shields.io/badge/release-1.8.0-blue) &nbsp; ![python](https://img.shields.io/badge/python-3.11+-green)<br>
<img src="https://github.com/user-attachments/assets/48ed4c9a-e1fe-4846-9887-0842b51e9526" width="700" height="400" ><br>
【[:smile:开发文档](https://gf.bilibili.com/item/detail/1107273021)|[:heartpulse:视频教程](https://www.bilibili.com/read/cv33640951/)|[:truck:1.8整合包教程](https://www.bilibili.com/video/BV1e4421Z76E/)|[:sparkles:1.7整合包教程](https://www.bilibili.com/video/BV1zD421H76q)】<br>
- AI 虚拟主播 Vtuber 研发(N 卡版本)
- AI 名称：吟美
- 开发者：Winlone
- B站频道：[程序猿的退休生活](https://space.bilibili.com/46130941)
- 开源代码：https://github.com/worm128/AI-YinMei
- Ai吟美教程集合：https://www.bilibili.com/read/cv33640951/
- Q 群：27831318
- 版本：1.8.1
- 吟美整合包下载地址：<br>
  整合包教程：https://www.bilibili.com/video/BV1zD421H76q<br>
  <b>百度网盘群号：</b>930109408<br>
  提示：因为百度网盘分享总是屏蔽，现在切换到百度网盘的群分享，请在“百度网盘->消息” 添加群号，加入群后可以在文件列表进行下载<br>
  功能整合包下载(4个)：人工智能 -> yinmei-all<br>
  吟美核心【版本迭代】：人工智能 -> 吟美核心<br>
  吟美开发文档：人工智能 -> 吟美开发文档<br>
- 旧版吟美项目【因集成过多内置第三方项目，已废弃】：<br>
  https://github.com/worm128/AI-YinMei-backup<br>

## **技术架构**
<img width="700" alt="吟美流程图1.8.0" src="https://github.com/user-attachments/assets/1472b81e-9255-48bc-b4a4-f2b200a81513"><br>

## **支持技术**

- 支持 fastgpt 知识库聊天对话
- 支持 LLM 大语言模型的一整套解决方案：[fastgpt] + [one-api] + [Xinference]
- 支持对接 bilibili 直播间弹幕回复和进入直播间欢迎语
- 支持微软 edge-tts 语音合成
- 支持 Bert-VITS2 语音合成
- 支持 GPT-SoVITS 语音合成
- 支持表情控制 Vtuber Studio
- 支持绘画 stable-diffusion-webui 输出 OBS 直播间
- 支持绘画图片鉴黄 public-NSFW-y-distinguish
- 支持搜索和搜图服务 duckduckgo（需要魔法上网）
- 支持搜图服务 baidu 搜图（不需要魔法上网）
- 支持 AI 回复聊天框【html 插件】
- 支持 AI 唱歌 Auto-Convert-Music
- 支持歌单【html 插件】
- 支持跳舞功能
- 支持表情视频播放
- 支持摸摸头动作
- 支持砸礼物动作
- 支持唱歌自动启动伴舞功能
- 聊天和唱歌自动循环摇摆动作
- 支持多场景切换、背景音乐切换、白天黑夜自动切换场景
- 支持开放性唱歌和绘画，让 AI 自动判断内容
- 支持流式聊天，提速 LLM 回复与语音合成
- 对接 bilibili 开放平台弹幕【稳定性高】
- 支持 funasr 阿里语音识别系统
- 增加点赞、送礼物、欢迎词等触发事件
- Ai吟美桌宠【关注B站“[程序猿的退休生活](https://space.bilibili.com/46130941)”，回复181获取下载链接】

## **吟美直播间功能说明**

- 1、聊天功能：<br>
  1.1 设定了名字、性格、语气和嘲讽能力的 AI，能够与粉丝互怼，当然录入了老粉丝的信息记录，能够更好识别老粉丝的行为进行互怼。 <br>
  1.2 多重性格：吟美有善解人意的女仆和凶残怼人的大小姐性格，根据不同场景自行判断切换<br>
- 2、唱歌功能：<br>
  2.1 输入“唱歌+歌曲名称”，吟美会根据你输入的歌曲名称进行学习唱歌。当然，你可以输入类似“吟美给我推荐一首最好听的动漫歌曲”这些开放性的话题，让吟美给你智能选择歌曲进行演唱。<br>
  2.2 切歌请输入“切歌”指令，会跳过当前歌曲，直接唱下一首歌曲<br>
- 3、绘画功能：<br>
  3.1 输入“画画+图画标题”，吟美会根据你输入的绘画提示词进行实时绘画。<br>
  3.2 当然，你可以输入类似“吟美给我画一幅最丑的小龟蛋”这些开放性的话题，让吟美给你智能输出绘画提示词进行画画。<br>
- 4、跳舞功能：<br>
  4.1 输入“跳舞+舞蹈名称”，舞蹈如下：<br>
      书记舞、科目三、女团舞、社会摇 <br>
      呱呱舞、马保国、二次元、涩涩 <br>
      蔡徐坤、江南 style、Chipi、吟美 <br>
      直接输入“跳舞”两个字是随机跳舞 <br>
  4.2 停止跳舞请输入“停止跳舞” <br>
- 5、表情功能：<br>
  输入“表情+名称”, “表情+随机” 是随机表情，表情自己猜，例如，“哭、笑、吐舌头”之类<br>
- 6、场景切换功能：<br>
  6.1 输入“切换+场景名称”： 粉色房间、神社、海岸花坊、花房、清晨房间<br>
  6.2 系统智能判定时间进行早晚场景切换<br>
- 7、换装功能：<br>
  输入“换装+衣服名称”：便衣、爱的翅膀、青春猫娘、眼镜猫娘<br>
- 8、搜图功能：<br>
  输入“搜图+关键字”<br>
- 9、搜索资讯功能：<br>
  输入“搜索+关键字”<br>

- 智能辅助：<br>
  1、歌单列表显示<br>
  2、Ai 回复文字框显示<br>
  3、Ai 动作状态提示<br>
  4、智能识别唱歌和绘画<br>
  5、说话、唱歌循环随机摇摆动作<br>
  6、随着心情值增加或者当前的聊天关键字，智能判断输出日语<br>
  7、绘画提示词对接 C 站，丰富绘画内容<br>
  8、智能判断是否需要唱歌、画画<br>
  9、根据关键字进行场景切换<br>
  10、funasr 语音识别客户端<br>

### 应用模块

- Ai-YinMei：Ai 吟美核心<br>
- stable-diffusion-webui：绘画模块<br>
- public-NSFW-y-distinguish：鉴黄模块<br>
- gpt-SoVITS：语音合成模块<br>
- Auto-Convert-Music：唱歌模块<br>
- fastgpt + one-api + Xinference：聊天模块<br>
- funasr-html-client：语音识别客户端<br>

### 软件下载

整合包教程：https://www.bilibili.com/video/BV1zD421H76q<br>
百度网盘群号：930109408<br>
功能整合包下载(4个)：人工智能 -> yinmei-all<br>
吟美核心【版本迭代】：人工智能 -> 吟美核心<br>
吟美开发文档：人工智能 -> 吟美开发文档<br>

- 语音播放器 mpv：语音播放、音乐播放使用<br>
  在百度网盘->人工智能->软件->mpv.exe<br>
  注意：项目需要在根目录放两个播放器，分别是：mpv.exe【播放语音】、song.exe【播放音乐】<br>
- 虚拟声卡：虚拟人物口型输出音频<br>
  在百度网盘->人工智能->软件->虚拟声卡 Virtual Audio Cable v4.10 破解版<br>
- ffmpeg：音频解码器，用于语音合成<br>
  在百度网盘->人工智能->软件->ffmpeg<br>
- mongodb 连接工具-NoSQLBooster for MongoDB<br>
  人工智能->软件->nosqlbooster4mongo-8.1.7.exe<br>
- fastgpt 的 docker-compose 配置<br>
  人工智能->软件->docker 知识库<br>

### 运行环境

- Python 3.11.6

### 启动方式
注意：更详细的启动方法，请参考
[:fire:整合包说明文档](https://github.com/worm128/AI-YinMei/releases/download/v1.8.0/readme-v1.8.0.pdf)
[:truck:1.8整合包教程](https://www.bilibili.com/video/BV1e4421Z76E/)
<br>


#### 1、吟美核心(必选)
[下载整合包](https://github.com/worm128/AI-YinMei/releases/download/v1.8.0/AI-YinMei-v1.8.0.zip) 双击执行 start.bat <br>
[整合包说明文档](https://github.com/worm128/AI-YinMei/releases/download/v1.8.0/readme-v1.8.0.pdf) <br>

#### 2、聊天服务(可选)
##### 2-1、【fastgpt】+【one-api】+【Xinference】(推荐)<br>
fastgpt：https://github.com/labring/FastGPT<br>
one-api：https://github.com/songquanpeng/one-api<br>
Xinference：https://github.com/xorbitsai/inference<br>
启动：使用 window WSL 的 docker 启动，启动流程看教程文档第 23 点<br>
教程视频：https://www.bilibili.com/video/BV1SH4y1J7Wy/<br>

##### 2-2、text-generation-webui<br>
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

#### 3、语音合成(必选)<br>
##### 3-1、Bert-VITS2<br>
项目地址：https://github.com/fishaudio/Bert-VITS2<br>
启动：使用 Bert-VITS2-clap-novq-ui 里面的 start.bat 启动<br>
定制页面：hiyoriUI.py 包含中英日混合语音合成方法，需要放到对应项目，不一定兼容<br>
效果：Ai 与用户的语音互动，包括：聊天、绘画提示、唱歌提示、跳舞提示等<br>

##### 3-2、gtp-sovits(推荐)<br>
项目地址：https://github.com/fishaudio/Bert-VITS2<br>
效果：Ai 与用户的语音互动，包括：聊天、绘画提示、唱歌提示、跳舞提示等<br>
```bash
百度网盘群号：930109408
提示：因为百度网盘分享总是屏蔽，现在切换到百度网盘的群分享，请在“百度网盘->消息” 添加群号，加入群后可以在文件列表进行下载
双击执行 start.bat
```
[整合包说明文档](https://github.com/worm128/AI-YinMei/releases/download/v1.8.0/readme-v1.8.0.pdf) <br>

##### 3-3、edge-tts(吟美自带)<br>
edge不需要另外安装语音合成服务<br>

#### 4、绘画服务(可选)<br>
stable-diffusion-webui项目<br>
项目地址：https://github.com/AUTOMATIC1111/stable-diffusion-webui<br>
效果：输入“画画 xxx”，触发 Ai 使用 stable-diffusion 进行绘图<br>
```bash
百度网盘群号：930109408
提示：因为百度网盘分享总是屏蔽，现在切换到百度网盘的群分享，请在“百度网盘->消息” 添加群号，加入群后可以在文件列表进行下载
双击执行 start.bat 
```
[整合包说明文档](https://github.com/worm128/AI-YinMei/releases/download/v1.8.0/readme-v1.8.0.pdf) <br>


#### 5、鉴黄服务 (可选)<br>
public-NSFW-y-distinguish项目<br>
项目地址：https://github.com/fd-freedom/public-NSFW-y-distinguish<br>
```bash
百度网盘群号：930109408<br>
提示：因为百度网盘分享总是屏蔽，现在切换到百度网盘的群分享，请在“百度网盘->消息” 添加群号，加入群后可以在文件列表进行下载<br>
双击执行 start.bat <br>
```
[整合包说明文档](https://github.com/worm128/AI-YinMei/releases/download/v1.8.0/readme-v1.8.0.pdf) <br>


#### 6、唱歌服务 (可选)<br>
Auto-Convert-Music项目<br>
原创开发者：木白 Mu_Bai、宫园薰ヾ(≧∪≦\*)ノ〃<br>
项目地址：https://github.com/MuBai-He/Auto-Convert-Music<br>
启动：使用 Auto-Convert-Music 里面的 start.bat 启动<br>
效果：输入“唱歌 歌曲名称”，触发 Ai 从歌库学习唱歌<br>

#### 7、皮肤(必选)<br>
皮肤启动，安装 steam，安装 VTube Studio<br>
这个自行下载 steam 平台，在平台里面有一个 VTube Studio 软件，它就是启动 live2D 的虚拟主播皮肤<br>

#### 8、虚拟声卡驱动(必选)<br>
##### 8-1、 安装虚拟声卡：虚拟声卡驱动（Virtual Audio Cable）4.66 官方版<br>
效果：Ai 主播的发声来源
```bash
百度网盘群号：930109408
加群下载软件
```

##### 8-2、Voicemeeter虚拟声卡：<br>
[下载banana版本即可](https://voicemeeter.com/)【注意你主板要安装声卡驱动，不然虚拟声卡通道可能失效】：<br>
```bash
百度网盘群号：930109408
加群下载软件
```

#### 9、AI 回复框【HTML 插件】(可选)<br>

把项目文件：ai-yinmei\html\chatui.html 放入 OBS 浏览器插件展示<br>
效果：Ai 的回复内容会在回复插件显示<br>

#### 10、歌单显示【HTML 插件】(可选)<br>

把项目文件：ai-yinmei\html\songlist.html 放入 OBS 浏览器插件展示<br>
效果：用户点歌的歌单会在上面以列表形式显示：<br>
'xxx 用户'点播《歌曲名称》[正在播放]<br>
'xxx 用户 2'点播《歌曲名称》<br>

#### 11、时间显示【HTML 插件】(可选)<br>

把项目文件：ai-yinmei\html\time.html 放入 OBS 浏览器插件展示<br>
[整合包说明文档](https://github.com/worm128/AI-YinMei/releases/download/v1.8.0/readme-v1.8.0.pdf) <br>

#### 12、跳舞能力(可选)<br>

跳舞视频的存放地址【支持子文件夹存放】： dance_path = 'J:\\ai\\跳舞视频\\横屏'<br>
效果：输入跳舞，立即进行跳舞视频随机抽取播放；输入\停止跳舞，可以立即停止跳舞<br>

#### 13、弹出视频表情(可选)<br>

表情视频的存放地址【支持子文件夹存放】： emote_path = 'H:\\人工智能\\ai\\跳舞视频\\表情'<br>
效果：输入表情随机 或者 表情名称，立即进行表情视频播放，表情随机 为随机播放表情视频<br>
表情视频的名称展示【支持子文件夹存放】： emote_font = 'H:\\人工智能\\ai\\跳舞视频\\表情\\表情符号'<br>
效果：表情名称会显示在 obs 的字体控件，提示用户可以输入这些表情名称<br>

#### 14、funasr语音识别客户端(可选)<br>

吟美目定制funasr插件：./funasr/index.html<br>
服务端：需要根据[阿里 funasr](https://github.com/alibaba-damo-academy/FunASR/)进行配置, 建议安装容器，参考[服务器部署文档](https://github.com/alibaba-damo-academy/FunASR/blob/main/runtime/docs/SDK_advanced_guide_online_zh.md)：<br>

服务端启动：<br>
```bash
docker run -p 10095:10095 --name funasr -it --privileged=true -v /j/ai/ai-code/funasr/models:/workspace/models registry.cn-hangzhou.aliyuncs.com/funasr_repo/funasr:funasr-runtime-sdk-online-cpu-0.1.9
```

### 目录说明

- func：<br>
  吟美功能类库，全部功能源代码在这里<br>
- runtime：<br>
  整合包才有的python运行类库<br>
- html：<br>
  html插件，包含歌单列表、流式回复框、彩色回复框、功能说明框等<br>
- background：<br>
  背景图，可以在OBS软件自行添加背景图<br>
- porn：<br>
  存放鉴黄图片、绘画图片、搜图<br>
- output：<br>
  语音合成中转目录，还有歌曲、伴奏保存目录<br>
- logs：<br>
  日志输出目录<br>
- config：<br>
  OBS配置、fastgpt配置，可以参考<br>
- api.py：<br>
  接口启动主要文件<br>
- config.yml：<br>
  所有配置的文件<br>
- mpv.exe：<br>
  语音聊天播放器，输出设备设置：设置Voicemeeter第二个虚拟通道<br>
- song.exe：<br>
  人声唱歌播放器，输出设备设置：设置Voicemeeter第二个虚拟通道<br>
<img src="https://github.com/user-attachments/assets/560f0563-5915-4f5d-b5c3-b34cb0c4c0c9" width="700"><br>
- accompany.exe：<br>
  伴奏唱歌播放器，输出设备设置：设置Voicemeeter第一个虚拟通道<br>
<img src="https://github.com/user-attachments/assets/df1cc21b-d5b8-434f-ba50-115224869445" width="700"><br>

- Voicemeeter虚拟声卡官网：<br>
[下载banana版本即可](https://voicemeeter.com/)【注意你主板要安装声卡驱动，不然虚拟声卡通道可能失效】：<br>

### 特别鸣谢

- 唱歌变声：Auto-Convert-Music 开发者：木白 Mu_Bai、宫园薰ヾ(≧∪≦\*)ノ〃<br>
  项目地址：https://github.com/MuBai-He/Auto-Convert-Music<br>
- GPT-SoVITS：花儿不哭大佬开发的 TTS 语音合成<br>
  https://github.com/RVC-Boss/GPT-SoVITS<br>
- Bert-VITS2：TTS 语音合成，合成速度超快<br>
  https://github.com/fishaudio/Bert-VITS2<br>
- 知识库：fastgpt<br>
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
- 语音识别系统：FunASR<br>
  https://github.com/alibaba-damo-academy/FunASR/<br>
- 其他：<br>
  Lora 训练：https://github.com/yuanzhoulvpi2017/zero_nlp<br>
  ChatGLM 训练：https://github.com/hiyouga/ChatGLM-Efficient-Tuning<br>
  SillyTavern 酒馆：https://github.com/SillyTavern/SillyTavern<br>
  LoRA 中文训练：https://github.com/super-wuliao/LoRA-ChatGLM-Chinese-Alpaca<br>
  数据集-训练语料：https://github.com/codemayq/chinese-chatbot-corpus<br>

### 更多关注

- 讨论Q群：27831318<br>
- 我的Q号【定制化开发】：314769095<br>

### 捐献基金
捐助列表：https://docs.qq.com/sheet/DWUZPUlRrT1BXTXBk <br>
扫码赞助<br>
<img src="https://github.com/user-attachments/assets/ba090305-37f8-46b6-8057-a07af82bee60" style="width: 250px;"> <br>

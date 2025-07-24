<h1 align="center" style="font-weight: bold; font-size: 90px;">Ai吟美|一站式人工智能直播平台</h1>

<p align="right" style="font-weight: bold; font-size: 1.5em">开发者：Winlone</p>
<p align="right" style="font-weight: bold; font-size: 1.5em">B站：程序猿的退休生活</p>
<p align="right" style="font-weight: bold; font-size: 1.5em">技术Q群：27831318</p>
<p align="right" style="font-weight: bold; font-size: 1.5em">粉丝福利群：264534845</p>
<p align="right" style="font-weight: bold; font-size: 1.5em">版本：2.2.0</p>
<p align="right" style="font-weight: bold; font-size: 1.5em"><img src="https://www.yinmei.vip/images/logo.png" width="200px"/></p>
<br/><br/><br/>
<p align="center"><img src="https://www.yinmei.vip/images/%E7%9B%B4%E6%92%AD%E9%97%B4%E5%B0%81%E9%9D%A2.png" width="80%"/></p>

## 官网
https://www.yinmei.vip/  

## 项目声明
**开源版本：1.8.1**   
说明：这个版本是在github开源，但是她没有后台管理界面  
**完整版：2.3.0**  
说明：这个版本有完整后台管理界面，意图分析+情感分析+语音声纹识别+扩散思维+积分系统+用户系统等多种功能，可以在官网获取网盘下载链接，完整版不开源  

## 项目下载
**吟美整合包下载地址：**  
百度网盘群：请在“百度网盘->消息” 添加群号   
百度网盘群号1：930109408（满）  
百度网盘群号2：939447713（满）   
百度网盘群号3：945900295   
百度网盘群号4：969208563  
**夸克：**   
夸克群1：1231405830   
夸克群2：428937868   
**功能整合包下载(6个)：**  
下载路径：人工智能 -> yinmei-all  
桌宠2.0 yinmei-desktop-plus、TTS语音合成GPT-SoVITS-1.0版本和2.0版本、鉴黄public-NSFW-y-distinguish、绘画stable-diffusion-webui、Live2D皮肤  
**吟美核心【版本迭代】：**  
下载路径：人工智能 -> 吟美核心  
吟美开发文档：人工智能 -> 吟美开发文档  

## 快速配置
> 配置好以下两个配置，就可以马上进行聊天了

1、[配置聊天](https://www.yinmei.vip/#/yinmei-core?id=_2、通用ai聊天)  
2、[配置语音](https://www.yinmei.vip/#/yinmei-core?id=二、语音合成)  
3、[进行对话](https://www.yinmei.vip/#/yinmei-core?id=_23-聊天对话)  

## 功能概览
- **长期记忆：** 吟美核心、yinmei-analysis
- **短期记忆：** 吟美核心、mongodb
- **意图分析：** 吟美核心、yinmei-analysis
- **积分：** 吟美核心、mongodb
- **扩散思维：** 吟美核心、yinmei-analysis、neo4j
- **聊天：** 吟美核心、选择：阿里百炼  智谱清言  腾讯混元  百度云服务  DeepSeek  OneApi  Xinference Fastgpt
- **知识库：** 吟美核心、fastgpt【可外挂，不走fastgpt的语言模型】、Xinference、m3e
- **语音：** 吟美核心、GPT-SoVITS1.zip、GPT-SoVITS-v2.zip
- **唱歌：** 吟美核心、yinmei-music.zip、NeteaseCloudMusicApi.zip
- **绘画：** 吟美核心、stable-diffusion-webui.zip、public-NSFW-y-distinguish.zip【可选】
- **搜图：** 吟美核心、public-NSFW-y-distinguish.zip【可选】
- **搜索：** 吟美核心、vpn【可选】
- **皮肤：** 吟美核心、吟美桌宠【可选】、vtube studio【可选】
- **跳舞：** 吟美核心、OBS、本地视频
- **表情：** 吟美核心、吟美桌宠【可选】、vtube studio【可选】
- **弹幕：** 吟美核心、B站、qq机器人：napcat
- **自动化抽奖：**吟美核心、mongodb
- **MCP+自定义代码：**吟美核心、mongodb

## 指令说明
**1. 基础指令：**  
1.1 加入"\" 例如 "\我在直播间聊天"，这样ai不会对用户内容进行回复

**2. 唱歌功能：**  
2.1 输入“唱歌+歌曲名称”，吟美会根据你输入的歌曲名称进行学习唱歌。当然，你可以输入类似“吟美给我推荐一首最好听的动漫歌曲”这些开放性的话题，让吟美给你智能选择歌曲进行演唱。
2.2 切歌请输入“切歌”指令，会跳过当前歌曲，直接唱下一首歌曲
2.3 输入“停止学歌”，吟美会终止当前学歌进程，进入下一首歌曲学习

**3. 绘画功能：**  
3.1 输入“画画+图画标题”，吟美会根据你输入的绘画提示词进行实时绘画。
3.2 当然，你可以输入类似“吟美给我画一幅最丑的小龟蛋”这些开放性的话题，让吟美给你智能输出绘画提示词进行画画。

**4. 跳舞功能：**  
4.1 输入“跳舞+舞蹈名称”，舞蹈如下：
书记舞、科目三、女团舞、社会摇
呱呱舞、马保国、二次元、涩涩
蔡徐坤、江南 style、Chipi、吟美
直接输入“跳舞”两个字是随机跳舞
4.2 停止跳舞请输入“停止跳舞”

**5. 表情功能：**  
输入“表情+名称”, “表情+随机” 是随机表情，表情自己猜，例如，“哭、笑、吐舌头”之类

**6. 场景切换功能：**  
6.1 输入“切换+场景名称”： 粉色房间、神社、海岸花坊、花房、清晨房间
6.2 系统智能判定时间进行早晚场景切换

**7. 换装功能：**  
输入“换装+衣服名称”：便衣、爱的翅膀、青春猫娘、眼镜猫娘

**8. 搜图功能：**  
输入“搜图+关键字”

**9. 搜索资讯功能：**  
输入“搜索+关键字”

## 技术架构
![技术架构.png](https://github.com/user-attachments/assets/502e0295-b659-471c-a753-136b62a17f93)

## 快速启动
**下载包：**  
下载路径：在"吟美核心"文件夹  
应用包：AI-YinMei-v2.2.0.zip  
**启动方式：**
双击启动“start.bat"或者"yinmei-core-api.exe"  

![0.png](https://www.yinmei.vip/images/%E5%90%9F%E7%BE%8E%E6%A0%B8%E5%BF%83/0.png)

> 启动成功：管理后台地址

![00.png](https://www.yinmei.vip/images/%E5%90%9F%E7%BE%8E%E6%A0%B8%E5%BF%83/00.png)  
**访问地址：** http://127.0.0.1:9000  

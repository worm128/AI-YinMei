<h1 align="center" style="font-weight: bold; font-size: 90px;">Ai Yinmei | One-Stop AI Live Streaming Platform</h1>

<p align="right" style="font-weight: bold; font-size: 1.5em">Developer: Winlone</p>
<p align="right" style="font-weight: bold; font-size: 1.5em">Bilibili: A Programmer's Retirement Life</p>
<p align="right" style="font-weight: bold; font-size: 1.5em">Technical QQ Group: 27831318</p>
<p align="right" style="font-weight: bold; font-size: 1.5em">Fan Welfare Group: 264534845</p>
<p align="right" style="font-weight: bold; font-size: 1.5em">Version: 2.4.0</p>
<p align="right" style="font-weight: bold; font-size: 1.5em"><img src="https://www.yinmei.vip/images/logo.png" width="200px"/></p>
<br/><br/><br/>

<p align="center"><img src="https://www.yinmei.vip/images/%E7%9B%B4%E6%92%AD%E9%97%B4%E5%B0%81%E9%9D%A2.png" width="80%"/></p>

## Lanuage
[[中文](https://github.com/worm128/AI-YinMei) | [EN](https://github.com/worm128/AI-YinMei/blob/master/EN-README.md)]

## Video Introduction
[Desktop Pet + Voiceprint + ASR + QQ Bot](https://www.bilibili.com/video/BV1kh5TzLEv6/) <br>
[Powerful Management Backend + RAG Knowledge Base + KAG Divergent Thinking + Long-Term Memory + Intent Analysis](https://www.bilibili.com/video/BV1vFqjYBEK7) <br>
[MCP Plugin](https://www.bilibili.com/video/BV1FLuEztEGR) | [Compatible with All LLM Interfaces](https://www.bilibili.com/video/BV1NkktYTEkZ) | [Divergent Thinking](https://www.bilibili.com/video/BV15iBuY9EZ7)  

## Official Website
[https://www.yinmei.vip/](https://www.yinmei.vip/#/en/)  

## Project Statement
**Open Source Version: 1.8.1**
Note: This version is open source on GitHub, but it does not have a backend management interface.  
**Full Version: 2.4.0**
Note: This version includes a complete backend management interface, intent analysis, sentiment analysis, voiceprint recognition, diffuse thinking, a points system, a user system, and other features. A download link is available on the official website. The full version is not open source.  

## Project Download
**Yinmei Integration Package Download Address:**  
Baidu Netdisk Group: Please add the group ID in "Baidu Netdisk -> Messages"  
Baidu Netdisk Group 1: 930109408 (Full)  
Baidu Netdisk Group 2: 939447713 (Full)  
Baidu Netdisk Group 3: 945900295  
Baidu Netdisk Group 4: 969208563  
**Quark:**  
Quark Group 1: 1231405830  
Quark Group 2: 428937868  
**Function Integration Package Download (6):**  
Download Path: Artificial Intelligence -> yinmei-all  
Desktop Pet 2.0 yinmei-desktop-plus, TTS speech synthesis GPT-SoVITS-versions 1.0 and 2.0, porn detection public-NSFW-y-distinguish, painting stable-diffusion-webui, Live2D skin  
**Yinmei Core [Version Iteration]:**  
Download Path: Artificial Intelligence -> Yinmei Core  
Yinmei Development Documentation: Artificial Intelligence -> Yinmei Development Documentation  

## Quick Configuration
> Configure the following two settings to start chatting immediately.  

1. [Configure Chat](https://www.yinmei.vip/#/yinmei-core?id=_2, General AI Chat)  
2. [Configure Voice](https://www.yinmei.vip/#/yinmei-core?id=_2, Voice Synthesis)  
3. [Start a Conversation](https://www.yinmei.vip/#/yinmei-core?id=_23, Chat Conversation)  

## Function Overview
- **Aggregated Bullet Comments:** Aggregates live stream bullet comments, supporting the display of bullet comments from 9 major sources including Bilibili development platform, Napcat [QQ robot], Barragefly [Douyin, Huya, Kuaishou, Douyu], WeChat live stream, desktop pets, and background chat dialogues.
- **Intent Analysis:** Intent analysis with a 10ms response time can be used to train corpora to increase intent classification. Currently, it uses a multi-head attention mechanism, which can simultaneously analyze intent classification and sentiment classification.
- **Large Model Tools:** Supports MCP tools and custom-written code tools. Tools include: camera observation, timed patrol, visual capabilities, image search, greeting functionality, Wikipedia, TMDB movie rating website, browser manipulation, calculator, user points query, advanced search, thought chain, product information query, stock tools, time zone conversion, random number generation, cooking guide, changing character clothing, character movement and rotation, video search and playback, speech synthesis switch, speech speed adjustment, AI video, AI singing, AI painting, search tools, and 27 other tools.
- **Lottery:** The lottery is divided into self-service lotteries and streamer lotteries. Self-service lotteries are initiated by users entering "lottery" in the chat, while streamer lotteries are conducted by the streamer who clicks the lottery button to draw prizes from all online users in the live stream. Features include a list of lottery prizes and lottery records.
- **Long-term memory:** Intelligently recalls memories from different time periods based on time pronouns. It selectively recalls memories, avoiding impacting the main workflow speed by activating memories every time. The number of times a memory is recalled, its similarity, etc., can be set.
- **Short-term memory:** Recorded in the large model context memory of the MongoDB database, all chat records are fully persisted.
**Points:** Each user earns points for chatting, liking, sending gifts, and registering. Singing, drawing, playing videos, switching songs, and participating in raffles will deduct points. Points configuration options are available.
- **Diffusion Thinking:** Using the graph relation database neo4j to construct word relationships, you can export q-group data for thinking relationship training, and the analyzed graph will be displayed in neo4j.
- **Chat:** Supports all cloud service providers and local services that meet the OpenAI specification, with 100% coverage of large LLM models. LLM is streamed for high-performance dialogue.
- **Voice Support:** Supports Cosyvoice2, Bert-Vits2, the entire GPT-Sovits series, and Edge-TTS. OpenAI-compliant TTS is supported by 80% of TTS cloud providers on the market. Cosyvoice2 has been significantly modified and tweaked for tone and emotion, and VLLM acceleration has been implemented, making it stronger and faster than other speech synthesizers on the market. Voice is streamed for high-performance TTS.
- **Vision:** Supports OpenAI-compliant data models and visual models from most cloud vendors.
- **Camera:** Supports multi-camera monitoring and analysis
- **Computer Control:** Supports the computer to autonomously control the keyboard and mouse based on screen analysis.
- **Live Streaming UI Plugins:** Supports 18 UI plugins to assist with live streaming.
- **Knowledge Base:** Currently using FastGPT knowledge base capabilities for knowledge management and loading.
- **Singing:** It can cover songs in any language. It takes about 150 to 200 seconds to learn a song. The singing model can train its own tone.
- **Painting:** Supports downloading any painting model from civitai.com for drawing.
- **Image Search:** Use Baidu search to search for images.
- **Search:** Use the search aggregation platform searchng, which includes search engines such as Google, Bing, duckduckgo, Wikipedia, startpage, and brave. Requires a VPN.
- **Characters:** Supports the self-developed Yinmei desktop pet and Vtube Studio [available for download on Steam or the product's cloud drive]. The Yinmei desktop pet comes with a built-in microphone, powerful noise reduction, VAD, and AEC capabilities, and is overlaid with a voiceprint system, ensuring real-time conversations without accidental touches.
- **Emojis:** There are emoji schemes that can control character expressions, supporting the playback of character expressions + sound effects + video, supporting loop playback and random playback, and keyword-triggered emojis.
- **Videos:** Can play any video within a local folder, and supports videos stored in subfolders. Supports pulling and playing videos from Bilibili.
- **NSFW:** Supports image content moderation, can filter illegal characters in comments, provides AI responses to illegal characters, and draws prompts for illegal words.
- **Other:** Supports off-peak tasks, supports welcome messages upon entering a room, supports intelligent installation of Docker services, supports server monitoring, and supports data statistics.

## Command Description
**1. Basic Commands:**  
1.1 Add "\" for example "\I'm chatting in the livestream." This will prevent the AI from responding to user content.

**2. Singing Function:**

2.1 Enter "sing" + song title, and Yinmei will learn to sing based on the song title you enter. You can also enter open-ended topics like "Yinmei, recommend me the best anime song," and Yinmei will intelligently select a song for you to sing.

2.2 To change songs, enter "Cut Song" to skip the current song and move directly to the next one.

2.3 Enter "Stop Learning Song," and Yinmei will terminate the current song and move on to the next one.

**3. Drawing Function:**

3.1 Enter "drawing" + picture title, and Yinmei will draw in real time based on the drawing prompt you enter.

3.2 You can also enter open-ended topics like "Yinmei, draw me the ugliest little turtle egg," and Yinmei will intelligently generate drawing prompts for you to draw.

**4. Dance Function:**

4.1 Enter "video + dance name". Dances are as follows:

Secretary Dance, Subject Three, Girl Group Dance, Social Dance

Guagua Dance, Ma Baoguo, Anime, Sese

Cai Xukun, Gangnam Style, Chipi, Yinmei

Directly enter "video" for a random dance.

4.2 To stop dancing, enter "Stop Video."

**5. Emoji Function:**

Enter "emoji + name." "emoji + random" is a random emoji. You can guess the emoji yourself, for example, "crying, laughing, sticking out tongue."

**6. Scene Switching Function:**

6.1 Enter "Switch + Scene Name": Pink Room, Shrine, Coastal Flower Shop, Flower Room, Morning Room.

6.2 The system intelligently determines the time to switch between morning and evening scenes.

**7. Dress-Up Function:**

Enter "Outfit + Outfit Name": Plain Clothes, Wings of Love, Youthful Cat Girl, Glasses Cat Girl

**8. Image Search Function:** Enter "search image + keyword"

**9. Search Information Function:**
Enter "search + keyword"

## Technical Architecture
![技术架构.png](https://www.yinmei.vip/images/吟美流程图2.4.1.png)
![聊天异步流程.png](https://www.yinmei.vip/images/聊天异步流程.png)
![吟美工具调用.png](https://www.yinmei.vip/images/吟美工具调用.png)
![意图分析.png](https://www.yinmei.vip/images/意图分析.png)
![流式语音.png](https://www.yinmei.vip/images/流式语音.png)
![聚合弹幕.png](https://www.yinmei.vip/images/聚合弹幕.png)  

## Quick Start 
**Download package:** 
Download path: in the "Yinmei Core" folder 
Application package: AI-YinMei-v2.4.0.zip 
**Startup Method:** 
Double-click to launch "start.bat" or "yinmei-core-api.exe" 
![0.png](https://www.yinmei.vip/images/yinmei-core/0.png) 
![0.png](https://www.yinmei.vip/images/comm/4.png) 
 
> Startup successful: Management backend address 
 
![00.png](https://www.yinmei.vip/images/comm/5.png) 
**Access address:** http://127.0.0.1:9000

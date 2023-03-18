import asyncio, discord
from discord.ext import commands
import  datetime, pytz
import random
import time , os
from discord.ui import View, Select, Button
from youtube_dl import YoutubeDL
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from discord.utils import get
from discord import FFmpegPCMAudio
from urllib import request
from discord.ui import Button, View
from discord.utils import get
from user import *
from game import *

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='치처아 ', intents=intents)
client = discord.Client(intents=intents)

user = []
musictitle = []
musicnow = []
song_queue = []

userF = []
userFlist = []
allplaulist = []

number = 1

def title(msg):
    global music

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    chromedriver_dir = r"D:\Discord_Bot\chromedriver.exe"
    driver = webdriver.Chrome(chromedriver_dir, options = options)
    driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, 'lxml')
    entire = bs.find_all('a', {'id': 'video-title'})
    entireNum = entire[0]
    music = entireNum.text.strip()
    
    musictitle.append(music)
    musicnow.append(music)
    test1 = entireNum.get('href')
    url = 'https://www.youtube.com'+test1
    with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
    URL = info['formats'][0]['url']

    driver.quit()
    
    return music, URL

def URLPLAY(url):
    YDL_OPTIONS = {'format': 'bestaudio','noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if not vc.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        client.loop.create_task(subtitle_song(ctx, URL))

async def subtitle_song(ctx, suburl):
    TEXT = suburl
    rink = TEXT[-11:]
    target = request.urlopen("http://video.google.com/timedtext?type=list&v="+rink)

    soup = bs4.BeautifulSoup(target, "html.parser")
    sub = 0
    kor = 0
    for track in soup.select("track"):
        if sub == 0:
            firstsub = track['lang_code']
        if track['lang_code'] == 'ko':
            kor += 1
        sub += 1

    if sub == 0: #자막이 없음
        await ctx.send("""
        ```
        유튜브 자막이 포함되지 않은 영상입니다!
        ```
        """)
        return 0

    elif kor == 0 and sub != 0: #한글이 아닌 자막 재생
        target = request.urlopen("http://video.google.com/timedtext?lang="+firstsub+"&v="+rink)
        
    elif kor == 1 and sub != 0:  #한글 자막 재생
        target = request.urlopen("http://video.google.com/timedtext?lang=ko&v="+rink)

    soup = bs4.BeautifulSoup(target, "html.parser")
    subtimedur = []
    subtimelast = []
    last_time = 0
    subtext = []

    for text in soup.select("text"):
        subtimedur.append(text['start'])
        subtimelast.append(text['dur'])
        subtext.append(text.string)
    
    for i in range(len(subtext)):
        last_time += 1
        embed = discord.Embed(description=subtext[i], color=0x00ff00)
        if i == 0:
            time.sleep(float(subtimedur[i]))
            sub_message = await ctx.send(embed = embed)
        else:
            time.sleep(float(subtimedur[i]) - float(subtimedur[i-1]) - float(0.1))
            await sub_message.edit(embed = embed)
        
    time.sleep(subtimelast[last_time])

    await sub_message.delete()
    del subtimedur [:]
    del subtext [:]

def play(ctx):
    global vc
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    URL = song_queue[0]
    del user[0]
    del musictitle[0]
    del song_queue[0]
    vc = get(bot.voice_clients, guild=ctx.guild)
    if not vc.is_playing():
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx)) 
        (client.loop.create_task(subtitle_song(ctx, URL)))

def play_next(ctx):
    if len(musicnow) - len(user) >= 2:
        for i in range(len(musicnow) - len(user) - 1):
            del musicnow[0]
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    if len(user) >= 1:
        if not vc.is_playing():
            del musicnow[0]
            URL = song_queue[0]
            del user[0]
            del musictitle[0]
            del song_queue[0]
            vc.play(discord.FFmpegPCMAudio(URL,**FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
            (client.loop.create_task(subtitle_song(ctx, URL)))

    else:
        if not vc.is_playing():
            client.loop.create_task(vc.disconnect())

def again(ctx, url):
    global number
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    if number:
        with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        if not vc.is_playing():
            vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after = lambda e: again(ctx, url))

def load_chrome_driver():

    options = webdriver.ChromeOptions()

    options.binary_location = os.getenv('GOOGLE_CHROME_BIN')

    options.add_argument('--headless')
    options.add_argument('--no-sandbox')

    return webdriver.Chrome(executable_path = str(os.environ.get('CHROME_EXECUTABLE_PATH')), chrome_options=options)

@bot.event
async def on_ready():
    print("We have loggedd in as {0.user}".format(bot))
    server = len(bot.guilds)
    message = [f"{round(bot.latency*1000)}ms", "치처 야 이라고 부르세요!", f"{server}서버 있는것!"]
    await bot.tree.sync()
    while True:
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(message[0]))
        message.append(message.pop(0))
        await asyncio.sleep(3)

bad = ['ㅅㅂ','시발','씨발','미친','ㅁㅊ','썌기','ㅅㅂㄴ','시발놈','씨발놈','ㅁㅊㄴ','미친놈','나쁜놈','ㄴㅃㄴ','죽어','ㅈㅇ','죽어 섀기놈아','ㅈㅇ ㅅㄱㄴㅇ','너 죽으래 시발 썌기 놈아!']

science = {"51x48=" : "2448"}
check = False
b = ""

science = {"현무암이란?" : "현무암은 회색~흑색의 분출 화산암"}
check = False
d = ""

@bot.event
async def on_message(message):
    global science, b, check, mod, d
    if message.author.bot:
        return None
    if message.content.startswith("치처 야"):
        await message.channel.send("민섭 E이 여기있습니다!")

    if message.content.startswith("치처 게임"):
        await message.channel.send("전 게임를 못합니다...")
    
    if message.content.startswith("치처 봇 여기로 초대함?"):
        await message.channel.send("봇은 9월12일날에 생성 되어고 들어온날짜은 11월 16일입니다. ")
    
    if message.content.startswith("치처 다른거 은?"):
        await message.channel.send("안됨니다.")

    message_contant=message.content
    for i in bad:
        if i in message_contant:
            await message.delete()
            embed = discord.Embed(title="🚨욕설 감지🚨", color=0xFF0000)
            embed.add_field(name="닉네임 : ", value=message.author, inline=False)
            await message.channel.send(embed=embed)

    if message.content.startswith("치처 주사위"):
        r = random.randint(1, 50)
        if r == 1:
            await message.channel.send("1!")
        
        if r == 2:
            await message.channel.send("2!")
        
        if r == 3:
            await message.channel.send("3!")
        
        if r == 4:
            await message.channel.send("4!")

        if r == 5:
            await message.channel.send("5!")

        if r == 6: 
            await message.channel.send("6!")

        if r == 7: 
            await message.channel.send("7!")

        if r == 8: 
            await message.channel.send("8!")

        if r == 9: 
            await message.channel.send("9!")

        if r == 10: 
            await message.channel.send("10!")

        if r == 11:
            await message.channel.send("11!")
        
        if r == 12:
            await message.channel.send("12!")
        
        if r == 13:
            await message.channel.send("13!")
        
        if r == 14:
            await message.channel.send("14!")

        if r == 15:
            await message.channel.send("15!")

        if r == 16: 
            await message.channel.send("16!")

        if r == 17: 
            await message.channel.send("17!")

        if r == 18: 
            await message.channel.send("18!")

        if r == 19: 
            await message.channel.send("19!")

        if r == 20: 
            await message.channel.send("20!")

        if r == 21:
            await message.channel.send("21!")
        
        if r == 22:
            await message.channel.send("22!")

        if r == 23:
            await message.channel.send("23!")
        
        if r == 24:
            await message.channel.send("24!")

        if r == 25:
            await message.channel.send("25!")

        if r == 26: 
            await message.channel.send("26!")

        if r == 27: 
            await message.channel.send("27!")

        if r == 28: 
            await message.channel.send("28!")

        if r == 29: 
            await message.channel.send("29!")

        if r == 30: 
            await message.channel.send("30!")

        if r == 31:
            await message.channel.send("31!")
        
        if r == 32:
            await message.channel.send("32!")
        
        if r == 33:
            await message.channel.send("33!")
        
        if r == 34:
            await message.channel.send("34!")

        if r == 35:
            await message.channel.send("35!")

        if r == 36: 
            await message.channel.send("36!")

        if r == 37: 
            await message.channel.send("37!")

        if r == 38: 
            await message.channel.send("38!")

        if r == 39: 
            await message.channel.send("39!")

        if r == 40: 
            await message.channel.send("40!")

        if r == 41:
            await message.channel.send("41!")
        
        if r == 42:
            await message.channel.send("42!")
        
        if r == 43:
            await message.channel.send("43!")
        
        if r == 44:
            await message.channel.send("44!")

        if r == 45:
            await message.channel.send("45!")

        if r == 46: 
            await message.channel.send("46!")

        if r == 47: 
            await message.channel.send("47!")

        if r == 48: 
            await message.channel.send("48!")

        if r == 49: 
            await message.channel.send("49!")

        if r == 50: 
            await message.channel.send("50!!!!")

    if message.content.startswith("치처 프로필"):
        date = datetime.datetime.utcfromtimestamp(((int(message.author.id) >> 22) + 1420070400000) / 1000)
        embed = discord.Embed(color=0x00D8FF)
        embed.add_field(name="닉네임 : ", value=message.author, inline=False)
        embed.add_field(name="서버닉네임 : ", value=message.author.display_name, inline=False)
        embed.add_field(name="가입일 : ", value=str(date.year) + "년" + str(date.month) + "월" + str(date.day) + "일", inline=False)
        embed.add_field(name="아이디 : ", value=message.author.id, inline=False)
        await message.channel.send(embed=embed)

    if message.content.startswith("치처 바보임?"):
        embed = discord.Embed(color=0x1DDB16)
        embed.add_field(name="아닙니다.", value="절떄로 바보 아닙니다.")
        embed.add_field(name="경고 지급 예정 입니다.", value="바보 하지 말아 주세요. 도배하면 경고 X 로 들어 갑니다.")
        await message.channel.send(embed=embed)

    if message.content.startswith('치처 추방'):
            member = message.guild.get_member(int(message.content.split(" ")[1]))
            await message.guild.kick(member, reason=' '.join(message.content.split(" ")[2:]))

    if message.content.startswith("치처 밴"):
        if message.author.guild_permissions.administrator: ##관리자만 사용 가능
            member = message.guild.get_member(int(message.content.split(" ")[1]))
            await message.guild.ban(member, reason=' '.join(message.content.split(" ")[2:]))

 ##만약 await message.guild.ban 이라는거은 사용자가 메시지를 차단 합니다.

    if message.content.startswith("!퀴즈"):
        subject = message.content[4:]
        if subject == "수학":
            a = random.choice(list(science.keys()))
            b = science[a]
            check = True
            await message.channel.send("`" + a + "`")

        elif check == False:
            await message.channel.send("`이미 퀴즈를 푸시는 중 입니다. 모르겠다면 !패스 해주세요.`")

    if message.content.startswith("!정답"):
        if check == True:
            answer = message.content[4:]
            if answer == d:
                check = False
                embed = discord.Embed(title="!정답!", color=0x2FED28)
                await message.channel.send(embed = embed)
            elif answer != d:
                embed = discord.Embed(title="오답..", color=0xFF0000)
                await message.channel.send(embed = embed)

        elif check == False:
                await message.channel.send("폴고 있는 퀴즈가 없습니다.")

    if message.content.startswith("!패스"):
        if check == True:
            embed = discord.Embed(title="#패스#", color=0xFFE400)
            await message.channel.send(embed = embed)
            await message.channel.send("`정답은 '" + d + "` 였습니다. \n문제를 패스 하셨습니다.")
        elif check == False:
            await message.channel.send("`폴고 있는 퀴즈가 없습니다.`")

    if message.content.startswith("!퀴즈"):
        subject = message.content[4:]
        if subject == "과학":
            c = random.choice(list(science.keys()))
            d = science[c]
            check = True
            await message.channel.send("`" + c + "`")

        elif check == False:
            await message.channel.send("`이미 퀴즈를 푸시는 중 입니다. 모르겠다면 !패스 해주세요.`")

    if message.content.startswith("!정답"):
        if check == True:
            answer = message.content[4:]
            if answer == d:
                check = False
                embed = discord.Embed(title="!정답!", color=0x2FED28)
                await message.channel.send(embed = embed)
            elif answer != d:
                embed = discord.Embed(title="오답..", color=0xFF0000)
                await message.channel.send(embed = embed)

        elif check == False:
                await message.channel.send("폴고 있는 퀴즈가 없습니다.")

    if message.content.startswith("!패스"):
        if check == True:
            embed = discord.Embed(title="#패스#", color=0xFFE400)
            await message.channel.send(embed = embed)
            await message.channel.send("`정답은 '" + d + "` 였습니다. \n문제를 패스 하셨습니다.")
        elif check == False:
            await message.channel.send("`폴고 있는 퀴즈가 없습니다.`")
    
    if message.content.startswith("!규칙"):
        if(message.author.guild_permissions.administrator):
            embed = discord.Embed(title="규칙")
            embed.add_field(name="채팅에서 도배할시 👉 경고 I", value="도배은 안돼요~ 채팅방에서~", inline=False)
            embed.add_field(name="욕 보내며 , 음성 말하며👉 경고 I", value="욕 사용 할시 경고 들어갑니다.", inline=False)
            embed.add_field(name="도배방에서 수상함 링크 보내며 👉 경고 I", value="도배방에서 링크 의심 하면 경고 들어갑니다.", inline=False)
            embed.add_field(name="도배방에서 조금 더 수상함 링크 보내며 👉 경고 II", value="도배방에서 링크 의심 하면 경고 들어갑니다.", inline=False)
            embed.add_field(name="도배방에서 더 수상함 링크 보ㅐ며 👉 경고 III", value="도배방에서 링크 의심 하면 경고 들어갑니다.", inline=False)
            embed.add_field(name="도배방에서 덜 수상함 링크 보ㅐ며 👉 경고 IV", value="도배방에서 링크 의심 하면 경고 들어갑니다.", inline=False)
            embed.add_field(name="도배방에서 덜 마이 수상함 링크 보ㅐ며 👉 경고 V", value="도배방에서 링크 의심 하면 경고 들어갑니다.", inline=False)
            embed.add_field(name="도배방에서 심각하 링크 보ㅐ며 👉 경고 VI", value="도배방에서 링크 의심 하면 경고 들어갑니다.", inline=False)
            embed.add_field(name="도배방에서 조금 심각하 링크 보ㅐ며 👉 경고 VII", value="도배방에서 링크 의심 하면 경고 들어갑니다.", inline=False)
            embed.add_field(name="도배방에서 조금 마이 심각하 링크 보ㅐ며 👉 경고 VIII", value="도배방에서 링크 의심 하면 경고 들어갑니다.", inline=False)
            embed.add_field(name="도배방에서 조금 위험하 링크 보ㅐ며 👉 경고 IX + 타임아옷 1일", value="도배방에서 링크 의심 하면 경고 들어갑니다.", inline=False)
            embed.add_field(name="도배방에서 위험하 링크 보ㅐ며 👉 경고 X + 타임아옷 1주일", value="도배방에서 링크 의심 하면 경고 들어갑니다.", inline=False)
            embed.add_field(name="요즘 계정 밴하고 부꼐 들어올시👉 경고 X + 타임아옷 1주일 + 즉시 밴 ", value="요즘 계정은 밴하고 부계정 들어 주시면 경고 추방 하겠습니다.", inline=False)
            embed.add_field(name="심각한 욕 보내면👉 경고 III 타임아옷 1일", value="심각한 욕 보내면 경고 예요!", inline=False)
            embed.set_thumbnail(url="https://yt3.ggpht.com/M5bUy8QEDikBXVzwimxXYHxWRs9UJgl-WUsAjdcuzo0hgoFkJqPwGtss_j9mipemupvHPni17g=s600-c-k-c0x00ffffff-no-rj-rp-mo")
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("**당신은 규칙 명령어 써할 \n`관리 명령 입니다.`\n당신은 관리 명령 사용 할수 없습니다.**")
            await message.channel.send(embed=embed)

    if message.content.startswith("치처 음악골라"):
        r = random.randint(1, 10)
        if r == 1:
            await message.channel.send("1 https://www.youtube.com/watch?v=KTrhCoBC_9E")
        
        if r == 2:
            await message.channel.send("2 https://www.youtube.com/watch?v=3lwTql6YlSE")
        
        if r == 3:
            await message.channel.send("3 https://www.youtube.com/watch?v=2PvVUguRs8M")
        
        if r == 4:
            await message.channel.send("4 https://www.youtube.com/watch?v=DmZm8OjnlvM")

        if r == 5:
            await message.channel.send("5 https://www.youtube.com/watch?v=8_VEfjQpxc0")

        if r == 6: 
            await message.channel.send("6 https://www.youtube.com/watch?v=0upiNhdMaBs")

        if r == 7: 
            await message.channel.send("7 https://www.youtube.com/watch?v=zg-iVxZCBHU")

        if r == 8: 
            await message.channel.send("8 https://www.youtube.com/watch?v=nFeP8cO7xLI")

        if r == 9: 
            await message.channel.send("9 https://www.youtube.com/watch?v=4ZFRyil9T-w")

        if r == 10: 
            await message.channel.send("10 https://www.youtube.com/watch?v=LwNhvbet8pU")
    
    if message.content.startswith ("!청소"):
          user = message.author.id
          if message.author.guild_permissions.administrator:
            if user == 970967370128588820:
              amount = message.content[4:]
              await message.delete()
              await message.channel.purge(limit=int(amount))
    
              embed = discord.Embed(title="메시지 삭제 알림", description="최근 디스코드 채팅 {}개가\n관리자 {}님의 요청으로 인해 정상 삭제 조치 되었습니다".format(amount, message.author), color=0x000000)
              embed.set_footer(text="Bot Made by. 치처 #8915", icon_url="https://discord.com/channels/981478423249698826/1041253382050021426")
              await message.channel.send(embed=embed)
            
          else:
              await message.delete()
              await message.channel.send("{}, 당신은 명령어를 사용할 수 있는 권한이 없습니다".format(message.author.mention))

    if message.content.startswith ("!공지"):
        await message.delete()
        if message.author.guild_permissions.administrator:
            notice = message.content[4:]
            channel = bot.get_channel(1038824258048102410)
            embed = discord.Embed(title="**공지사항 제목 (볼드)*", description="공지사항 내용은 항상 숙지 해주시기 바랍니다\n――――――――――――――――――――――――――――\n\n{}\n\n――――――――――――――――――――――――――――".format(notice),timestamp=datetime.datetime.now(pytz.timezone('UTC')), color=0x00ff00)
            embed.set_footer(text="Bot Made by. 민섭 E #8915 | 담당 관리자 : {}".format(message.author), icon_url="https://yt3.ggpht.com/M5bUy8QEDikBXVzwimxXYHxWRs9UJgl-WUsAjdcuzo0hgoFkJqPwGtss_j9mipemupvHPni17g=s600-c-k-c0x00ffffff-no-rj-rp-mo")
            embed.set_thumbnail(url="https://yt3.ggpht.com/M5bUy8QEDikBXVzwimxXYHxWRs9UJgl-WUsAjdcuzo0hgoFkJqPwGtss_j9mipemupvHPni17g=s600-c-k-c0x00ffffff-no-rj-rp-mo")
            await channel.send ("@everyone", embed=embed)
            await message.author.send("**[ BOT 자동 알림 ]** | 정상적으로 공지가 채널에 작성이 완료되었습니다 : )\n\n[ 기본 작성 설정 채널 ] : {}\n[ 공지 발신자 ] : {}\n\n[ 내용 ]\n{}".format(channel, message.author, notice))
 
        else:
            await message.channel.send("{}, 당신은 관리자가 아닙니다".format(message.author.mention))

        if message.content.startswith("!복권"):
            Text = ""
            number = [1, 2, 3, 4, 5, 6, 7] # 배열크기 선언해줌
            count = 0
            for i in range(0, 7):
                num = random.randrange(1, 46)
                number[i] = num
                if count >= 1:
                    for i2 in range(0, i):
                        if number[i] == number[i2]:  # 만약 현재랜덤값이 이전숫자들과 값이 같다면
                            numberText = number[i]
                            print("작동 이전값 : " + str(numberText))
                            number[i] = random.randrange(1, 46)
                            numberText = number[i]
                            print("작동 현재값 : " + str(numberText))
                            if number[i] == number[i2]:  # 만약 다시 생성한 랜덤값이 이전숫자들과 또 같다면
                                numberText = number[i]
                                print("작동 이전값 : " + str(numberText))
                                number[i] = random.randrange(1, 46)
                                numberText = number[i]
                                print("작동 현재값 : " + str(numberText))
                                if number[i] == number[i2]:  # 만약 다시 생성한 랜덤값이 이전숫자들과 또 같다면
                                    numberText = number[i]
                                    print("작동 이전값 : " + str(numberText))
                                    number[i] = random.randrange(1, 46)
                                    numberText = number[i]
                                    print("작동 현재값 : " + str(numberText))

                count = count + 1
                Text = Text + "  " + str(number[i])

            print(Text.strip())
            embed = discord.Embed(
                title="복권 숫자!",
                description=Text.strip(),
                colour=discord.Color.red()
            )
            await bot.send_message(message.channel, embed=embed)
    
    if message.content.startswith("치처 광산"):
        minerals = ['에메랄드', '다이아몬드', '강화 재료', '루비', '금', '청금석', '철', '석탄', '돌']
        weights = [0.5,1.5,1.7,2,6,10,30,60,65]
        results = random.choices(minerals, weights=weights, k=5)  # 광물 5개를 가중치에 따라 뽑음
        await message.channel.send(', '.join(results) + ' 광물들을 획득하였습니다.')
    
    if message.content.startswith("치처 확률"):
        embed = discord.Embed(color=0x00D8FF)
        embed.add_field(name="돌", value="65", inline=False)
        embed.add_field(name="청금석", value="30", inline=False)
        embed.add_field(name="금", value="10", inline=False)
        embed.add_field(name="루비", value="6", inline=False)
        embed.add_field(name="강화 재료", value="1.7", inline=False)
        embed.add_field(name="다이아몬드", value="1.5", inline=False)
        embed.add_field(name="에메랄드", value="0.5", inline=False)
        await message.channel.send(embed=embed)

    if message.content.startswith('치처 도배모드 ON'):
        time.sleep(1)
        await message.channel.send("3초후에 도배모드 발동!")
        time.sleep(1)
        await message.channel.send("2초후에 도배모드 발동!")
        time.sleep(1)
        await message.channel.send("1초후에 도배모드 발동!")
        time.sleep(1)
        mod = 15
        while mod < 1000:
            embed = discord.Embed(title="삐빅!", description="도배모드 활성화!", color=0x00ff00)
            embed.set_footer(text="끄려면 민섭 E 도배모드 OFF를..")
            await message.channel.send(embed=embed)
            mod = mod + 1

    if message.content.startswith('치처 도배모드 OFF'):
        mod = 1000
        await message.channel.send('삐빅~ 도배 모드 OFF!')

    if message.content.startswith("치처 생존"):
        r = random.randint(1, 5)
        if r == 1:
            await message.channel.send("생존 했다!")
        
        if r == 2:
            await message.channel.send("감염 되다.. 으어어어엉어어")

        if r == 3:
            await message.channel.send("도망 쳐다!")

        if r == 4:
            await message.channel.send("비밀 장소로 이동 했다!")

        if r == 5:
            await message.channel.send("좀비 되다...")


    if message.content.startswith('치처 추방'):
        if message.author.guild_permissions.administrator:
            member = message.guild.get_member(int(message.content.split(" ")[1]))
            await message.guild.kick(member, reason=' '.join(message.content.split(" ")[2:]))

    if message.content.startswith('치처 밴'):
        if message.author.guild_permissions.administrator:
            member = message.guild.get_member(int(message.content.split(" ")[1]))
            await message.guild.ban(member, reason=' '.join(message.content.split(" ")[2:]))

    if message.content.startswith('치처 낚시'):
        embed = discord.Embed(title="낚시중!", description="기다리는중...", color=0x00D8FF)
        embed.add_field(name="몰고기를 잡고 싶다..", value="오늘은 잡을 수 있나?", inline=False)
        embed.add_field(name="오늘은 잡아보자.", value="내가 낚시대 끝에 먹을거 준비!", inline=False)
        await message.channel.send(embed=embed)
        time.sleep(8)
        embed = discord.Embed(title="❗뭔가 있어!!", description="당기자!!!!!!", color=0x00D8FF)
        embed.add_field(name="뭔가 짜릿한 느낌이 난다!", value="들어가자!!", inline=False)
        await message.channel.send(embed=embed)
        time.sleep(12)
        r = random.randint(1, 6)
        if r == 1:
            embed = discord.Embed(title="에잇... 쓰레기", description="바다에 버리면 몰이 오염 될수 있으니깐. 비닐에 버리자.", color=0x1DDB16)
            embed.add_field(name="스레기는 버려야돼!", value="가격 : 4원", inline=False)
            await message.channel.send(embed=embed)

        if r == 2:
            embed = discord.Embed(title="앗! 운이 좋다!!!!!!!!!!!!!!!!!!!!!!! 해왕를 잡았다!!!!", description="오예!!!!!!!!", color=0x1DDB16)
            embed.add_field(name="해왕 잡았다니 대단하다!", value="가격 : 175만원", inline=False)
            await message.channel.send(embed=embed)

        if r == 3:
            embed = discord.Embed(title="에잇... 쓰레기 켄..", description="바다에 버리면 몰이 오염 될수 있으니깐. 비닐에 버리자.", color=0x1DDB16)
            embed.add_field(name="쓰레기 싫어어어어", value="가격 : 2원", inline=False)
            await message.channel.send(embed=embed)

        if r == 4:
            embed = discord.Embed(title="몰고기? 봉어??", description="오 좋은데ㅋ", color=0x1DDB16)
            embed.add_field(name="몰고기가? 봉어간?", value="가격 : 5만원", inline=False)
            await message.channel.send(embed=embed)

        if r == 5:
            embed = discord.Embed(title="기본 몰고기다.", description="기본으로 생겨다.", color=0x1DDB16)
            embed.add_field(name="다른 몰고기도 잡았보자.", value="가격 : 5천원", inline=False)
            await message.channel.send(embed=embed)

        if r == 6:
            embed = discord.Embed(title="대왕 몰고기?!?!?!?!?!?!?", description="너무 큰데? 상어 보다 커!!!!", color=0x1DDB16)
            embed.add_field(name="오예!!!!!", value="가격 : 780억원", inline=False)
            await message.channel.send(embed=embed)


    if message.content.startswith("치처 10초 타이머"):
        time.sleep(10)
        await message.channel.send(f"{message.author.mention}10초 지났어요!!!")

    if message.content.startswith("치처 1분 타이머"):
        time.sleep(60)
        await message.channel.send(f"{message.author.mention}1분 지났어요!!!")

    if message.content.startswith("치처 5분 타이머"):
        time.sleep(300)
        await message.channel.send(f"{message.author.mention}5분 지났어요!!!")

    if message.content.startswith("치처 10분 타이머"):
        time.sleep(600)
        await message.channel.send(f"{message.author.mention}10분 지났어요!!!")

    if message.content.startswith("치처 30분 타이머"):
        time.sleep(1800)
        await message.channel.send(f"{message.author.mention}30분 지났어요!!!")

    if message.content.startswith("치처 1시간 타이머"):
        time.sleep(3600)
        await message.channel.send(f"{message.author.mention}1시간 지났어요!!!")

    if message.content.startswith("치처 2시간 타이머"):
        time.sleep(7200)
        await message.channel.send(f"{message.author.mention}2시간 지났어요!!!")

    if message.content.startswith("치처 3시간 타이머"):
        time.sleep(10800)
        await message.channel.send(f"{message.author.mention}3시간 지났어요!!!")

    if message.content.startswith("치처 4시간 타이머"):
        time.sleep(14400)
        await message.channel.send(f"{message.author.mention}4시간 지났어요!!!")

    if message.content.startswith("치처 5시간 타이머"):
        time.sleep(18000)
        await message.channel.send(f"{message.author.mention}5시간 지났어요!!!")

    if message.content.startswith("치처 10시간 타이머"):
        time.sleep(36000)
        await message.channel.send(f"{message.author.mention}10시간 지났어요!!!")

    if message.content.startswith("치처 24시간 타이머"):
        time.sleep(86400)
        await message.channel.send(f"{message.author.mention}24시간 지났어요!!!")

    if message.content == "!매니저":
        if(message.author.guild_permissions.administrator):
            await message.channel.send("**당신은 매니저 입니다.\n`매니저은 유저 관리를 합니다..!`**")
        else:
            await message.channel.send("**😑 당신은 매니저가 아닙니다!\n`유저는 매니저의 유저 관리 명령어를 사용할수 없어요..\n근데 여기서 봇 개발 한 사람이면 바로 유저 관리 명령어 사용 가능`**")


    if message.content.startswith("치처 강화"):
        minerals = ['강화 성공','강화 실패']
        weights = [25,75]
        results = random.choices(minerals, weights=weights, k=1)  # 광물 1개를 가중치에 따라 뽑음
        await message.channel.send(', '.join(results) + ' 하였습니다.')

    if message.content == "관리자":
        if(message.author.guild_permissions.administrator):
            await message.channel.send("**`관리자 입니다. 당신은 관리 명령 사용 가능 합니다.`**")
        else:
            await message.channel.send("**`당신은 관리자가 아닙니다. 관리 명령 사용 볼가능 합니다.\n근데 여기서 봇 개발 한 사람이면 바로 관리 명령어 사용 가능`**")

    if message.content.startswith("치처 실험실"):
        embed = discord.Embed(title="좀비 바이러스 실험실", color=0x00D8FF)
        embed.add_field(name="연구중....", value="대기중이다. 0%...", inline=False)
        await message.channel.send(embed=embed)
        time.sleep(2)
        embed = discord.Embed(title="좀비 바이러스 실험실", color=0x00D8FF)
        embed.add_field(name="연구중....", value="대기중이다. 5%...", inline=False)
        await message.channel.send(embed=embed)
        time.sleep(3)
        embed = discord.Embed(title="좀비 바이러스 실험실", color=0x00D8FF)
        embed.add_field(name="연구중....", value="대기중이다. 12%...", inline=False)
        await message.channel.send(embed=embed)
        time.sleep(1)
        embed = discord.Embed(title="좀비 바이러스 실험실", color=0x00D8FF)
        embed.add_field(name="연구중....", value="대기중이다. 17%...", inline=False)
        await message.channel.send(embed=embed)
        time.sleep(1)
        embed = discord.Embed(title="좀비 바이러스 실험실", color=0x00D8FF)
        embed.add_field(name="연구중....", value="대기중이다. 36%...", inline=False)
        await message.channel.send(embed=embed)
        time.sleep(1)
        embed = discord.Embed(title="좀비 바이러스 실험실", color=0x00D8FF)
        embed.add_field(name="연구중....", value="대기중이다. 41%...", inline=False)
        await message.channel.send(embed=embed)
        time.sleep(0.5)
        embed = discord.Embed(title="좀비 바이러스 실험실", color=0x00D8FF)
        embed.add_field(name="연구중....", value="대기중이다. 50%...", inline=False)
        await message.channel.send(embed=embed)
        time.sleep(0.5)
        embed = discord.Embed(title="좀비 바이러스 실험실", color=0x00D8FF)
        embed.add_field(name="연구중....", value="대기중이다. 55%...", inline=False)
        await message.channel.send(embed=embed)
        time.sleep(0.5)
        embed = discord.Embed(title="좀비 바이러스 실험실", color=0x00D8FF)
        embed.add_field(name="연구중....", value="대기중이다. 64%...", inline=False)
        await message.channel.send(embed=embed)
        time.sleep(2)
        embed = discord.Embed(title="좀비 바이러스 실험실", color=0x00D8FF)
        embed.add_field(name="연구중....", value="대기중이다. 72%...", inline=False)
        await message.channel.send(embed=embed)
        time.sleep(3)
        embed = discord.Embed(title="좀비 바이러스 실험실", color=0x00D8FF)
        embed.add_field(name="연구중....", value="대기중이다. 81%...", inline=False)
        await message.channel.send(embed=embed)
        time.sleep(2)
        embed = discord.Embed(title="좀비 바이러스 실험실", color=0x00D8FF)
        embed.add_field(name="연구중....", value="대기중이다. 90%...", inline=False)
        await message.channel.send(embed=embed)
        time.sleep(3)
        embed = discord.Embed(title="좀비 바이러스 실험실", color=0x00D8FF)
        embed.add_field(name="연구중....", value="대기중이다. 95%...", inline=False)
        await message.channel.send(embed=embed)
        time.sleep(2)
        embed = discord.Embed(title="좀비 바이러스 실험실", color=0x00D8FF)
        embed.add_field(name="연구중....", value="대기중이다. 100%...", inline=False)
        await message.channel.send(embed=embed)
        r = random.randint(1, 5)
        
        if r == 1:
            embed = discord.Embed(title="좀비 바이러스 펴져다!!!!!!!!!!!!!!", description="!!!!", color=0xFF0000)
            embed.add_field(name="좀비로 변해다.... 좀비 역활 받으수 있습니다.", value="으어어어어어ㅑ어어....", inline=False)
            await message.channel.send(embed=embed)

        if r == 2:
            embed = discord.Embed(title="연구 실행", description="연구 시작!", color=0xFF0000)
            embed.add_field(name="하지만.. 연구 할씨 좀비 바이러스 조심 하려고ㅋ", value="가즈아!!!", inline=False)
            await message.channel.send(embed=embed)

        if r == 3:
            embed = discord.Embed(title="정지", description="정지", color=0xFF0000)
            embed.add_field(name="정지", value="정지", inline=False)
            await message.channel.send(embed=embed)

        if r == 4:
            embed = discord.Embed(title="연구", description="연구소 정보!", color=0xFF0000)
            embed.add_field(name="연구 확인!", value=". ", inline=False)
            embed.set_thumbnail(url="https://image.aladin.co.kr/product/29541/22/cover500/e932530889_1.jpg")
            await message.channel.send(embed=embed)

        if r == 5:
            embed = discord.Embed(title="확인", description="확인 시작", color=0xFF0000)
            embed.add_field(name="확인 중...", value="연구소 정보 확인!", inline=False)
            await message.channel.send(embed=embed)

    if message.content.startswith("치처 핑"):
        embed = discord.Embed(title="퐁!", color=0xFF00DD)
        embed.add_field(name="현재 핑 = {0}초".format(bot.latency), value="풍!!!!")
        await message.channel.send(embed=embed)

    if message.content.startswith("치처 봇 온라인"):
        user = message.author.id
        if user == 970967370128588820:
            await bot.change_presence(status=discord.Status.online)
            await message.channel.send("치처봇이 온라인으로 변경 됩니다.")
        else:
            await message.channel.send("봇 만든 주인만 사용 가능 합니다.")

    if message.content.startswith("치처 봇 방해금지"):
        user = message.author.id
        if user == 970967370128588820:
            await bot.change_presence(status=discord.Status.dnd)
            await message.channel.send("치처봇이 방해금지으로 변경 됩니다.")
        else:
            await message.channel.send("봇 만든 주인만 사용 가능 합니다.")

    if message.content.startswith("치처 봇 자리비옴"):
        user = message.author.id
        if user == 970967370128588820:
            await bot.change_presence(status=discord.Status.idle)
            await message.channel.send("치처봇이 자리비옴으로 변경 됩니다.")
        else:
            await message.channel.send("봇 만든 주인만 사용 가능 합니다.")

    if message.content.startswith("치처 봇 오프라인"):
        user = message.author.id
        if user == 970967370128588820:
            await bot.change_presence(status=discord.Status.offline)
            await message.channel.send("치처봇이 오프라인으로 변경 됩니다.")
        else:
            await message.channel.send("봇 만든 주인만 사용 가능 합니다.")

    if message.content.startswith("어쩔티비"):
        await message.channel.send("안몰티비")

    if message.content.startswith("뇌쩔티비"):
        await message.channel.send("어쩔 42인치티비")

    if message.content.startswith("저쩔 세탁기"):
        await message.channel.send("어쩔 초고속블렌딩 믹서기")

    if message.content.startswith("저쩔 스타일러"):
        await message.channel.send("어쩔 아이폰13Promax시에라블루")

    if message.content.startswith("저쩔 갤럭시Z플립3 비스포크 에디션"):
            await message.channel.send("어쩔 냉장고")


    if message.content.startswith("저쩔 다이슨 V15청소기"):
            await message.channel.send("어쩔 삼성 QLED 4K 스위블벽걸리형 티비...!")


    if message.content.startswith("저쩔 프리미엄 건조기 사면 같이 오는 면도기!"):
            await message.channel.send("어쩔...! 어쩔ㅈ..어쩔!..")


    if message.content.startswith("아무말 못하죠ㅋㅋ"):
            await message.channel.send("도와줘요! 2000L 상냉장하냉동 4도어 냉장고!")


    if message.content.startswith("어쩔 안궁티비"):
            await message.channel.send("어쩔 컴퓨터")


    if message.content.startswith("저쩔 생일"):
            await message.channel.send("어쩔티비")

    if message.content.startswith('글리치'):
        embed = discord.Embed(title="글리치 1%")
        embed.add_field(name="잠시 기다리세여.", value="잠시 기다림")
        await message.channel.send(embed=embed)
        time.sleep(2)
        embed = discord.Embed(title="글리치 4%")
        embed.add_field(name="잠시 기다리세여.", value="잠시 기다림")
        await message.channel.send(embed=embed)
        time.sleep(2)
        embed = discord.Embed(title="글리치 42%")
        embed.add_field(name="잠시 기다리세여.", value="잠시 기다림")
        await message.channel.send(embed=embed)
        time.sleep(2)
        embed = discord.Embed(title="글리치 55%")
        embed.add_field(name="잠시 기다리세여.", value="잠시 기다림")
        await message.channel.send(embed=embed)
        time.sleep(2)
        embed = discord.Embed(title="글리치 56%")
        embed.add_field(name="잠시 기다리세여.", value="잠시 기다림")
        await message.channel.send(embed=embed)
        time.sleep(2)
        embed = discord.Embed(title="글리치 77%")
        embed.add_field(name="잠시 기다리세여.", value="잠시 기다림")
        await message.channel.send(embed=embed)
        time.sleep(2)
        embed = discord.Embed(title="글리치 88%")
        embed.add_field(name="잠시 기다리세여.", value="잠시 기다림")
        await message.channel.send(embed=embed)
        time.sleep(2)
        embed = discord.Embed(title="글리치 99%")
        embed.add_field(name="잠시 기다리세여.", value="잠시 기다림")
        await message.channel.send(embed=embed)
        time.sleep(2)
        embed = discord.Embed(title="글리치 100%")
        embed.add_field(name="잠시 기다리세여.", value="잠시 기다림")
        await message.channel.send(embed=embed)
        r = random.randint(1, 5)
        
        if r == 1:
            embed = discord.Embed(title="글리치가 돼벌려다..", description="!!!", color=0xFF0000)
            embed.add_field(name="글리치로 변해다.... 글리치 역활 받으수 있습니다.", value="내 글리치 ERROR 좀 봐줘래?", inline=False)
            await message.channel.send(embed=embed)

        if r == 2:
            embed = discord.Embed(title="연구 실행", description="연구 시작!", color=0xFF0000)
            embed.add_field(name="하지만.. 연구 할씨 글리치 바이러스 조심 하려고ㅋ", value="가즈아!!!", inline=False)
            await message.channel.send(embed=embed)

        if r == 3:
            embed = discord.Embed(title="정지상태!", description="글리치가 오류 있습니다.", color=0xFF0000)
            embed.add_field(name="정지", value="정지", inline=False)
            await message.channel.send(embed=embed)

        if r == 4:
            embed = discord.Embed(title="연구", description="연구소 정보!", color=0xFF0000)
            embed.add_field(name="연구 확인!", value=". ", inline=False)
            embed.set_thumbnail(url="https://image.aladin.co.kr/product/29541/22/cover500/e932530889_1.jpg")
            await message.channel.send(embed=embed)

        if r == 5:
            embed = discord.Embed(title="확인", description="확인 시작", color=0xFF0000)
            embed.add_field(name="확인 중...", value="연구소 정보 확인!", inline=False)
            await message.channel.send(embed=embed)

        if message.author == bot.user:
            return
        if message.content == "!reset":
            await bot.process_commands(message)
            return
        else:
            userExistance, userRow = checkUser(message.author.name, message.author.id)
            channel = message.channel
            if userExistance:
                levelUp, lvl = levelupCheck(userRow)
                if levelUp:
                    print(message.author, "가 레벨업 했습니다")
                    print("")
                    embed = discord.Embed(title = "레벨업", description = None, color = 0x00A260)
                    embed.set_footer(text = message.author.name + "이 " + str(lvl) + "레벨 달성!")
                    await channel.send(embed=embed)
                else:
                    modifyExp(userRow, 1)
                    print("------------------------------\n")

    await bot.process_commands(message)

@bot.command(name="주사위2")
async def dice(ctx):
    randnum = random.randint(1, 6)  # 1이상 6이하 랜덤 숫자를 뽑음
    await ctx.send(f'주사위 결과는 {randnum} 입니다.')

@bot.command(name="가위바위보")
async def game(ctx, user: str):  # user:str로 !game 다음에 나오는 메시지를 받아줌
    rps_table = ['가위', '바위', '보']
    bot = random.choice(rps_table)
    result = rps_table.index(user) - rps_table.index(bot)  # 인덱스 비교로 결과 결정
    if result == 0:
        await ctx.send(f'{user} vs {bot}  비겼습니다.')
    elif result == 1 or result == -2:
        await ctx.send(f'{user} vs {bot}  유저가 이겼습니다.')
    else:
        await ctx.send(f'{user} vs {bot}  봇이 이겼습니다.')

@bot.command()
async def 광산2(ctx):
    minerals = ['레드 다이아몬드', '다이아몬드', '금', '은', '철', '석탄']
    weights = [0.5, 3, 6, 15, 25, 1]
    results = random.choices(minerals, weights=weights, k=10)  # 광물 10개를 가중치에 따라 뽑음
    await ctx.send(', '.join(results) + ' 광물들을 획득하였습니다.')

@bot.command()
async def 반갑다(ctx):
    await ctx.send("안녕!")

@bot.command()
async def 검색(ctx,search=None):
        if search==None:
            searchem = discord.Embed(title='그래서 뭘 검색 하라고요? `?!검색 (원하는 컨탠츠)`',description='띄어쓰기 하면 한 문장만 검색 되요!',color=0xFF0F13)
            return await ctx.send(embed = searchem)
        embed = discord.Embed(title='**검색 결과**')
        embed.add_field(name='네이버', value=f'[바로가기](https://m.search.naver.com/search.naver?sm=mtp_hty.top&where=m&query={search})')
        embed.add_field(name='유튜브',value=f'[바로가기](https://m.youtube.com/results?sp=mAEA&search_query={search})')
        embed.add_field(name='구글',value=f'[바로가기](https://www.google.com/search?q={search})')
        await ctx.send(embed=embed)


@bot.command()
async def 메뉴(ctx):
    select = Select(
        placeholder = "메뉴 선택 하기",
        options = [
        discord.SelectOption(label="프로필", description="자신 프로필를 알려 줘요!"),
        discord.SelectOption(label="광산", description="광산 게임 해요!"),
        discord.SelectOption(label="도옴말", description="도옴말 알려 줘요!")
    ])

    async def my_callback(interaction):
        if select.values[0] == "프로필":
            await interaction.response.send_message("프로필!!")
            date = datetime.datetime.utcfromtimestamp(((int(ctx.author.id) >> 22) + 1420070400000) / 1000)
            embed = discord.Embed(color=0x00D8FF)
            embed.add_field(name="닉네임 : ", value=ctx.author, inline=False)
            embed.add_field(name="서버닉네임 : ", value=ctx.author.display_name, inline=False)
            embed.add_field(name="가입일 : ", value=str(date.year) + "년" + str(date.month) + "월" + str(date.day) + "일", inline=False)
            embed.add_field(name="아이디 : ", value=ctx.author.id, inline=False)
            await ctx.channel.send(embed=embed)
        elif select.values[0] == "광산":
            await interaction.response.send_message("광산!!")
            minerals = ['레드 다이아몬드', '다이아몬드', '금', '은', '철', '석탄']
            weights = [0.5, 3, 6, 15, 25, 1]
            results = random.choices(minerals, weights=weights, k=10)  # 광물 10개를 가중치에 따라 뽑음
            await ctx.send(', '.join(results) + ' 광물들을 획득하였습니다.')
        elif select.values[0] == "도옴말":
            await interaction.response.send_message("도옴말!!")
            embed = discord.Embed(title="도옴말")
            embed.add_field(name="치처 야", value="기본말 입니다.")
            embed.add_field(name="치처 다른거 은?", value="안돼안돼")
            embed.add_field(name="치처 봇 여기로 초대함?", value="알려 줘요!")
            embed.add_field(name="치처 게임", value="게임 할 수 없다")
            embed.add_field(name="치처 넌 바보니?", value="ㅋ.")
            embed.add_field(name="치처 프로필", value="내정보 알려줘요!")
            embed.add_field(name="치처 바보임?", value="ㅋㅋ.")
            embed.add_field(name="!퀴즈 , !패스 , 정답", value="퀴즈 내요")
            embed.add_field(name="치처 음악골라", value="유튜브 음악를 알려줘요!")
            embed.add_field(name="!청소", value="관리자만 사용 가능 합니다.")
            embed.add_field(name="!공지", value="관리자만 사용 가능 합니다.")
            embed.add_field(name="!복권", value="복권 확인!")
            embed.add_field(name="치처 광산", value="광산 합니다!")
            embed.add_field(name="치처 확률", value="광산의 확률를 보여 줘요!")
            embed.add_field(name="치처 도배모드 ON", value="도배 모드 활성화 됩니다!")
            embed.add_field(name="치처 도배모드 OFF", value="도배 모드가 비활성화 됩니다!")
            embed.add_field(name="치처 생존", value="생존 좀비 게임 할수 있다")
            embed.add_field(name="치처 현재 시간", value="시각!")
            embed.add_field(name="치처 강화", value="강화 합니다!")
            embed.add_field(name="!가위바위보 보 , 가위 , 바위", value="강화 합니다!")
            embed.add_field(name="!주사위2", value="주사위 2레벨 진화된 주사위 보여줘요!") 
            embed.add_field(name="!주사위", value = "주사위를 굴려 봇과 대결합니다")
            embed.add_field(name="!회원가입", value = "각종 컨텐츠를 즐기기 위한 회원가입을 합니다")
            embed.add_field(name="!내정보", value = "자신의 정보를 확인합니다")
            embed.add_field(name="!정보 [대상]", value = "멘션한 [대상]의 정보를 확인합니다")
            embed.add_field(name="!송금 [대상] [돈]", value = "멘션한 [대상]에게 [돈]을 보냅니다")
            embed.add_field(name="!도박 [돈]", value = "[돈]을 걸어 도박을 합니다. 올인도 가능합니다")
  
            await ctx.channel.send(embed=embed)
            
    select.callback = my_callback
    view = View()
    view.add_item(select)

    await ctx.send("메뉴 선택 해주세요!", view = view)

@bot.command()
async def 들어와(ctx):
    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("채널에 유저가 접속해있지 않네요..")

@bot.command()
async def 나가(ctx):
    try:
        await vc.disconnect()
    except:
        await ctx.send("이미 그 채널에 속해있지 않아요.")

@bot.command(name="URL재생하기")
async def URL재생(ctx, *, url):

    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("채널에 유저가 접속해있지 않네요..")

    YDL_OPTIONS = {'format': 'bestaudio','noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if not vc.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        await subtitle_song(ctx, url)
    else:
        await ctx.send("노래가 이미 재생되고 있습니다!")

@bot.command()
async def 재생(ctx, *, msg):

    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("채널에 유저가 접속해있지 않네요..")

    if not vc.is_playing():
        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        global entireText
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            
        chromedriver_dir = r"D:\Discord_Bot\chromedriver.exe"
        driver = webdriver.Chrome(chromedriver_dir, options = options)
        driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a', {'id': 'video-title'})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get('href')
        url = 'https://www.youtube.com'+musicurl 

        driver.quit()

        musicnow.insert(0, entireText)
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        await ctx.send(embed = discord.Embed(title= "노래 재생", description = "현재 " + musicnow[0] + "을(를) 재생하고 있습니다.", color = 0x00ff00))
        await subtitle_song(ctx, url)
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
    else:
        await ctx.send("이미 노래가 재생 중이라 노래를 재생할 수 없어요!")

@bot.command()
async def 일시정지(ctx):
    if vc.is_playing():
        vc.pause()
        await ctx.send(embed = discord.Embed(title= "일시정지", description = musicnow[0] + "을(를) 일시정지 했습니다.", color=0x00ff00))
    else:
        await ctx.send("지금 노래가 재생되지 않네요.")

@bot.command()
async def 다시재생(ctx):
    try:
        vc.resume()
    except:
         await ctx.send("지금 노래가 재생되지 않네요.")
    else:
         await ctx.send(embed = discord.Embed(title= "다시재생", description = musicnow[0]  + "을(를) 다시 재생했습니다.", color = 0x00ff00))

@bot.command()
async def 노래끄기(ctx):
    if vc.is_playing():
        vc.stop()
        await ctx.send(embed = discord.Embed(title= "노래끄기", description = musicnow[0]  + "을(를) 종료했습니다.", color = 0x00ff00))
    else:
        await ctx.send("지금 노래가 재생되지 않네요.")

@bot.command()
async def 지금노래(ctx):
    if not vc.is_playing():
        await ctx.send("지금은 노래가 재생되지 않네요..")
    else:
        await ctx.send(embed = discord.Embed(title = "지금노래", description = "현재 " + musicnow[0] + "을(를) 재생하고 있습니다.", color = 0x00ff00))

@bot.command()
async def 대기열추가(ctx, *, msg):
    user.append(msg)
    result, URLTEST = title(msg)
    song_queue.append(URLTEST)
    await ctx.send(result + "를 재생목록에 추가했어요!")

@bot.command()
async def 대기열삭제(ctx, *, number):
    try:
        ex = len(musicnow) - len(user)
        del user[int(number) - 1]
        del musictitle[int(number) - 1]
        del song_queue[int(number)-1]
        del musicnow[int(number)-1+ex]
            
        await ctx.send("대기열이 정상적으로 삭제되었습니다.")
    except:
        if len(list) == 0:
            await ctx.send("대기열에 노래가 없어 삭제할 수 없어요!")
        else:
            if len(list) < int(number):
                await ctx.send("숫자의 범위가 목록개수를 벗어났습니다!")
            else:
                await ctx.send("숫자를 입력해주세요!")

@bot.command()
async def 목록(ctx):
    if len(musictitle) == 0:
        await ctx.send("아직 아무노래도 등록하지 않았어요.")
    else:
        global Text
        Text = ""
        for i in range(len(musictitle)):
            Text = Text + "\n" + str(i + 1) + ". " + str(musictitle[i])
            
        await ctx.send(embed = discord.Embed(title= "노래목록", description = Text.strip(), color = 0x00ff00))

@bot.command()
async def 목록초기화(ctx):
    try:
        ex = len(musicnow) - len(user)
        del user[:]
        del musictitle[:]
        del song_queue[:]
        while True:
            try:
                del musicnow[ex]
            except:
                break
        await ctx.send(embed = discord.Embed(title= "목록초기화", description = """목록이 정상적으로 초기화되었습니다. 이제 노래를 등록해볼까요?""", color = 0x00ff00))
    except:
        await ctx.send("아직 아무노래도 등록하지 않았어요.")

@bot.command()
async def 목록재생(ctx):

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    
    if len(user) == 0:
        await ctx.send("아직 아무노래도 등록하지 않았어요.")
    else:
        if len(musicnow) - len(user) >= 1:
            for i in range(len(musicnow) - len(user)):
                del musicnow[0]
        if not vc.is_playing():
            play(ctx)
        else:
            await ctx.send("노래가 이미 재생되고 있어요!")

@bot.command()
async def 즐겨찾기(ctx):
    global Ftext
    Ftext = ""
    correct = 0
    global Flist
    for i in range(len(userF)):
        if userF[i] == str(ctx.message.author.name): #userF에 유저정보가 있는지 확인
            correct = 1 #있으면 넘김
    if correct == 0:
        userF.append(str(ctx.message.author.name)) #userF에다가 유저정보를 저장
        userFlist.append([]) #유저 노래 정보 첫번째에 유저이름을 저장하는 리스트를 만듬.
        userFlist[len(userFlist)-1].append(str(ctx.message.author.name))
        
    for i in range(len(userFlist)):
        if userFlist[i][0] == str(ctx.message.author.name):
            if len(userFlist[i]) >= 2: # 노래가 있다면
                for j in range(1, len(userFlist[i])):
                    Ftext = Ftext + "\n" + str(j) + ". " + str(userFlist[i][j])
                titlename = str(ctx.message.author.name) + "님의 즐겨찾기"
                embed = discord.Embed(title = titlename, description = Ftext.strip(), color = 0x00ff00)
                embed.add_field(name = "목록에 추가\U0001F4E5", value = "즐겨찾기에 모든 곡들을 목록에 추가합니다.", inline = False)
                embed.add_field(name = "플레이리스트로 추가\U0001F4DD", value = "즐겨찾기에 모든 곡들을 새로운 플레이리스트로 저장합니다.", inline = False)
                Flist = await ctx.send(embed = embed)
                await Flist.add_reaction("\U0001F4E5")
                await Flist.add_reaction("\U0001F4DD")
            else:
                await ctx.send("아직 등록하신 즐겨찾기가 없어요.")



@bot.command()
async def 즐겨찾기추가(ctx, *, msg):
    correct = 0
    for i in range(len(userF)):
        if userF[i] == str(ctx.message.author.name): #userF에 유저정보가 있는지 확인
            correct = 1 #있으면 넘김
    if correct == 0:
        userF.append(str(ctx.message.author.name)) #userF에다가 유저정보를 저장
        userFlist.append([]) #유저 노래 정보 첫번째에 유저이름을 저장하는 리스트를 만듦.
        userFlist[len(userFlist)-1].append(str(ctx.message.author.name))

    for i in range(len(userFlist)):
        if userFlist[i][0] == str(ctx.message.author.name):
            
            options = webdriver.ChromeOptions()
            options.add_argument("headless")

            chromedriver_dir = r"D:\Discord_Bot\chromedriver.exe"
            driver = webdriver.Chrome(chromedriver_dir, options = options)
            driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
            source = driver.page_source
            bs = bs4.BeautifulSoup(source, 'lxml')
            entire = bs.find_all('a', {'id': 'video-title'})
            entireNum = entire[0]
            music = entireNum.text.strip()

            driver.quit()

            userFlist[i].append(music)
            await ctx.send(music + "(이)가 정상적으로 등록되었어요!")



@bot.command()
async def 즐겨찾기삭제(ctx, *, number):
    correct = 0
    for i in range(len(userF)):
        if userF[i] == str(ctx.message.author.name): #userF에 유저정보가 있는지 확인
            correct = 1 #있으면 넘김
    if correct == 0:
        userF.append(str(ctx.message.author.name)) #userF에다가 유저정보를 저장
        userFlist.append([]) #유저 노래 정보 첫번째에 유저이름을 저장하는 리스트를 만듦.
        userFlist[len(userFlist)-1].append(str(ctx.message.author.name))

    for i in range(len(userFlist)):
        if userFlist[i][0] == str(ctx.message.author.name):
            if len(userFlist[i]) >= 2: # 노래가 있다면
                try:
                    del userFlist[i][int(number)]
                    await ctx.send("정상적으로 삭제되었습니다.")
                except:
                     await ctx.send("입력한 숫자가 잘못되었거나 즐겨찾기의 범위를 초과하였습니다.")
            else:
                await ctx.send("즐겨찾기에 노래가 없어서 지울 수 없어요!")

@bot.event
async def on_reaction_add(reaction, users, ctx):
    if users.bot == 1:
        pass
    else:
        try:
            await Flist.delete()
        except:
            pass
        else:
            if str(reaction.emoji) == '\U0001F4E5':
                await reaction.message.channel.send("잠시만 기다려주세요. (즐겨찾기 갯수가 많으면 지연될 수 있습니다.)")
                print(users.name)
                for i in range(len(userFlist)):
                    if userFlist[i][0] == str(users.name):
                        for j in range(1, len(userFlist[i])):
                            try:
                                driver.close()
                            except:
                                print("NOT CLOSED")

                            user.append(userFlist[i][j])
                            result, URLTEST = title(userFlist[i][j])
                            song_queue.append(URLTEST)
                            await reaction.message.channel.send(userFlist[i][j] + "를 재생목록에 추가했어요!")
            elif str(reaction.emoji) == '\U0001F4DD':
                await reaction.message.channel.send("플레이리스트가 나오면 생길 기능이랍니다. 추후에 올릴 영상을 기다려주세요!")

@bot.command()
async def 반복재생(ctx, *, msg):
      
    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()   
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            pass
    
    global entireText
    global number
    number = 1
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    
    if len(musicnow) - len(user) >= 1:
        for i in range(len(musicnow) - len(user)):
            del musicnow[0]
            
    driver = load_chrome_driver()
    driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, 'lxml')
    entire = bs.find_all('a', {'id': 'video-title'})
    entireNum = entire[0]
    entireText = entireNum.text.strip()
    musicnow.insert(0, entireText)
    test1 = entireNum.get('href')
    url = 'https://www.youtube.com'+test1
    await ctx.send(embed = discord.Embed(title= "반복재생", description = "현재 " + musicnow[0] + "을(를) 반복재생하고 있습니다.", color = 0x00ff00))
    again(ctx, url)

@bot.command()
async def 도움말(ctx):
            embed = discord.Embed(title="도옴말", description="접두사 : 치처아  , 제작한 사람 : bms#8915", color=0x0054FF)
            embed.add_field(name="치처 야", value="기본말 입니다.")
            embed.add_field(name="치처 다른거 은?", value="안돼안돼")
            embed.add_field(name="치처 봇 여기로 초대함?", value="알려 줘요!")
            embed.add_field(name="치처 게임", value="게임 할 수 없다")
            embed.add_field(name="치처 넌 바보니?", value="ㅋ.")
            embed.add_field(name="치처 프로필", value="내정보 알려줘요!")
            embed.add_field(name="치처 바보임?", value="ㅋㅋ.")
            embed.add_field(name="!퀴즈 , !패스 , 정답", value="퀴즈 내요")
            embed.add_field(name="치처 음악골라", value="유튜브 음악를 알려줘요!")
            embed.add_field(name="!청소", value="관리자만 사용 가능 합니다.")
            embed.add_field(name="!공지", value="관리자만 사용 가능 합니다.")
            embed.add_field(name="!복권", value="복권 확인!")
            embed.add_field(name="치처 광산", value="광산 합니다!")
            embed.add_field(name="치처 확률", value="광산의 확률를 보여 줘요!")
            embed.add_field(name="치처 도배모드 ON", value="도배 모드 활성화 됩니다!")
            embed.add_field(name="치처 도배모드 OFF", value="도배 모드가 비활성화 됩니다!")
            embed.add_field(name="치처 생존", value="생존 좀비 게임 할수 있다")
            embed.add_field(name="치처 현재 시간", value="시각!")
            embed.add_field(name="치처 강화", value="강화 합니다!")
            embed.add_field(name="!가위바위보 보 , 가위 , 바위", value="강화 합니다!")
            embed.add_field(name="!주사위2", value="주사위 2레벨 진화된 주사위 보여줘요!") 
            embed.add_field(name="!주사위", value = "주사위를 굴려 봇과 대결합니다")
            embed.add_field(name="!회원가입", value = "각종 컨텐츠를 즐기기 위한 회원가입을 합니다")
            embed.add_field(name="!내정보", value = "자신의 정보를 확인합니다")
            embed.add_field(name="!정보 [대상]", value = "멘션한 [대상]의 정보를 확인합니다")
            embed.add_field(name="!송금 [대상] [돈]", value = "멘션한 [대상]에게 [돈]을 보냅니다")
            embed.add_field(name="!도박 [돈]", value = "[돈]을 걸어 도박을 합니다. 올인도 가능합니다")
            await ctx.send(embed=embed)
  
@bot.command()
async def 주사위(ctx):
    result, _color, bot1, bot2, user1, user2, a, b = dice()

    embed = discord.Embed(title = "주사위 게임 결과", description = None, color = _color)
    embed.add_field(name = "치처 봇의 숫자 " + bot1 + "+" + bot2, value = ":game_die: " + a, inline = False)
    embed.add_field(name = ctx.author.name+"의 숫자 " + user1 + "+" + user2, value = ":game_die: " + b, inline = False)
    embed.set_footer(text="결과: " + result)
    await ctx.send(embed=embed)

@bot.command()
async def 도박(ctx, money):
    userExistance, userRow = checkUser(ctx.author.name, ctx.author.id)
    win = gamble()
    result = ""
    betting = 0
    _color = 0x000000
    if userExistance:
        print("DB에서 ", ctx.author.name, "을 찾았습니다.")
        cur_money = getMoney(ctx.author.name, userRow)

        if money == "올인":
            betting = cur_money
            if win:
                result = "성공"
                _color = 0x00ff56
                print(result)

                modifyMoney(ctx.author.name, userRow, int(0.5*betting))

            else:
                result = "실패"
                _color = 0xFF0000
                print(result)

                modifyMoney(ctx.author.name, userRow, -int(betting))
                addLoss(ctx.author.name, userRow, int(betting))

            embed = discord.Embed(title = "도박 결과", description = result, color = _color)
            embed.add_field(name = "배팅금액", value = betting, inline = False)
            embed.add_field(name = "현재 자산", value = getMoney(ctx.author.name, userRow), inline = False)

            await ctx.send(embed=embed)
            
        elif int(money) >= 10:
            if cur_money >= int(money):
                betting = int(money)
                print("배팅금액: ", betting)
                print("")

                if win:
                    result = "성공"
                    _color = 0x00ff56
                    print(result)

                    modifyMoney(ctx.author.name, userRow, int(0.5*betting))

                else:
                    result = "실패"
                    _color = 0xFF0000
                    print(result)

                    modifyMoney(ctx.author.name, userRow, -int(betting))
                    addLoss(ctx.author.name, userRow, int(betting))

                embed = discord.Embed(title = "도박 결과", description = result, color = _color)
                embed.add_field(name = "배팅금액", value = betting, inline = False)
                embed.add_field(name = "현재 자산", value = getMoney(ctx.author.name, userRow), inline = False)

                await ctx.send(embed=embed)

            else:
                print("돈이 부족합니다.")
                print("배팅금액: ", money, " | 현재자산: ", cur_money)
                await ctx.send("돈이 부족합니다. 현재자산: " + str(cur_money))
        else:
            print("배팅금액", money, "가 10보다 작습니다.")
            await ctx.send("10원 이상만 배팅 가능합니다.")
    else:
        print("DB에서 ", ctx.author.name, "을 찾을 수 없습니다")
        await ctx.send("도박은 회원가입 후 이용 가능합니다.")

    print("------------------------------\n")

@bot.command()
async def 랭킹(ctx):
    rank = ranking()
    embed = discord.Embed(title = "레벨 랭킹", description = None, color = 0x4A44FF)

    for i in range(0,len(rank)):
        if i%2 == 0:
            name = rank[i]
            lvl = rank[i+1]
            embed.add_field(name = str(int(i/2+1))+"위 "+name, value ="레벨: "+str(lvl), inline=False)

    await ctx.send(embed=embed) 

@bot.command()
async def 회원가입(ctx):
    print("회원가입이 가능한지 확인합니다.")
    userExistance, userRow = checkUser(ctx.author.name, ctx.author.id)
    if userExistance:
        print("DB에서 ", ctx.author.name, "을 찾았습니다.")
        print("------------------------------\n")
        await ctx.send("이미 가입하셨습니다.")
    else:
        print("DB에서 ", ctx.author.name, "을 찾을 수 없습니다")
        print("")

        Signup(ctx.author.name, ctx.author.id)

        print("회원가입이 완료되었습니다.")
        print("------------------------------\n")
        await ctx.send("회원가입이 완료되었습니다.")

@bot.command()
async def 탈퇴(ctx):
    print("탈퇴가 가능한지 확인합니다.")
    userExistance, userRow = checkUser(ctx.author.name, ctx.author.id)
    if userExistance:
        DeleteAccount(userRow)
        print("탈퇴가 완료되었습니다.")
        print("------------------------------\n")

        await ctx.send("탈퇴가 완료되었습니다.")
    else:
        print("DB에서 ", ctx.author.name, "을 찾을 수 없습니다")
        print("------------------------------\n")

        await ctx.send("등록되지 않은 사용자입니다.")

@bot.command()
async def 내정보(ctx):
    userExistance, userRow = checkUser(ctx.author.name, ctx.author.id)

    if not userExistance:
        print("DB에서 ", ctx.author.name, "을 찾을 수 없습니다")
        print("------------------------------\n")
        await ctx.send("회원가입 후 자신의 정보를 확인할 수 있습니다.")
    else:
        level, exp, money, loss = userInfo(userRow)
        rank = getRank(userRow)
        userNum = checkUserNum()
        expToUP = level*level + 6*level
        boxes = int(exp/expToUP*20)
        print("------------------------------\n")
        embed = discord.Embed(title="유저 정보", description = ctx.author.name, color = 0x62D0F6)
        embed.add_field(name = "레벨", value = level)
        embed.add_field(name = "순위", value = str(rank) + "/" + str(userNum))
        embed.add_field(name = "XP: " + str(exp) + "/" + str(expToUP), value = boxes * ":blue_square:" + (20-boxes) * ":white_large_square:", inline = False)
        embed.add_field(name = "보유 자산", value = money, inline = False)
        embed.add_field(name = "도박으로 날린 돈", value = loss, inline = False)

        await ctx.send(embed=embed)

@bot.command()
async def 정보(ctx, user: discord.User):
    userExistance, userRow = checkUser(user.name, user.id)

    if not userExistance:
        print("DB에서 ", user.name, "을 찾을 수 없습니다")
        print("------------------------------\n")
        await ctx.send(user.name  + " 은(는) 등록되지 않은 사용자입니다.")
    else:
        level, exp, money, loss = userInfo(userRow)
        rank = getRank(userRow)
        userNum = checkUserNum()
        print("------------------------------\n")
        embed = discord.Embed(title="유저 정보", description = user.name, color = 0x62D0F6)
        embed.add_field(name = "레벨", value = level)
        embed.add_field(name = "경험치", value = str(exp) + "/" + str(level*level + 6*level))
        embed.add_field(name = "순위", value = str(rank) + "/" + str(userNum))
        embed.add_field(name = "보유 자산", value = money, inline = False)
        embed.add_field(name = "도박으로 날린 돈", value = loss, inline = False)

        await ctx.send(embed=embed)

@bot.command()
async def 송금(ctx, user: discord.User, money):
    print("송금이 가능한지 확인합니다.")
    senderExistance, senderRow = checkUser(ctx.author.name, ctx.author.id)
    receiverExistance, receiverRow = checkUser(user.name, user.id)

    if not senderExistance:
        print("DB에서", ctx.author.name, "을 찾을수 없습니다")
        print("------------------------------\n")
        await ctx.send("회원가입 후 송금이 가능합니다.")
    elif not receiverExistance:
        print("DB에서 ", user.name, "을 찾을 수 없습니다")
        print("------------------------------\n")
        await ctx.send(user.name  + " 은(는) 등록되지 않은 사용자입니다.")
    else:
        print("송금하려는 돈: ", money)

        s_money = getMoney(ctx.author.name, senderRow)
        r_money = getMoney(user.name, receiverRow)

        if s_money >= int(money) and int(money) != 0:
            print("돈이 충분하므로 송금을 진행합니다.")
            print("")

            remit(ctx.author.name, senderRow, user.name, receiverRow, money)

            print("송금이 완료되었습니다. 결과를 전송합니다.")

            embed = discord.Embed(title="송금 완료", description = "송금된 돈: " + money, color = 0x77ff00)
            embed.add_field(name = "보낸 사람: " + ctx.author.name, value = "현재 자산: " + str(getMoney(ctx.author.name, senderRow)))
            embed.add_field(name = "→", value = ":moneybag:")
            embed.add_field(name="받은 사람: " + user.name, value="현재 자산: " + str(getMoney(user.name, receiverRow)))
                    
            await ctx.send(embed=embed)
        elif int(money) == 0:
            await ctx.send("0원을 보낼 필요는 없죠")
        else:
            print("돈이 충분하지 않습니다.")
            print("송금하려는 돈: ", money)
            print("현재 자산: ", s_money)
            await ctx.send("돈이 충분하지 않습니다. 현재 자산: " + str(s_money))

        print("------------------------------\n")


@bot.command()
async def reset(ctx):
    resetData()

@bot.command()
async def add(ctx, money):
    user, row = checkUser(ctx.author.name, ctx.author.id)
    addMoney(row, int(money))
    print("money")

@bot.command()
async def exp(ctx, exp):
    user, row = checkUser(ctx.author.name, ctx.author.id)
    addExp(row, int(exp))
    print("exp")

@bot.command()
async def lvl(ctx, lvl):
    user, row = checkUser(ctx.author.name, ctx.author.id)
    adjustlvl(row, int(lvl))
    print("lvl")

@bot.command(name = "출석")
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(ctx):
    await ctx.send(f"{ctx.author.mention}님, 오늘 출석체크를 완료했습니다")


@bot.tree.command(name="도움말", description="슬래시 커맨드 도움말 알려 줘요!")
async def 도움말(interaction: discord.Interaction):
  embed = discord.Embed(title="도움말", description="모든 슬래시 커맨드 만들어 졌습니다.", color=0x4000FF) #큰 제목과 작은 제목을 보여준다
  embed.add_field(name="일반 명령어", value="프로필\n 문의", inline=False) #작은 제목과 작은제목의 설명
  embed.add_field(name="관리 명령어", value="개발중..", inline=False) #작은 제목과 작은제목의 설명
  embed.add_field(name="고급 명령어", value="개발중..", inline=False) #작은 제목과 작은제목의 설명
  await interaction.response.send_message(embed=embed)

@bot.tree.command(name="프로필", description="내정보을 보여줘요! 2단계로 진화!")
async def 프로필(interaction: discord.Interaction, member:discord.Member=None):
  if member == None:
    member = interaction.user
  roles = [role for role in member.roles]
  embed = discord.Embed(title="프로필!", description="내정보를 알려드릴겠습니다!", color=0x00D8FF)
  embed.add_field(name="이름 : ", value=f"{member.name}#{member.discriminator}", inline=False)
  embed.add_field(name="내 id : ", value=member.id, inline=False)
  embed.add_field(name="서버닉네임 : ", value=member.display_name, inline=False)
  embed.add_field(name="상태 : ", value=member.status, inline=False)
  embed.add_field(name="만든 날짜 : ", value=member.created_at.strftime("%a, %B, %d, %Y, %I:%M %p"), inline=False)
  embed.add_field(name="서버 접속 날짜 : ", value=member.joined_at.strftime("%a, %B, %d, %Y, %I:%M %p"), inline=False)
  embed.add_field(name="봇 맞습니까? : ", value=member.bot, inline=False)
  await interaction.response.send_message(embed=embed)

@bot.tree.command(name = '문의', description = '봇을 통해 문의를 할 수 있습니다')  # 문의 명령어
async def 문의(interaction: discord.Interaction, 문의: str):  # 옵션

    
    embed = discord.Embed(title="📑 봇 문의 📑", description="ㅤ", color=0x4000FF)  # 문의 보낸 후 결과 임베드
    embed.add_field(name="봇 문의가 접수되었습니다", value="ㅤ", inline=False)
    embed.add_field(name="문의 내용", value="fix\n{}\n ".format(문의), inline=False)  # 문의 내용
    embed.add_field(name="ㅤ", value="**▣ 문의 내용에 대한 답장은 관리자가 확인후\n24시간 내에 답장이 오니 기다려 주시면 감사하겠습니다**", inline=False) 
    embed.add_field(name="ㅤ", value="- **관리자 이름** -", inline=False)  # 관리자 이름
    await interaction.response.send_message(embed=embed)
    users = await client.fetch_user("970967370128588820")   # 문의 온 문의 내용을 DM으로 받을 사람의 ID
    await users.send("유저 아이디 {}  / 문의 내용 {}".format(interaction.user.id, 문의)) # 그 사람에게 올 유저 ID와 문의 내용

@bot.tree.command(name = '문의답변', description = '봇을 통해 문의에 답변을 할 수 있습니다') #답변하기
async def 문의답변(interaction: discord.Interaction, 아이디: str, 답변: str):   # 옵션

    embed = discord.Embed(title="📑 봇 답변 📑", description="ㅤ", color=0x4000FF)   # 답변 임베드
    embed.add_field(name="문의에 대한 답변 내용", value="{}".format(답변) , inline=False)   
    await interaction.response.send_message(f"✅")  # 보내졌을시 나오는 확인 이모티콘


    user = await client.fetch_user("{}".format(아이디))
    await user.send(embed=embed)

@bot.tree.command(name = '랜덤뽑기', description= '봇을 랜덤으로 답장을 합니다')          # 봇 명령, 설명
async def 랜덤뽑기(interaction: discord.Interaction):
    ran = random.randint(0,3)       # 봇 랜덤 변수 갯수   0,3 = 0,1,2,3  /  0,5 = 0,1,2,3,4,5
    if ran == 0:        # 랜덤 변수 0
        d = "1"           # 랜덤 변수 0 의 내용
    if ran == 1:        # 랜덤 변수 1
        d = "2"           # 랜덤 변수 1 의 내용
    if ran == 2:        # 랜덤 변수 2
        d = "3"           # 랜덤 변수 2 의 내용
    if ran == 3:        # 랜덤 변수 3
        d = "4"           # 랜덤 변수 3 의 내용
    await interaction.response.send_message(d)

bot.run("봇 토큰")

# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import asyncio
import io
import json
import random
import re
import subprocess
import wave
from subprocess import Popen

import psycopg2
import requests as requests
import discord
import wavelink as wavelink
from discord import Guild
from discord.ext import tasks
from requests import Timeout, ReadTimeout


token = ""
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)
vclist = {}
voice_select_dict = {}
filelist = ["temp1.wav", "temp2.wav", "temp3.wav", "temp4.wav", "temp5.wav", "temp6.wav", "temp7.wav", "temp8.wav",
            "temp9.wav", "temp10.wav"]
counter = 0
DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASS = 'maikura123'
ManagerGuilds = [864441028866080768]
tips_list= ["/setvoice　で自分の声を変更できます"]
voice_id_list = []
host = '127.0.0.1'
port = 50021


def initdatabase():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS voice(id char(20), voiceid char(2));')
    cur.execute('ALTER TABLE voice ADD COLUMN IF NOT EXISTS readname char(15);')
    cur.execute('ALTER TABLE voice ADD COLUMN IF NOT EXISTS is_premium boolean;')
    cur.execute('CREATE TABLE IF NOT EXISTS guild(id char(20), is_premium boolean);')
    cur.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS is_joinoutread boolean;')
    conn.commit()
    cur.close()
    conn.close()


def init_voice_list():

    headers = {'Content-Type': 'application/json', }
    response2 = requests.get(
        f'http://{host}:{port}/speakers',
        headers=headers,
        timeout=(3.0, 10)
    )
    json : list = response2.json()
    global voice_id_list
    voice_id_list = json
    print(json)
    print(type(json))
    print([discord.SelectOption(label=e) for e in [d["name"] for d in voice_id_list]])
    print(discord.SelectOption(label=e) for e in ())


init_voice_list()

class VoiceSelectView(discord.ui.Select):
    def __init__(self, default=None):
        options = []
        for i in [discord.SelectOption(label=e) for e in [d["name"] for d in voice_id_list]]:
            if i.label == default:
                i.default = True
            options.append(i)

        super().__init__(placeholder='Voice', min_values=1, max_values=1, options=options)

    async def callback(self, interaction): # the function called when the user is done selecting options
        voice_select_dict.update()
        await interaction.response.edit_message(view=HogeList(name=self.values[0]))


class HogeList(discord.ui.View):
    def __init__(self,name=None):
        super().__init__()
        self.add_item(VoiceSelectView(default=name))
        self.add_item(VoiceSelectView2(name=name))

class VoiceSelectView2(discord.ui.Select):
    def __init__(self, name):
        options = []
        self.name = name
        for i in list(filter(lambda item : item['name'] == name, voice_id_list))[0]["styles"]:
            options.append(discord.SelectOption(label=i["name"]))

        super().__init__(placeholder='Style', min_values=1, max_values=1, options=options)

    async def callback(self, interaction : discord.Interaction):  # the function called when the user is done selecting options
        id = list(filter(lambda item2 : item2["name"] == self.values[0], (list(filter(lambda item : item['name'] == self.name, voice_id_list))[0]["styles"])))[0]["id"]
        embed = discord.Embed(
            title="**Changed voice**",
            description=f"**{self.name}({self.values[0]})** id:{id}に変更したのだ",
            color=discord.Colour.brand_green(),
        )
        print(f"**{self.name}({self.values[0]})**");
        setdatabase(interaction.user.id, "voiceid", id)
        await interaction.response.send_message(embed=embed)
        await interaction.message.delete()


@bot.slash_command(description="読み上げを開始・終了するのだ")
async def vc(ctx):
    await ctx.defer()
    if ctx.author.voice is None:
        await ctx.send_followup("音声チャンネルに入っていないため操作できません")
        return
    if ctx.guild.id in vclist and ctx.guild.voice_client is not None:
        del vclist[ctx.guild.id]
        await ctx.guild.voice_client.disconnect()
        embed = discord.Embed(
            title="Disconnect",
            color=discord.Colour.brand_red()
        )
        await ctx.send_followup(embed=embed)
        return
    else:
        await ctx.author.voice.channel.connect()
        vclist[ctx.guild.id] = ctx.channel.id
        embed = discord.Embed(
            title="Connect",
            color=discord.Colour.brand_green(),
            description="tips: `"+random.choice(tips_list)+"`"
        )
        await ctx.send_followup(embed=embed)
        return


@bot.slash_command(description="自分の声を変更できるのだ")
async def setvc(ctx, voiceid: discord.Option(required=False, input_type=int, description="指定しない場合は一覧が表示されます")):
    await ctx.defer()
    if (voiceid is None):
        await ctx.send_followup("", view=HogeList("ずんだもん"))
        return

    setdatabase(ctx.author.id, "voiceid", voiceid)
    name = ""
    for speaker in voice_id_list:
        if name != "":
            break
        for style in speaker["styles"]:
            if str(style["id"]) == voiceid:
                name = f"{speaker['name']}({style['name']})"
                break
    embed = discord.Embed(
            title="**Changed voice**",
            description=f"**{name}** id:{voiceid}に変更したのだ",
            color=discord.Colour.brand_green(),
        )
    print(f"**{name}**")
    await ctx.send_followup(embed=embed)


#@bot.slash_command(description="自分の名前の読み方を変更できるのだ", guild_ids=ManagerGuilds)
async def setname(ctx, name: discord.Option(input_type=str, description="自分の名前の読み方")):
    if len(name)>15:
        embed = discord.Embed(
            title="**Error**",
            description=f"16文字以上の設定はできません",
            color=discord.Colour.brand_red(),
        )
        await ctx.respond(embed=embed)
        return
    setdatabase(ctx.author.id, "readname", name)


#@bot.slash_command(description="ユーザーをプレミアム登録するのだ(modonly)", guild_ids=ManagerGuilds)
async def setpremium(ctx, id: discord.Option(input_type=int, description="対象ユーザーのID"), premium: discord.Option(input_type=bool, description="有効/無効")):
    setdatabase(id, "is_premium", premium)


#@bot.slash_command(description="出入りを読み上げるかの設定なのだ", guild_ids=ManagerGuilds)
async def setjoiuout(ctx, read: discord.Option(input_type=bool, description="有効/無効")):
    setdatabase(id, "is_joinoutread", read)


@bot.slash_command(description="辞書に単語を追加するのだ", guild_ids=ManagerGuilds)
async def adddict(ctx, surface: discord.Option(input_type=str, description="辞書に登録する単語"), pronunciation: discord.Option(input_type=str, description="カタカナでの読み方"),
                  accent_type: discord.Option(input_type=int, description="アクセント核位置、整数(詳しくはサイトに記載)",default=0)):
    params = (
        ('surface', surface),
        ('pronunciation', pronunciation),
        ('accent_type', accent_type)
    )
    headers = {'Content-Type': 'application/json', }
    response2 = requests.post(
        f'http://{host}:{port}/user_dict_word',
        headers=headers,
        params=params,
        timeout=(3.0, 10)
    )
    embed = discord.Embed(
        title="**Add Dict**",
        description=f"辞書に単語を登録しました。",
        color=discord.Colour.brand_green(),
    )
    embed.add_field(name="surface", value=surface)
    embed.add_field(name="pronunciation", value=pronunciation)
    embed.add_field(name="accent_type", value=accent_type)
    embed.add_field(name="uuid", value=response2.text)
    await ctx.respond(embed=embed)


def get_connection():
    return psycopg2.connect('postgresql://{user}:{password}@{host}:{port}/{dbname}'
        .format(
        user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, dbname=DB_NAME
    ))


def getdatabase(userid, id, default=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f'SELECT {id} from "voice" where "id" = %s;', (str(userid),))
    rows = cur.fetchone()
    if rows is None:
        cur.execute('INSERT INTO voice (id, voiceid) VALUES (%s, 3);', (str(userid),))
        conn.commit()
        cur.execute(f'SELECT {id} from voice where id = %s;', (str(userid),))
        rows = cur.fetchone()
    cur.close()
    conn.close()
    if rows[0] is None:
        return default
    else:
        return rows[0]



def setdatabase(userid, id, value):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('SELECT %s from "voice" where "id" = %s;', (id ,str(userid),))
    rows = cur.fetchone()
    if rows is None:
        cur.execute('INSERT INTO voice (id, voiceid) VALUES (%s, 3);', (str(userid),))
        conn.commit()
        cur.execute('SELECT voiceid from voice where id = %s;', (str(userid),))
        rows = cur.fetchone()
    cur.execute(f'UPDATE voice SET {id} = %s WHERE "id" = %s;', (value, str(userid)))
    conn.commit()
    cur.close()
    conn.close()
    return rows[0]


def text2wav(text, voiceid):
    global counter
    counter += 1
    if (counter > 9):
        counter = 0
    filename = filelist[counter]
    if generate_wav(text, voiceid, './' + filename):
        return filename
    else:
        return "failed"


def generate_wav(text, speaker=1, filepath='./audio.wav'):
    params = (
        ('text', text),
        ('speaker', speaker),
    )
    response1 = requests.post(
        f'http://{host}:{port}/audio_query',
        params=params,
        timeout=(3.0, 10)
    )
    headers = {'Content-Type': 'application/json', }
    query_json = response1.json()
    #query_json["prePhonemeLength"] = 0.1
    #query_json["outputSamplingRate"] = 96000
    response2 = requests.post(
        f'http://{host}:{port}/synthesis',
        headers=headers,
        params=params,
        data=json.dumps(query_json),
        timeout=(3.0, 10)
    )
    wf = wave.open(filepath, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(query_json["outputSamplingRate"])
    try:
        wf.writeframes(response2.content)
        wf.close()
        return True
    except ReadTimeout:
        wf.close()
        return False





@bot.event
async def on_ready():
    status_update_loop.start()
    print("起動しました")


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    voice = discord.utils.get(bot.voice_clients, guild=message.guild)

    if voice and voice.is_connected and message.channel.id == vclist[message.guild.id]:
        pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        pattern_emoji = "\<.+?\>"
        pattern_voice = "\.vc[0-9]*"
        voice_id = None

        if re.search(pattern_voice, message.content) is not None:
            cmd = re.search(pattern_voice, message.content).group()
            if re.search("[0-9]", cmd.group()) is not None:
                voice_id = re.search("[0-9]", cmd.group()).group()

        output = re.sub(pattern, "URL省略", message.content)
        output = re.sub(pattern_emoji, "", output)
        output = re.sub(pattern_voice, "", output)

        if voice_id is None:
            voice_id = getdatabase(message.author.id, "voiceid", 0)
        if len(output) > 50:
            output = output[:50]
            output += "以下略"
        if len(output) <= 0:
            return
        print(output)

        while message.guild.voice_client.is_playing():
            await asyncio.sleep(0.1)
        filename = text2wav(output, int(voice_id))
        if filename == "failed":
            return
        source = discord.FFmpegOpusAudio(source=filename, bitrate=24)
        message.guild.voice_client.play(source)
    else:
        return


@bot.event
async def on_voice_state_update(member, before, after):
    voicestate = member.guild.voice_client
    if voicestate is None:
        return
    if (voicestate.user.id == member.id and after.channel is None) or len(voicestate.channel.members) == 1:
        del vclist[voicestate.guild.id]
        await voicestate.disconnect(force=True)


@bot.event
async def on_guild_join(guild: Guild):
    await guild.get_member(bot.user.id).edit(nick="ずんだもんβ")



@tasks.loop(minutes=1)
async def status_update_loop():
    text = str(len(vclist)) + "/" + str(len(bot.guilds))+ " 読み上げ"
    await bot.change_presence(activity=discord.Game(text))



# Press the green button in the gutter to run the script.
initdatabase()
if __name__ == '__main__':

    bot.run(token)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

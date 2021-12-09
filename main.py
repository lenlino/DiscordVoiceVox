# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import asyncio
import json
import re
import wave

import psycopg2
import requests as requests
import discord

token = "OTE3NjMzNjA1Njg0MDU2MDg1.Ya7i5A.vjx7pL_UBz6gxGn8kshdJeVyiUI"
bot = discord.Bot()
vclist = {}
mclist = {}
filelist = ["temp1.wav", "temp2.wav", "temp3.wav", "temp4.wav", "temp5.wav", "temp6.wav", "temp7.wav", "temp8.wav",
            "temp9.wav", "temp10.wav"]
counter = 0
DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASS = 'maikura123'


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


@bot.slash_command()
async def vc(ctx):
    if ctx.author.voice is None:
        await ctx.respond("音声チャンネルに入っていないため操作できません")
        return
    if ctx.guild.voice_client is not None:
        del vclist[ctx.guild.id]
        await ctx.guild.voice_client.disconnect()
        await ctx.respond("切断しました")
        return
    else:
        vclist[ctx.guild.id] = ctx.channel.id
        await ctx.author.voice.channel.connect()
        await ctx.respond("読み上げを開始します")
        return

@bot.slash_command()
async def setvc(ctx, voiceid: int):
    setvoiceid(ctx.author.id, voiceid)
    await ctx.respond("設定を変更しました")


def get_connection():
    return psycopg2.connect('postgresql://{user}:{password}@{host}:{port}/{dbname}'
        .format(
        user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, dbname=DB_NAME
    ))


def getvoiceid(userid):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('SELECT "voiceid" from "voice" where "id" = %s;', (str(userid),))
    rows = cur.fetchone()
    if rows is None:
        cur.execute('INSERT INTO voice VALUES (%s, 0);', (str(userid),))
        conn.commit()
        cur.execute('SELECT voiceid from voice where id = %s;', (str(userid),))
        rows = cur.fetchone()
    print(rows[0])
    cur.close()
    conn.close()
    return rows[0]


def setvoiceid(userid, voiceid):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('SELECT "voiceid" from "voice" where "id" = %s;', (str(userid),))
    rows = cur.fetchone()
    if rows is None:
        cur.execute('INSERT INTO voice VALUES (%s, %s);', (str(userid), voiceid))
        conn.commit()
        cur.execute('SELECT voiceid from voice where id = %s;', (str(userid),))
        rows = cur.fetchone()
    print(rows[0])
    cur.execute('UPDATE voice SET voiceid = %s WHERE "id" = %s;', (voiceid,str(userid)))
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
    generate_wav(text, voiceid, './' + filename)

    return filename


def generate_wav(text, speaker=1, filepath='./audio.wav'):
    host = 'localhost'
    port = 50021
    params = (
        ('text', text),
        ('speaker', speaker),
    )
    response1 = requests.post(
        f'http://{host}:{port}/audio_query',
        params=params
    )
    headers = {'Content-Type': 'application/json', }
    response2 = requests.post(
        f'http://{host}:{port}/synthesis',
        headers=headers,
        params=params,
        data=json.dumps(response1.json())
    )

    wf = wave.open(filepath, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(24000)
    wf.writeframes(response2.content)
    wf.close()


async def vc(ctx):
    if ctx.author.voice is None:
        await ctx.channel.send("音声チャンネルに入っていないため操作できません")
        return
    if ctx is not None:
        del vclist[ctx.guild.id]
        await ctx.guild.voice_client.disconnect()
        await ctx.channel.send("切断しました")
        return
    else:
        vclist[ctx.guild.id] = ctx.channel.id
        await ctx.author.voice.channel.connect()
        await ctx.channel.send("接続しました。読み上げを開始します")
        return


@bot.event
async def on_ready():
    print("起動しました")


@bot.event
async def on_message(message):
    voice = discord.utils.get(bot.voice_clients, guild=message.guild)

    if voice and voice.is_connected and message.channel.id == vclist[message.guild.id]:
        pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        pattern_emoji = "\<.+?\>"

        output = re.sub(pattern, "URL省略", message.content)
        output = re.sub(pattern_emoji, "", output)
        if len(output) > 50:
            output = output[:len(output)-50]
            output += "以下略"
        print(output)

        while message.guild.voice_client.is_playing():
            await asyncio.sleep(0.1)
        source = discord.FFmpegPCMAudio(text2wav(output, getvoiceid(message.author.id)))
        message.guild.voice_client.play(source)
        return
    else:
        return


@bot.event
async def on_voice_state_update(member, before, after):
    voicestate = member.guild.voice_client
    if voicestate is None:
        return
    if len(voicestate.channel.members) == 1:
        await voicestate.disconnect()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    bot.run(token)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

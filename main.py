# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import asyncio
import json
import logging
import os
import random
import re
import time
import importlib

import aiofiles as aiofiles
import aiohttp
import asyncpg as asyncpg
import discord
import requests as requests
import stripe
import wavelink
from discord import default_permissions
from discord.ext import tasks, pages
from psycopg2._json import Json
from requests import ReadTimeout

import emoji

token =
host = '127.0.0.1'
port = 50021
premium_host_list = ['127.0.0.1:50021']
host_count = 0
coeiroink_host = '127.0.0.1'
coeiroink_port = 50031
ManagerGuilds = [888020016660893726]
intents = discord.Intents.none()
intents.message_content = True
intents.guilds = True
intents.voice_states = True
intents.guild_messages = True
bot = discord.AutoShardedBot(intents=intents)
vclist = {}
voice_select_dict = {}
premium_user_list = []
premium_server_list = []
counter = 0
voiceapi_counter = 0
DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASS =
tips_list = ["/setvc　で自分の声を変更できます。","[プレミアムプラン](https://lenlino.com/?page_id=2510)(月100円～)あります。",
             "[要望・不具合募集中](https://forms.gle/1TvbqzHRz6Q1vSfq9)",]
voice_id_list = []

stripe.api_key =
generating_guilds = set()
pool = None
logger = logging.getLogger('discord')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
default_conn = aiohttp.TCPConnector(limit_per_host=3)


async def initdatabase():
    async with pool.acquire() as conn:
        await conn.execute('CREATE TABLE IF NOT EXISTS voice(id char(20), voiceid char(4));')
        await conn.execute('ALTER TABLE voice ADD COLUMN IF NOT EXISTS readname char(15);')
        await conn.execute('ALTER TABLE voice ADD COLUMN IF NOT EXISTS is_premium boolean;')
        await conn.execute('ALTER TABLE voice ADD COLUMN IF NOT EXISTS speed char(3);')
        await conn.execute('ALTER TABLE voice ADD COLUMN IF NOT EXISTS pitch char(3);')
        await conn.execute('CREATE TABLE IF NOT EXISTS guild(id char(20), is_premium boolean);')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS is_joinoutread boolean;')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS auto_join jsonb;')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS is_reademoji boolean;')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS is_readname boolean;')



async def init_voice_list():
    headers = {'Content-Type': 'application/json', }
    async with aiohttp.ClientSession() as session:
        async with session.get(
        f'http://{host}:{port}/speakers',
        headers=headers,
        timeout=10
        ) as response2:
            json: list = await response2.json()
        async with session.get(
            f'http://{coeiroink_host}:{coeiroink_port}/speakers',
            headers=headers,
            timeout=10
        ) as response3:
            json2: list = await response3.json()
            for voice_info in json2:
                for style_info in voice_info["styles"]:
                    style_info["id"] += 1000

            json.extend(json2)


    global voice_id_list
    voice_id_list = json
    print(json)
    print(type(json))
    print([discord.SelectOption(label=e) for e in [d["name"] for d in voice_id_list]])
    print(discord.SelectOption(label=e) for e in ())


class VoiceSelectView(discord.ui.Select):
    def __init__(self, default=None, id_list=voice_id_list, start=0, end=0):
        self.end = end
        self.start = start
        options = []
        for i in [discord.SelectOption(label=e) for e in [d["name"] for d in id_list]]:
            if i.label == default:
                i.default = True
            options.append(i)

        super().__init__(placeholder='Voice', min_values=1, max_values=1, options=options)

    async def callback(self, interaction):  # the function called when the user is done selecting options
        await interaction.response.edit_message(view=HogeList(name=self.values[0],start=self.start,end=self.end))


class HogeList(discord.ui.View):
    def __init__(self, name=None, start=0, end=0):
        super().__init__()
        self.add_item(VoiceSelectView(default=name, id_list=voice_id_list[start:end],start=start, end=end))
        self.add_item(VoiceSelectView2(name=name,start=start))


class VoiceSelectView2(discord.ui.Select):
    def __init__(self, name, start=1):
        options = []
        self.name = name
        for i in (list(filter(lambda item: item['name'] == self.name, voice_id_list))[0]["styles"]):
            options.append(discord.SelectOption(label=i["name"]))

        super().__init__(placeholder='Style', min_values=1, max_values=1, options=options)

    async def callback(self,
                       interaction: discord.Interaction):  # the function called when the user is done selecting options
        id = list(filter(lambda item2: item2["name"] == self.values[0],
                         (list(filter(lambda item: item['name'] == self.name, voice_id_list))[0]["styles"])))[0]["id"]
        embed = discord.Embed(
            title="**Changed voice**",
            description=f"**{self.name}({self.values[0]})** id:{id}に変更したのだ",
            color=discord.Colour.brand_green(),
        )
        if id >= 1000 and str(interaction.user.id) not in premium_user_list:
            embed = discord.Embed(
                title="**Error**",
                description=f"この音声はプレミアムプラン限定です。",
                color=discord.Colour.brand_red(),
            )
        else:
            await setdatabase(interaction.user.id, "voiceid", id)
        print(f"**{self.name}({self.values[0]})**")
        await interaction.response.send_message(embed=embed)
        await interaction.message.delete()


class ActivateButtonView(discord.ui.View):  # Create a class called MyView that subclasses discord.ui.View

    def __init__(self):
        super().__init__(timeout=None)  # timeout of the view must be set to None

    @discord.ui.button(label="Activate", style=discord.ButtonStyle.primary, custom_id="activate_button")
    async def button_callback(self, button, interaction):
        await interaction.response.send_modal(ActivateModal(title="Activate"))


class ActivateModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="メールアドレスを入力してください。(登録状況の参照にのみ使用されます。)"))

    async def callback(self, interaction: discord.Interaction):
        mail = self.children[0].value
        customer: list = stripe.Customer.search(query=f"email: '{mail}'")["data"]
        if len(customer) == 0:
            embed = discord.Embed(title="fail", color=discord.Colour.brand_red())
            embed.description = "ユーザーが存在しません。"
            await interaction.response.send_message(embeds=[embed], ephemeral=True)
            return
        customer_id = customer[0]["id"]
        subscription: list = stripe.Subscription.search(query=f"status:'active' AND metadata['discord_user_id']:null")
        target_subscription = list(filter(lambda item: item['customer'] == customer_id, subscription))
        if len(target_subscription) == 0:
            embed = discord.Embed(title="fail", color=discord.Colour.brand_red())
            embed.description = "有効なサブスクリプションが存在しません。"
            await interaction.response.send_message(embeds=[embed], ephemeral=True)
            return

        subscription_id = target_subscription[0]["id"]
        stripe.Subscription.modify(subscription_id, metadata={"discord_user_id": interaction.user.id})
        embed = discord.Embed(title="success")
        embed.description = "プレミアムプランへの登録が完了しました。"
        premium_user_list.append(str(interaction.user.id))
        await interaction.response.send_message(embeds=[embed], ephemeral=True)


@bot.slash_command(description="読み上げを開始・終了するのだ")
async def vc(ctx):
    await ctx.defer()
    if ctx.author.voice is None:
        await ctx.send_followup("音声チャンネルに入っていないため操作できません")
        return
    if ctx.guild.voice_client is not None:
        del vclist[ctx.guild.id]
        await ctx.guild.voice_client.disconnect()
        embed = discord.Embed(
            title="Disconnect",
            color=discord.Colour.brand_red()
        )
        await ctx.send_followup(embed=embed)
        return
    else:
        vclist[ctx.guild.id] = ctx.channel.id
        await ctx.author.voice.channel.connect(cls=wavelink.Player)
        embed = discord.Embed(
            title="Connect",
            color=discord.Colour.brand_green(),
            description="tips: " + random.choice(tips_list)
        )
        if ctx.guild.id in premium_server_list:
            premium_server_list.remove(ctx.guild.id)
        if str(ctx.author.id) in premium_user_list:
            embed.set_author(name="Premium")
            premium_server_list.append(ctx.guild.id)

        await ctx.send_followup(embed=embed)
        return


@bot.slash_command(description="色々な設定なのだ")
async def set(ctx, key: discord.Option(str, choices=[
    discord.OptionChoice(name="voice", value="voice"),
    discord.OptionChoice(name="speed", value="speed"),
    discord.OptionChoice(name="pitch", value="pitch")], description="設定項目"), value: discord.Option(str, description="設定値", required=False)):
    await ctx.defer()
    if key == "voice":
        if value is None:
            test_pages = []
            for i in range(-(-len(voice_id_list)//25)):
                name = None
                if i==0:
                    name = "ずんだもん"
                else:
                    name = voice_id_list[i*25]["name"]
                test_pages.append(pages.Page(content="ボイス・スタイルを選択してください。",custom_view=HogeList(name=name,start=i*25,end=((i+1)*25))))
            paginator = pages.Paginator(pages=test_pages)
            await paginator.respond(ctx.interaction)
            return
        else:
            if value.isdecimal() is False:
                embed = discord.Embed(
                    title="**Error**",
                    description=f"valueは数字なのだ",
                    color=discord.Colour.brand_red(),
                )
                print(f"**errorid**")
                await ctx.send_followup(embed=embed)
                return
            elif int(value) >= 1000 and str(ctx.author.id) not in premium_user_list:
                embed = discord.Embed(
                    title="**Error**",
                    description=f"この音声はプレミアムプラン限定なのだ",
                    color=discord.Colour.brand_red(),
                )
                print(f"**errorvoice**")
                await ctx.send_followup(embed=embed)
                return
            await setdatabase(ctx.author.id, "voiceid", value)
            name = ""
            for speaker in voice_id_list:
                if name != "":
                    break
                for style in speaker["styles"]:
                    if str(style["id"]) == value:
                        name = f"{speaker['name']}({style['name']})"
                        break
            embed = discord.Embed(
                title="**Changed Voice**",
                description=f"**{name}** id:{value}に変更したのだ",
                color=discord.Colour.brand_green(),
            )
            await ctx.send_followup(embed=embed)
    elif key == "speed":
        if value is None:
            value = "100"
        if value.isdecimal() is False:
            embed = discord.Embed(
                title="**Error**",
                description=f"valueは数字なのだ",
                color=discord.Colour.brand_red(),
            )
            await ctx.send_followup(embed=embed)
            return
        await setdatabase(ctx.author.id, "speed", value)
        embed = discord.Embed(
            title="**Changed Speed**",
            description=f"読み上げ速度を {value} に変更したのだ",
            color=discord.Colour.brand_green(),
        )
        await ctx.send_followup(embed=embed)
    elif key == "pitch":
        if value is None:
            value = "0"
        try:
            int(value)
        except ValueError:
            embed = discord.Embed(
                title="**Error**",
                description=f"valueは数字なのだ",
                color=discord.Colour.brand_red(),
            )
            await ctx.send_followup(embed=embed)
            return

        await setdatabase(ctx.author.id, "pitch", value)
        embed = discord.Embed(
            title="**Changed Speed**",
            description=f"読み上げピッチを {value} に変更したのだ",
            color=discord.Colour.brand_green(),
        )
        await ctx.send_followup(embed=embed)


@bot.slash_command(description="サーバーの色々な設定なのだ", name="server-set", default_member_permissions=discord.Permissions.manage_guild)
@default_permissions(manage_messages=True)
async def server_set(ctx, key: discord.Option(str, choices=[
    discord.OptionChoice(name="autojoin", value="autojoin"),
    discord.OptionChoice(name="reademoji"),
    discord.OptionChoice(name="readname")], description="設定項目"), value: discord.Option(str, description="設定値", required=False),):
    await ctx.defer()
    guild_id = ctx.guild_id
    if key == "autojoin":
        text_channel_id = ctx.channel_id
        if value == "0":
            setting_json = Json({"text_channel_id": 1, "voice_channel_id": 1})
            await setdatabase(ctx.guild.id, "auto_join", setting_json,"guild")
            embed = discord.Embed(
                title="Changed AutoJoin",
                description="自動接続を削除しました。",
                color=discord.Colour.brand_green()
            )
            await ctx.send_followup(embed=embed)
            return
        if ctx.author.voice is None:
            embed = discord.Embed(
                title="Error",
                description="対象のボイスチャットに接続してから実行してください。",
                color=discord.Colour.brand_red()
            )
            await ctx.send_followup(embed=embed)
            return
        voice_channel_id = ctx.author.voice.channel.id
        setting_json = Json({"text_channel_id":text_channel_id, "voice_channel_id":voice_channel_id})
        await setdatabase(ctx.guild.id, "auto_join", setting_json,"guild")
        embed = discord.Embed(
            title="Changed AutoJoin",
            description="現在の接続している音声チャンネル、テキストチャンネルで設定したのだ。(OFFにする際は0をvalueに設定して実行してください。)",
            color=discord.Colour.brand_green()
        )
        await ctx.send_followup(embed=embed)
    elif key == "reademoji":
        embed = discord.Embed(
            title="Changed ReadEmoji",
            description="絵文字",
            color=discord.Colour.brand_green()
        )
        if value is None:
            embed.description = "絵文字の読み上げをオンにしました（デフォルト）(1:ON,0:OFF)"
            await setdatabase(ctx.guild.id, "is_reademoji", True, "guild")
        elif value == "0":
            embed.description = "絵文字の読み上げをオフにしました。"
            await setdatabase(ctx.guild.id, "is_reademoji", False, "guild")
        elif value == "1":
            embed.description = "絵文字の読み上げをオンにしました。"
            await setdatabase(ctx.guild.id, "is_reademoji", True, "guild")
        else:
            embed.title = "Error"
            embed.description = "数字をvalueに指定してください。(1:ON,0:OFF)"
            embed.color = discord.Colour.brand_red()
        await ctx.send_followup(embed=embed)
    elif key == "readname":
        embed = discord.Embed(
            title="Changed ReadName",
            description="名前",
            color=discord.Colour.brand_green()
        )
        if value is None:
            embed.description = "名前の読み上げをオンにしました（デフォルト）(1:ON,0:OFF)"
            await setdatabase(ctx.guild.id, "is_readname", True, "guild")
        elif value == "0":
            embed.description = "名前の読み上げをオフにしました。"
            await setdatabase(ctx.guild.id, "is_readname", False, "guild")
        elif value == "1":
            embed.description = "名前の読み上げをオンにしました。"
            await setdatabase(ctx.guild.id, "is_readname", True, "guild")
        else:
            embed.title = "Error"
            embed.description = "数字をvalueに指定してください。(1:ON,0:OFF)"
            embed.color = discord.Colour.brand_red()
        await ctx.send_followup(embed=embed)


@bot.slash_command(description="自分の声を変更できるのだ")
async def setvc(ctx, voiceid: discord.Option(required=False, input_type=int, description="指定しない場合は一覧が表示されます")):
    await ctx.defer()
    if (voiceid is None):
        test_pages = []
        for i in range(-(-len(voice_id_list) // 25)):
            if i == 0:
                name = "ずんだもん"
            else:
                name = voice_id_list[i * 25]["name"]
            test_pages.append(pages.Page(content="ボイス・スタイルを選択してください。",
                                         custom_view=HogeList(name=name, start=i * 25, end=((i + 1) * 25))))
        paginator = pages.Paginator(pages=test_pages)
        await paginator.respond(ctx.interaction)
        return

    if voiceid.isdecimal() is False:
        embed = discord.Embed(
            title="**Error**",
            description=f"idは数字なのだ",
            color=discord.Colour.brand_red(),
        )
        print(f"**errorid**")
        await ctx.send_followup(embed=embed)
        return
    elif int(voiceid) >= 1000 and str(ctx.author.id) not in premium_user_list:
        embed = discord.Embed(
            title="**Error**",
            description=f"この音声はプレミアムプラン限定です。",
            color=discord.Colour.brand_red(),
        )
        print(f"**errorvoice**")
        await ctx.send_followup(embed=embed)
        return
    await setdatabase(ctx.author.id, "voiceid", voiceid)
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


# @bot.slash_command(description="自分の名前の読み方を変更できるのだ", guild_ids=ManagerGuilds)
async def setname(ctx, name: discord.Option(input_type=str, description="自分の名前の読み方")):
    if len(name) > 15:
        embed = discord.Embed(
            title="**Error**",
            description=f"16文字以上の設定はできません",
            color=discord.Colour.brand_red(),
        )
        await ctx.respond(embed=embed)
        return
    await setdatabase(ctx.author.id, "readname", name)


@bot.slash_command(description="ユーザーをプレミアム登録するのだ(modonly)", guild_ids=ManagerGuilds)
async def activate(ctx):
    embed = discord.Embed(
        title="Activate",
        description=f"ボタンを",
        color=discord.Colour.gold(),
    )
    await ctx.respond(embed=embed, view=ActivateButtonView())


@bot.slash_command(description="辞書に単語を追加するのだ", guild_ids=ManagerGuilds)
async def adddict(ctx, surface: discord.Option(input_type=str, description="辞書に登録する単語"),
                  pronunciation: discord.Option(input_type=str, description="カタカナでの読み方"),
                  accent_type: discord.Option(input_type=int, description="アクセント核位置、整数(詳しくはサイトに記載)",
                                              default=0)):
    print(surface)
    if (surface.startswith("<") and surface.endswith(">")) or emoji.is_emoji(surface):
        await save_customemoji(surface, pronunciation)
        embed2 = discord.Embed(
            title="**Add Emoji**",
            description=f"辞書に絵文字を登録しました。",
            color=discord.Colour.brand_green(),
        )
        embed2.add_field(name="surface", value=surface)
        embed2.add_field(name="pronunciation", value=pronunciation)
        await ctx.respond(embed=embed2)
        return


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
    await updatedict()


@bot.slash_command(description="辞書から単語を削除するのだ", guild_ids=ManagerGuilds)
async def deletedict(ctx, uuid: discord.Option(input_type=str, description="辞書に登録する単語", required=True)):
    headers = {'Content-Type': 'application/json', }
    embed = discord.Embed(
        title="**Add Dict**",
        description=f"辞書から単語を削除しました。",
        color=discord.Colour.brand_red(),
    )
    for d_host in premium_host_list:
        response2 = requests.delete(
            f'http://{d_host}/user_dict_word/{uuid}',
            headers=headers,
            timeout=(3.0, 10)
        )
        embed.add_field(name="uuid", value=response2.text)



    await ctx.respond(embed=embed)


async def get_connection():
    return await asyncpg.create_pool('postgresql://{user}:{password}@{host}:{port}/{dbname}'
    .format(
        user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, dbname=DB_NAME
    ))


async def getdatabase(userid, id, default=None, table="voice"):
    async with pool.acquire() as conn:
        rows = await conn.fetchrow(f'SELECT {id} from {table} where "id" = $1;', (str(userid)))
        if rows is None:
            if table == "voice":
                await conn.execute(f'INSERT INTO {table} (id, voiceid) VALUES ($1, 3);', (str(userid)))
                rows = await conn.fetchrow(f'SELECT {id} from {table} where "id" = $1;', (str(userid)))
            elif table == "guild":
                await conn.execute(f'INSERT INTO {table} (id) VALUES ($1);', (str(userid)))
                rows = await conn.fetchrow(f'SELECT {id} from {table} where "id" = $1;', (str(userid)))
        if rows[0] is None:
            return default
        else:
            return rows[0]


async def setdatabase(userid, id, value, table="voice"):
    async with pool.acquire() as conn:
        rows = await conn.fetchrow(f'SELECT {id} from {table} where "id" = $1;', (str(userid)))
        if rows is None:
            await conn.execute('INSERT INTO voice (id, voiceid) VALUES ($1, 3);', (str(userid)))
            rows = await conn.fetchrow('SELECT voiceid from voice where id = $1;', (str(userid)))
        await conn.execute(f'UPDATE {table} SET {id} = {value} WHERE "id" = $1;', (str(userid)))
        return rows[0]


async def text2wav(text, voiceid, is_premium: bool, speed="100", pitch="0"):
    global counter
    counter += 1
    if counter > 30:
        counter = 0
    filename = "temp"+str(counter)+".wav"

    if voiceid >= 1000:
        target_host =f"{coeiroink_host}:{coeiroink_port}"
        voiceid -= 1000
    else:
        target_port = 50021
        global voiceapi_counter
        target_host = premium_host_list[voiceapi_counter]
        if voiceapi_counter+1 >= len(premium_host_list):
            voiceapi_counter=0
        else:
            voiceapi_counter+=1
    if await generate_wav(text, voiceid, './' + filename, target_host=target_host,
                          is_premium=is_premium,speed=speed,pitch=pitch):
        return filename
    else:
        return "failed"


async def generate_wav(text, speaker=1, filepath='./audio.wav', target_host='localhost', target_port=50021,
                       is_premium=False,speed="100",pitch="0"):

    params = (
        ('text', text),
        ('speaker', speaker),
    )
    if is_premium:
        conn = None
        owner = True
    else:
        conn = default_conn
        owner = False
    try:
        async with aiohttp.ClientSession(connector_owner=owner, connector=conn) as private_session:
            async with private_session.post(f'http://{target_host}/audio_query',
                                            params=params,
                                            timeout=30) as response1:
                if response1.status != 200:
                    return False
                headers = {'Content-Type': 'application/json', }
                query_json = await response1.json()
                # query_json["prePhonemeLength"] = 0.4
                query_json["outputSamplingRate"] = 24000
                query_json["speedScale"] = int(speed) / 100
                query_json["pitchScale"] = int(pitch) / 100
                lenge = len(query_json["kana"])
                if lenge > 50:
                    if is_premium:
                        if lenge > 100:
                            query_json["kana"] = query_json["kana"][:100]
                            query_json["kana"] += "イカリャク'"
                    else:
                        query_json["kana"] = query_json["kana"][:50]
                        query_json["kana"] += "イカリャク'"
            async with private_session.post(f'http://{target_host}/synthesis',
                                            headers=headers,
                                            params=params,
                                            data=json.dumps(query_json),
                                            timeout=30) as response2:
                if response2.status != 200:
                    return False

                try:
                    async with aiofiles.open(filepath, mode='wb') as f:
                        await f.write(await response2.read())
                    return True
                except ReadTimeout:
                    return False
    except:
        return False





@bot.event
async def on_ready():
    print("起動しました")


@bot.event
async def on_message(message):
    voice = discord.utils.get(bot.voice_clients, guild=message.guild)
    if message.guild.id not in vclist.keys():
        if voice is not None:
            await voice.disconnect(force=True)
        return

    if voice is not None and message.channel.id == vclist[message.guild.id]:
        pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        pattern_emoji = "\<.+?\>"
        pattern_voice = "\.v[0-9]*"
        voice_id = None
        is_premium = message.guild.id in premium_server_list
        output = message.content
        if message.guild.id in premium_server_list:
            if re.search(pattern_voice, message.content) is not None:
                cmd = re.search(pattern_voice, message.content).group()
                if re.search("[0-9]", cmd) is not None:
                    voice_id = re.sub(r"\D", "", cmd)
            if re.search(pattern, message.content) is not None:
                url = re.search(pattern, message.content).group()
                async with aiohttp.ClientSession() as session:
                    async with session.get(url=url,timeout=5) as response:
                        html = await response.text()
                        title = re.findall('<title>(.*)</title>',html)[0]
                        if title is not None:
                            output = re.sub(pattern, "URL "+title, output)
        if await getdatabase(message.guild.id, "is_reademoji", True, "guild"):
            output = emoji.demojize(output, language="ja")



        if await getdatabase(message.guild.id, "is_readname", False, "guild"):
            output = message.author.display_name + " " + output



        output = re.sub(pattern, "URL省略", output)
        output = re.sub(pattern_emoji, "", output)
        output = re.sub(pattern_voice, "", output)
        output = re.sub("w{4,100}", "笑", output)
        if re.search("[^w]", output) is None:
            output = "笑"

        if voice_id is None:
            voice_id = await getdatabase(message.author.id, "voiceid", 0)
        if len(output) > 100:
            output = output[:100]


        if len(output) <= 0:
            return
        print(output)

        while message.guild.voice_client.is_playing() or message.guild.id in generating_guilds:
            await asyncio.sleep(0.5)
        generating_guilds.add(message.guild.id)
        try:
            time_sta = time.time()
            done =True
            while done:
                filename = await text2wav(output, int(voice_id), is_premium,
                                          speed=await getdatabase(message.author.id, "speed", 100),
                                          pitch=await getdatabase(message.author.id, "pitch", 0))
                if filename != "failed":
                    print("合成失敗")
                    done = False

            time_end = time.time()
            tim = time_end - time_sta
            print("音声合成:"+str(tim))
            time_sta = time.time()
            source = await wavelink.LocalTrack.search(query=os.path.dirname(os.path.abspath(__file__)) + "/" + filename,
                                                      return_first=True)
            time_end = time.time()
            tim = time_end - time_sta
            print("ソース:" + str(tim))
        finally:
            generating_guilds.remove(message.guild.id)
        await message.guild.voice_client.play(source)
        print("☑")
    else:
        return


@bot.event
async def on_voice_state_update(member, before, after):
    voicestate = member.guild.voice_client
    if after.channel is not None and voicestate is None and member.bot is False and len(after.channel.members) == 1:
        json_str = await getdatabase(after.channel.guild.id, "auto_join", None, "guild")
        if json_str is None:
            return
        autojoin = json.loads(json_str)
        if int(autojoin["voice_channel_id"]) == int(after.channel.id):
            vclist[after.channel.guild.id] = autojoin["text_channel_id"]
            embed = discord.Embed(
                title="Connect",
                color=discord.Colour.brand_green(),
                description="tips: " + random.choice(tips_list)
            )
            if after.channel.guild.id in premium_server_list:
                premium_server_list.remove(after.channel.guild.id)
            if str(member.id) in premium_user_list:
                embed.set_author(name="Premium")
                premium_server_list.append(after.channel.guild.id)
            await after.channel.guild.get_channel(autojoin["text_channel_id"]).send(embed=embed)
            await asyncio.sleep(1.0)
            await after.channel.connect(cls=wavelink.Player)
        return

    if voicestate is None:
        return

    if (voicestate.client.user.id == member.id and after.channel is None) or (len(voicestate.channel.members) == 1 and (member.bot is False or voicestate.channel.members[0].bot)):
        await voicestate.disconnect()
        del vclist[voicestate.guild.id]


@bot.event
async def on_guild_join(guild):
    await guild.get_member(bot.user.id).edit(nick="ずんだもんβ")


@tasks.loop(minutes=1)
async def status_update_loop():
    for key in list(vclist):
        guild = bot.get_guild(key)
        if guild is None:
            del vclist[key]
            continue
        if guild.voice_client is None or guild.voice_client.channel is None:
            del vclist[key]
    text = str(len(vclist)) + "/" + str(len(bot.guilds)) + " 読み上げ"
    await bot.change_presence(activity=discord.Game(text))


@tasks.loop(hours=24)
async def premium_user_check_loop():
    global premium_user_list
    premium_user_list = [d['metadata']['discord_user_id'] for d in stripe.Subscription.search(limit=100,
                                                                                              query="status:'active' AND -metadata['discord_user_id']:null")]
    print(premium_user_list)


@tasks.loop(minutes=1)
async def init_loop():
    global pool
    pool = await get_connection()
    await initdatabase()
    await init_voice_list()
    status_update_loop.start()
    premium_user_check_loop.start()
    bot.add_view(ActivateButtonView())
    bot.loop.create_task(connect_nodes())
    await updatedict()



async def connect_nodes():
    """Connect to our Lavalink nodes."""
    await bot.wait_until_ready()
    await wavelink.NodePool.create_node(
        bot=bot,
        host='127.0.0.1',
        port=2333,
        password='youshallnotpass',
    )

async def save_customemoji(custom_emoji, kana):
    with open("custom_emoji.json") as f:
        json_data = json.load(f)
    json_data.update({custom_emoji : {"ja" : " "+kana+" "}})
    with open('custom_emoji.json', 'wt') as f:
        json.dump(json_data, f, ensure_ascii=False)
    importlib.reload(emoji)
    emoji.EMOJI_DATA.update(json_data)


async def updatedict():
    with open("custom_emoji.json",) as f:
        json_data = json.load(f)
    emoji.EMOJI_DATA.update(json_data)

    headers = {'Content-Type': 'application/json', }
    async with aiohttp.ClientSession() as session:
        async with session.get(
        f'http://{host}:{port}/user_dict',
        headers=headers,
        timeout=10
        ) as response2:
            result = await response2.json()
            print(result)
        for d_host in premium_host_list:
            async with session.post(f'http://{d_host}/import_user_dict?override=true',
                                            headers=headers,
                                            data=json.dumps(result),
                                            timeout=30) as response1:
                print(response1)




if __name__ == '__main__':
    bot.loop.create_task(init_loop())
    bot.run(token)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
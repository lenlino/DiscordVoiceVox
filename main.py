# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import asyncio
import datetime
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
import stripe
import wavelink
from discord import default_permissions
from discord.ext import tasks, pages
from requests import ReadTimeout
from ko2kana import korean2katakana
from dotenv import load_dotenv

import emoji
import romajitable

load_dotenv()

token = os.environ.get("BOT_TOKEN", "BOT_TOKEN_HERE")
host = os.environ.get("VOICEVOX_HOST", "127.0.0.1:50021")
premium_host_list = os.environ.get("VOICEVOX_HOSTS", "127.0.0.1:50021").split(",")
host_count = 0
stripe.api_key = os.environ.get("STRIPE_TOKEN", None)
is_lavalink = True
coeiroink_host = os.environ.get("COEIROINK_HOST", "127.0.0.1:50032")
sharevox_host = os.environ.get("SHAREVOX_HOST", "127.0.0.1:50025")
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
voice_cache_dict = {}
voice_cache_counter_dict = {}
counter = 0
voiceapi_counter = 0
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "maikura123")
tips_list = ["/setvc　で自分の声を変更できます。", "[プレミアムプラン](https://lenlino.com/?page_id=2510)(月100円～)あります。",
             "[要望・不具合募集中](https://forms.gle/1TvbqzHRz6Q1vSfq9)",
             "[VOICEVOX規約](https://voicevox.hiroshiba.jp/term/)の遵守をお願いします。",
             "10/05 [VOICEVOX](https://voicevox.hiroshiba.jp/)より音声が追加されました。/setvcより音声の変更が可能です。追加音声：栗田まろん、あいえるたん、満点花丸、琴詠ニア",
             "/vc コマンドで「考え中...」のまま動かない場合は[サポートサーバー](https://discord.gg/MWnnkbXSDJ)へお問い合わせください。"]
voice_id_list = []

generating_guilds = {}
pool = None
logger = logging.getLogger('discord')
handler = logging.FileHandler(filename=os.path.dirname(os.path.abspath(__file__)) + "/" + 'discord.log',
                              encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
default_conn = aiohttp.TCPConnector(limit_per_host=16)
premium_conn = aiohttp.TCPConnector()


async def initdatabase():
    async with pool.acquire() as conn:
        await conn.set_type_codec("jsonb", schema="pg_catalog", encoder=json.dumps, decoder=json.loads)
        await conn.execute('CREATE TABLE IF NOT EXISTS voice(id char(20), voiceid char(4));')
        await conn.execute('ALTER TABLE voice ADD COLUMN IF NOT EXISTS readname char(15);')
        await conn.execute('ALTER TABLE voice ADD COLUMN IF NOT EXISTS is_premium boolean;')
        await conn.execute('ALTER TABLE voice ADD COLUMN IF NOT EXISTS speed char(3);')
        await conn.execute('ALTER TABLE voice ADD COLUMN IF NOT EXISTS pitch char(3);')
        await conn.execute('ALTER TABLE voice ADD COLUMN IF NOT EXISTS premium_guild1 char(20);')
        await conn.execute('ALTER TABLE voice ADD COLUMN IF NOT EXISTS premium_guild2 char(20);')
        await conn.execute('ALTER TABLE voice ADD COLUMN IF NOT EXISTS premium_guild3 char(20);')
        await conn.execute('CREATE TABLE IF NOT EXISTS guild(id char(20), is_premium boolean);')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS is_joinoutread boolean;')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS auto_join jsonb;')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS is_reademoji boolean;')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS is_readname boolean;')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS is_readjoin boolean;')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS is_readurl boolean;')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS is_readsan boolean;')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS premium_user char(20);')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS lang char(2);')


async def init_voice_list():
    headers = {'Content-Type': 'application/json', }
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'http://{host}/speakers',
            headers=headers,
            timeout=10
        ) as response2:
            json: list = await response2.json()
            for voice_info in json:
                voice_info["name"] = "VOICEVOX:" + voice_info["name"]
        try:
            async with session.get(
                f'http://{coeiroink_host}/v1/speakers',
                headers=headers,
                timeout=10
            ) as response3:
                json2: list = await response3.json()
                for voice_info in json2:
                    voice_info["name"] = "COEIROINK:" + voice_info["speakerName"]
                    for style_info in voice_info["styles"]:
                        style_info["id"] = style_info["styleId"] + 1000
                        style_info["name"] = style_info["styleName"]

                json.extend(json2)
        except:
            print("COEIROINK接続なし")
        try:
            async with session.get(
                f'http://{sharevox_host}/speakers',
                headers=headers,
                timeout=10
            ) as response3:
                json2: list = await response3.json()
                for voice_info in json2:
                    voice_info["name"] = "SHAREVOX:" + voice_info["name"]
                    for style_info in voice_info["styles"]:
                        style_info["id"] += 2000

                json.extend(json2)
        except:
            print("SHAREVOX接続なし")

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
        await interaction.response.edit_message(view=HogeList(name=self.values[0], start=self.start, end=self.end))


class HogeList(discord.ui.View):
    def __init__(self, name=None, start=0, end=0):
        super().__init__()
        self.add_item(VoiceSelectView(default=name, id_list=voice_id_list[start:end], start=start, end=end))
        self.add_item(VoiceSelectView2(name=name, start=start))


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
        if 1000 <= id < 2000 and str(interaction.user.id) not in premium_user_list:
            embed = discord.Embed(
                title="**Error**",
                description=f"この音声はプレミアムプラン限定です。",
                color=discord.Colour.brand_red(),
            )
        else:
            await setdatabase(interaction.user.id, "voiceid", str(id))
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
        await ctx.send_followup("音声チャンネルに入っていないため操作できません。")
        return
    if ctx.guild.voice_client is not None and ctx.guild.voice_client.is_connected() and ctx.guild.id in vclist:
        del vclist[ctx.guild.id]
        await ctx.guild.voice_client.disconnect()
        embed = discord.Embed(
            title="Disconnect",
            color=discord.Colour.brand_red()
        )
        await ctx.send_followup(embed=embed)
        return
    else:
        if ctx.author.voice.channel.user_limit != 0 and ctx.author.voice.channel.user_limit <= len(
            ctx.author.voice.channel.members):
            embed = discord.Embed(
                title="Error",
                color=discord.Colour.brand_red(),
                description="満員で入れないのだ。"

            )

            await ctx.send_followup(embed=embed)
            return
        elif (ctx.author.voice.channel.permissions_for(ctx.me)).connect is False:
            embed = discord.Embed(
                title="Error",
                color=discord.Colour.brand_red(),
                description="接続の権限がないのだ。"
            )
            await ctx.send_followup(embed=embed)
            return
        elif ctx.me.timed_out is True:
            embed = discord.Embed(
                title="Error",
                color=discord.Colour.brand_red(),
                description="タイムアウトなのだ。"
            )
            await ctx.send_followup(embed=embed)
            return
        vclist[ctx.guild.id] = ctx.channel.id
        if is_lavalink:
            try:
                await ctx.author.voice.channel.connect(cls=wavelink.Player)
            except Exception as e:
                logger.error(e)
                await ctx.send_followup("現在起動中です。")
                return
        else:
            await ctx.author.voice.channel.connect()
        embed = discord.Embed(
            title="Connect",
            color=discord.Colour.brand_green(),
            description="tips: " + random.choice(tips_list)
        )
        if ctx.guild.id in premium_server_list:
            premium_server_list.remove(ctx.guild.id)
        if str(ctx.author.id) in premium_user_list or str(
            int(await getdatabase(ctx.guild.id, "premium_user", 0, "guild"))) in premium_user_list:
            embed.set_author(name="Premium")
            premium_server_list.append(ctx.guild.id)

        await ctx.send_followup(embed=embed)
        return


@bot.slash_command(description="色々な設定なのだ")
async def set(ctx, key: discord.Option(str, choices=[
    discord.OptionChoice(name="voice", value="voice"),
    discord.OptionChoice(name="speed", value="speed"),
    discord.OptionChoice(name="pitch", value="pitch"),
    discord.OptionChoice(name="premium_guild1", value="premium_guild1"),
    discord.OptionChoice(name="premium_guild2", value="premium_guild2"),
    discord.OptionChoice(name="premium_guild3", value="premium_guild3")], description="設定項目"),
              value: discord.Option(str, description="設定値", required=False)):
    await ctx.defer()
    if key == "voice":
        if value is None:
            test_pages = []
            for i in range(-(-len(voice_id_list) // 25)):
                name = None
                if i == 0:
                    name = "VOICEVOX:ずんだもん"
                else:
                    name = voice_id_list[i * 25]["name"]
                test_pages.append(pages.Page(content="ボイス・スタイルを選択してください。",
                                             custom_view=HogeList(name=name, start=i * 25, end=((i + 1) * 25))))
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
        if int(value) < 80:
            embed = discord.Embed(
                title="**Error**",
                description=f"80以上の数字で設定できます。",
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
    elif key == "premium_guild1" or key == "premium_guild2" or key == "premium_guild3":
        if str(ctx.author.id) not in premium_user_list:
            embed = discord.Embed(
                title="**Error**",
                description=f"プレミアム限定設定なのだ",
                color=discord.Colour.brand_red(),
            )
            await ctx.send_followup(embed=embed)
            return
        before_guild_id = await getdatabase(ctx.author.id, key, "0")
        if before_guild_id.replace(" ", "") != "0":
            await setdatabase(before_guild_id, "premium_user", "0", "guild")
        await setdatabase(ctx.author.id, key, value)
        await setdatabase(ctx.guild.id, "premium_user", str(ctx.author.id), "guild")
        embed = discord.Embed(
            title="**Changed Premium Guild**",
            description=f"{key}　のサーバーを サーバーid({ctx.guild.id}) に設定したのだ",
            color=discord.Colour.brand_green(),
        )
        await ctx.send_followup(embed=embed)


async def get_server_set_value(ctx: discord.AutocompleteContext):
    setting_type = ctx.options["key"]
    bool_settings = ["reademoji", "readname", "readurl", "readjoinleave", "readsan"]
    if setting_type in bool_settings:
        return ["off", "on"]
    elif setting_type == "lang":
        return ["ja", "ko"]
    else:
        return ["off"]


@bot.slash_command(description="サーバーの色々な設定なのだ", name="server-set",
                   default_member_permissions=discord.Permissions.manage_guild)
@default_permissions(manage_messages=True)
async def server_set(ctx, key: discord.Option(str, choices=[
    discord.OptionChoice(name="autojoin", value="autojoin"),
    discord.OptionChoice(name="reademoji"),
    discord.OptionChoice(name="readname"),
    discord.OptionChoice(name="readurl"),
    discord.OptionChoice(name="readjoinleave"),
    discord.OptionChoice(name="lang"),
    discord.OptionChoice(name="readsan")], description="設定項目"),
                     value: discord.Option(str, description="設定値", required=False,
                                           autocomplete=get_server_set_value), ):
    await ctx.defer()
    guild_id = ctx.guild_id
    if key == "autojoin":
        text_channel_id = ctx.channel_id
        if value == "off":
            setting_json = json.dumps({"text_channel_id": 1, "voice_channel_id": 1})
            await setdatabase(ctx.guild.id, "auto_join", setting_json, "guild")
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
        setting_json = json.dumps({"text_channel_id": text_channel_id, "voice_channel_id": voice_channel_id})
        await setdatabase(ctx.guild.id, "auto_join", setting_json, "guild")
        embed = discord.Embed(
            title="Changed AutoJoin",
            description="現在の接続している音声チャンネル、テキストチャンネルで設定したのだ。(OFFにする際はoffをvalueに設定して実行してください。)",
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
            embed.description = "絵文字の読み上げをオンにしました（デフォルト)"
            await setdatabase(ctx.guild.id, "is_reademoji", True, "guild")
        elif value == "off":
            embed.description = "絵文字の読み上げをオフにしました。"
            await setdatabase(ctx.guild.id, "is_reademoji", False, "guild")
        elif value == "on":
            embed.description = "絵文字の読み上げをオンにしました。"
            await setdatabase(ctx.guild.id, "is_reademoji", True, "guild")
        else:
            embed.title = "Error"
            embed.description = "on/offをvalueに指定してください。"
            embed.color = discord.Colour.brand_red()
        await ctx.send_followup(embed=embed)
    elif key == "readname":
        embed = discord.Embed(
            title="Changed ReadName",
            description="名前",
            color=discord.Colour.brand_green()
        )
        if value is None:
            embed.description = "名前の読み上げをオンにしました（デフォルト）"
            await setdatabase(ctx.guild.id, "is_readname", True, "guild")
        elif value == "off":
            embed.description = "名前の読み上げをオフにしました。"
            await setdatabase(ctx.guild.id, "is_readname", False, "guild")
        elif value == "on":
            embed.description = "名前の読み上げをオンにしました。"
            await setdatabase(ctx.guild.id, "is_readname", True, "guild")
        else:
            embed.title = "Error"
            embed.description = "on/offをvalueに指定してください。"
            embed.color = discord.Colour.brand_red()
        await ctx.send_followup(embed=embed)
    elif key == "readurl":
        embed = discord.Embed(
            title="Changed ReadName",
            description="名前",
            color=discord.Colour.brand_green()
        )
        if value is None:
            embed.description = "URLの読み上げをオンにしました（デフォルト）"
            await setdatabase(ctx.guild.id, "is_readurl", True, "guild")
        elif value == "off":
            embed.description = "URLの読み上げをオフにしました。"
            await setdatabase(ctx.guild.id, "is_readurl", False, "guild")
        elif value == "on":
            embed.description = "URLの読み上げをオンにしました。"
            await setdatabase(ctx.guild.id, "is_readurl", True, "guild")
        else:
            embed.title = "Error"
            embed.description = "on/offをvalueに指定してください。"
            embed.color = discord.Colour.brand_red()
        await ctx.send_followup(embed=embed)
    elif key == "readjoinleave":
        embed = discord.Embed(
            title="Changed ReadJoinLeave",
            description="名前",
            color=discord.Colour.brand_green()
        )
        if value is None:
            embed.description = "入退室の読み上げをオフにしました（デフォルト）"
            await setdatabase(ctx.guild.id, "is_readjoin", False, "guild")
        elif value == "off":
            embed.description = "入退室の読み上げをオフにしました。"
            await setdatabase(ctx.guild.id, "is_readjoin", False, "guild")
        elif value == "on":
            embed.description = "入退室の読み上げをオンにしました。"
            await setdatabase(ctx.guild.id, "is_readjoin", True, "guild")
        else:
            embed.title = "Error"
            embed.description = "on/offをvalueに指定してください。"
            embed.color = discord.Colour.brand_red()
        await ctx.send_followup(embed=embed)
    elif key == "lang":
        embed = discord.Embed(
            title="Changed Lang",
            description="名前",
            color=discord.Colour.brand_green()
        )
        if value is None:
            embed.description = "言語をjaにしました（デフォルト）(日本語:ja,　한국어:OFF)"
            await setdatabase(ctx.guild.id, "lang", "ja", "guild")
        elif value == "ja":
            embed.description = "言語をjaにしました"
            await setdatabase(ctx.guild.id, "lang", "ja", "guild")
        elif value == "ko":
            embed.description = "言語をkoにしました。"
            await setdatabase(ctx.guild.id, "lang", "ko", "guild")
        else:
            embed.title = "Error"
            embed.description = "言語をvalueに指定してください。(日本語:ja,　한국어:OFF)"
            embed.color = discord.Colour.brand_red()
        await ctx.send_followup(embed=embed)
    elif key == "readsan":
        embed = discord.Embed(
            title="Changed readsan",
            description="名前",
            color=discord.Colour.brand_green()
        )
        if value is None:
            embed.description = "さん付けをオフにしました（デフォルト）"
            await setdatabase(ctx.guild.id, "is_readsan", False, "guild")
        elif value == "off":
            embed.description = "さん付けをオフにしました"
            await setdatabase(ctx.guild.id, "is_readsan", False, "guild")
        elif value == "on":
            embed.description = "さん付けをオンにしました"
            await setdatabase(ctx.guild.id, "is_readsan", True, "guild")
        else:
            embed.title = "Error"
            embed.description = "on/offをvalueに指定してください。"
            embed.color = discord.Colour.brand_red()
        await ctx.send_followup(embed=embed)


@bot.slash_command(description="自分の声を変更できるのだ")
async def setvc(ctx, voiceid: discord.Option(required=False, input_type=int, description="指定しない場合は一覧が表示されます")):
    await ctx.defer()
    if (voiceid is None):
        test_pages = []
        for i in range(-(-len(voice_id_list) // 25)):
            if i == 0:
                name = "VOICEVOX:ずんだもん"
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


@bot.slash_command(description="ユーザーをプレミアム登録するのだ(modonly)", guild_ids=ManagerGuilds, name="stop")
async def stop_bot(ctx, message: discord.Option(input_type=str, description="カスタムメッセージ",
                                                default="ずんだもんの再起動を行います。数分程度ご利用いただけません。")):
    embed = discord.Embed(
        title="Notice",
        description=message,
        color=discord.Colour.red(),
    )
    savelist = []
    await ctx.defer()
    for server_id, text_ch_id in vclist.copy().items():
        guild = bot.get_guild(server_id)
        if guild.voice_client is None:
            continue
        savelist.append({"guild": server_id, "text_ch_id": text_ch_id, "voice_ch_id": guild.voice_client.channel.id})
        try:
            await guild.get_channel(text_ch_id).send(embed=embed)
        except:
            pass
    with open('bot_stop.json', 'wt') as f:
        json.dump(savelist, f, ensure_ascii=False)
    await ctx.send_followup("送信しました。", embed=embed)
    await bot.close()


async def auto_join():
    embed = discord.Embed(
        title="Notice",
        description="復帰しました。",
        color=discord.Colour.green(),
    )
    with open("bot_stop.json", ) as f:
        json_list = json.load(f)
        for server_json in json_list:
            guild = bot.get_guild(server_json["guild"])
            await guild.get_channel(server_json["voice_ch_id"]).connect(cls=wavelink.Player)
            await guild.get_channel(server_json["text_ch_id"]).send(embed=embed)


@bot.slash_command(description="辞書に単語を追加するのだ(全サーバー)", guild_ids=ManagerGuilds)
async def adddict(ctx, surface: discord.Option(input_type=str, description="辞書に登録する単語"),
                  pronunciation: discord.Option(input_type=str, description="カタカナでの読み方")):
    print(surface)
    """if (surface.startswith("<") and surface.endswith(">")) or emoji.is_emoji(surface):
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
        ('accent_type', accent_type),
        ('priority', priority)
    )
    headers = {'Content-Type': 'application/json', }
    response2 = requests.post(
        f'http://{host}:{port}/user_dict_word',
        headers=headers,
        params=params,
        timeout=(3.0, 10)
    )"""
    if surface == "":
        embed = discord.Embed(
            title="**Error**",
            description=f"空文字は登録できません。",
            color=discord.Colour.brand_red(),
        )
        await ctx.respond(embed=embed)
        return
    await update_private_dict(9686, surface, pronunciation)
    embed = discord.Embed(
        title="**Add Dict**",
        description=f"辞書に単語を登録しました。",
        color=discord.Colour.brand_green(),
    )
    embed.add_field(name="surface", value=surface)
    embed.add_field(name="pronunciation", value=pronunciation)
    await ctx.respond(embed=embed)
    # await updatedict()


@bot.slash_command(description="辞書から単語を削除するのだ(全サーバー)", guild_ids=ManagerGuilds)
async def deletedict(ctx, uuid: discord.Option(input_type=str, description="辞書から削除する単語", required=True)):
    headers = {'Content-Type': 'application/json', }
    embed = discord.Embed(
        title="**Add Dict**",
        description=f"辞書から単語を削除しました。",
        color=discord.Colour.brand_red(),
    )
    await delete_private_dict(9686, uuid)
    """for d_host in premium_host_list:
        response2 = requests.delete(
            f'http://{d_host}/user_dict_word/{uuid}',
            headers=headers,
            timeout=(3.0, 10)
        )
        embed.add_field(name="uuid", value=response2.text)"""

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
            await conn.execute(f'INSERT INTO {table} (id) VALUES ($1);', (str(userid)))
            rows = await conn.fetchrow(f'SELECT {id} from {table} where id = $1;', (str(userid)))
        await conn.execute(f'UPDATE {table} SET {id} = $1 WHERE "id" = $2;', value, str(userid))
        return rows[0]


async def text2wav(text, voiceid, is_premium: bool, speed="100", pitch="0"):
    global counter
    counter += 1
    if counter > 100:
        counter = 0
    filename = "temp" + str(counter) + ".wav"

    if voiceid >= 2000:
        target_host = f"{sharevox_host}"
        voiceid -= 2000
    elif voiceid >= 1000:
        target_host = f"{coeiroink_host}"
        voiceid -= 1000
    else:
        target_port = 50021
        global voiceapi_counter
        target_host = premium_host_list[voiceapi_counter]
        if voiceapi_counter + 1 >= len(premium_host_list):
            voiceapi_counter = 0
        else:
            voiceapi_counter += 1

    if voice_cache_dict.get(voiceid, {}).get(text):
        return voice_cache_dict.get(voiceid).get(text)
    if voice_cache_counter_dict.get(voiceid, None) is None:
        voice_cache_counter_dict[voiceid] = {}
        voice_cache_dict[voiceid] = {}
    voice_cache_counter_dict[voiceid][text] = voice_cache_counter_dict.get(voiceid, {}).get(text, 0) + 1
    if voice_cache_counter_dict[voiceid][text] > 10:
        filename = f"cache/{text}-{voiceid}.wav"
        voice_cache_dict[voiceid][text] = filename
    if await generate_wav(text, voiceid, filename, target_host=target_host,
                          is_premium=is_premium, speed=speed, pitch=pitch):
        return filename
    else:
        return "failed"


async def generate_wav(text, speaker=1, filepath='audio.wav', target_host='localhost', target_port=50021,
                       is_premium=False, speed="100", pitch="0"):
    params = (
        ('text', text),
        ('speaker', speaker),
    )
    len_limit = 80
    if is_premium:
        conn = premium_conn
        len_limit = 160
    else:
        conn = default_conn
    if int(speed) < 80:
        speed = 100

    # COEIROINKAPI用に対応
    if coeiroink_host == target_host:
        return await synthesis_coeiroink(target_host, conn, text, speed, pitch, speaker, filepath)
    else:
        return await synthesis(target_host, conn, params, speed, pitch, len_limit, speaker, filepath)


async def synthesis_coeiroink(target_host, conn, text, speed, pitch, speaker, filepath):
    try:
        text_json = {"text": text}
        async with aiohttp.ClientSession(connector_owner=False, connector=conn) as private_session:
            async with private_session.post(f'http://{target_host}/v1/estimate_prosody',
                                            json=text_json,
                                            timeout=30) as response1:
                if response1.status != 200:
                    return False
                headers = {'Content-Type': 'application/json', }
                query_json = {}
                query_json["speedScale"] = int(speed) / 100
                query_json["pitchScale"] = int(pitch) / 100
                query_json["styleId"] = speaker
                query_json["text"] = text
                query_json["prosodyDetail"] = (await response1.json())["detail"]
                query_json["volumeScale"] = 0.8
                query_json["intonationScale"] = 1
                query_json["prePhonemeLength"] = 0.1
                query_json["postPhonemeLength"] = 0.1
                query_json["outputSamplingRate"] = 24000

            async with private_session.post(f'http://{target_host}/v1/style_id_to_speaker_meta?styleId={speaker}',
                                            headers=headers,
                                            timeout=30) as response_speaker_res:
                query_json["speakerUuid"] = (await response_speaker_res.json())["speakerUuid"]

            async with private_session.post(f'http://{target_host}/v1/synthesis',
                                            headers=headers,
                                            json=query_json,
                                            timeout=30) as response2:
                if response2.status != 200:
                    return False

                try:
                    async with aiofiles.open(os.path.dirname(os.path.abspath(__file__)) + "/" + filepath,
                                             mode='wb') as f:
                        await f.write(await response2.read())
                    return True
                except ReadTimeout:
                    return False
    except:
        return False


async def synthesis(target_host, conn, params, speed, pitch, len_limit, speaker, filepath):
    try:
        async with aiohttp.ClientSession(connector_owner=False, connector=conn) as private_session:
            async with private_session.post(f'http://{target_host}/audio_query',
                                            params=params,
                                            timeout=30) as response1:
                if response1.status != 200:
                    return False
                headers = {'Content-Type': 'application/json', }
                query_json = await response1.json()
                query_json["speedScale"] = int(speed) / 100
                query_json["pitchScale"] = int(pitch) / 100

            if len(query_json["kana"]) > len_limit:
                print(query_json["kana"])
                ikaryaku = query_json["kana"][:len_limit]
                if ikaryaku[-1] == "'":
                    ikaryaku += "イカリャク"
                elif ikaryaku[-1] == "/" or ikaryaku[-1] == "、":
                    ikaryaku += "イカリャク'"
                elif ikaryaku.rfind("'") > ikaryaku.rfind('/') > ikaryaku.rfind('、'):
                    ikaryaku += "/イカリャク'"
                elif ikaryaku.rfind("'") > ikaryaku.rfind('、') > ikaryaku.rfind('/'):
                    ikaryaku += "/イカリャク'"
                else:
                    ikaryaku += "'/イカリャク'"
                print(ikaryaku)
                params_len = (
                    ('text', ikaryaku),
                    ('speaker', speaker),
                    ('is_kana', "true")
                )
                async with private_session.post(f'http://{target_host}/accent_phrases',
                                                params=params_len,
                                                timeout=30) as response3:
                    query_json["accent_phrases"] = await response3.json()

            async with private_session.post(f'http://{target_host}/synthesis',
                                            headers=headers,
                                            params=params,
                                            data=json.dumps(query_json),
                                            timeout=30) as response2:
                if response2.status != 200:
                    return False

                try:
                    async with aiofiles.open(os.path.dirname(os.path.abspath(__file__)) + "/" + filepath,
                                             mode='wb') as f:
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
    voice = message.guild.voice_client

    if voice is not None and message.channel.id == vclist[message.guild.id]:
        await yomiage(message.author, message.guild, message.content)
    else:
        return


async def yomiage(member, guild, text: str):
    if text == "zundamon!!stop":
        generating_guilds[guild.id].clear()
        print(f"クリアしました。guild: {guild.id}")
        return
    pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
    pattern_emoji = "\<.+?\>"
    pattern_voice = "\.v[0-9]*"
    pattern_spoiler = "\|\|.*?\|\|"
    voice_id = None
    is_premium = guild.id in premium_server_list
    if stripe.api_key is None:
        is_premium = True
    output = text
    if await getdatabase(guild.id, "is_readname", False, "guild"):
        if await getdatabase(member.guild.id, "is_readsan", False, "guild"):
            output = member.display_name + "さん " + output
        else:
            output = member.display_name + " " + output
    output = await henkan_private_dict(guild.id, output)
    output = await henkan_private_dict(9686, output)

    if guild.id in premium_server_list:
        if re.search(pattern_voice, text) is not None:
            cmd = re.search(pattern_voice, text).group()
            if re.search("[0-9]", cmd) is not None:
                voice_id = re.sub(r"\D", "", cmd)
        if re.search(pattern, text) is not None and await getdatabase(guild.id, "is_readurl", True,
                                                                      "guild"):
            url = re.search(pattern, text).group()
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url, timeout=5) as response:
                    html = await response.text()
                    title = re.findall('<title>(.*)</title>', html)[0]
                    if title is not None:
                        output = re.sub(pattern, "ユーアールエル " + title, output)
    if await getdatabase(guild.id, "is_reademoji", True, "guild"):
        output = emoji.demojize(output, language="ja")

    lang = await getdatabase(guild.id, "lang", "ja", "guild")
    output = re.sub(pattern_emoji, "", output)
    output = re.sub(pattern_voice, "", output)
    output = re.sub(pattern_spoiler, "", output)

    if lang == "ko":
        output = re.sub(pattern, "유알엘생략", output)
        if len(output) <= 0:
            return
        output = re.sub("w{4,100}", "ㅋ", output)
        if re.search("[^w]", output) is None:
            output = "ㅋ"

        if voice_id is None:
            voice_id = await getdatabase(member.id, "voiceid", 0)
        if len(output) > 50:
            if is_premium:
                if len(output) > 100:
                    output = output[:100] + "이하 약어"
            else:
                output = output[:50] + "이하 약어"
        output = korean2katakana(output)
        output = output.replace(" ", "")
    elif lang == "ja":
        output = re.sub(pattern, "ユーアールエル省略", output)
        output = romajitable.to_kana(output).katakana
        if len(output) <= 0:
            return
        output = re.sub("w{4,100}", "ワラ", output)
        if re.search("[^w]", output) is None:
            output = "ワラ"

        if voice_id is None:
            voice_id = await getdatabase(member.id, "voiceid", 0)
        if len(output) > 50:
            if is_premium:
                if len(output) > 100:
                    output = output[:100] + "以下略"
            else:
                output = output[:50] + "以下略"

    if len(output) <= 0:
        return
    print(output)

    try:
        generating_guilds.setdefault(guild.id, []).append(text)
        while guild.voice_client.is_playing() or generating_guilds[guild.id].index(text, 0) > 0:
            await asyncio.sleep(0.1)
        print(len(generating_guilds.get(guild.id)))
        print(text)
        filename = ""
        time_sta = time.time()
        done = True
        retry_count = 0
        while done and retry_count < 10:
            filename = await text2wav(output, int(voice_id), is_premium,
                                      speed=await getdatabase(member.id, "speed", 100),
                                      pitch=await getdatabase(member.id, "pitch", 0))
            if filename != "failed":
                done = False
            else:
                print("合成失敗")
                retry_count += 1
                if retry_count >= 3:
                    return

        time_end = time.time()
        tim = time_end - time_sta
        print("音声合成:" + str(tim))
        time_sta = time.time()

        if is_lavalink:
            source = (await wavelink.GenericTrack.search(os.path.dirname(os.path.abspath(__file__)) + "/" + filename))[
                0]
        else:
            source = await discord.FFmpegOpusAudio.from_probe(source=filename)

        time_end = time.time()
        tim = time_end - time_sta
        print("ソース:" + str(tim))
    finally:
        generating_guilds.get(guild.id, []).remove(text)
    if is_lavalink:
        await guild.voice_client.play(source)
    else:
        guild.voice_client.play(source)
    print("☑")


@bot.event
async def on_voice_state_update(member, before, after):
    voicestate = member.guild.voice_client
    if after.channel is not None and voicestate is None and member.bot is False and len(after.channel.members) == 1:
        if after.channel.user_limit != 0 and after.channel.user_limit <= len(after.channel.members):
            return
        elif (after.channel.permissions_for(member.guild.me)).connect is False:
            return
        elif member.guild.me.timed_out is True:
            return

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
            if str(member.id) in premium_user_list or str(
                int(await getdatabase(after.channel.guild.id, "premium_user", 0, "guild"))) in premium_user_list:
                embed.set_author(name="Premium")
                premium_server_list.append(after.channel.guild.id)
            await after.channel.guild.get_channel(autojoin["text_channel_id"]).send(embed=embed)
            try:
                await after.channel.connect(cls=wavelink.Player)
            except Exception as e:
                logger.error(e)
                logger.error("自動接続")
                return

        return

    if voicestate is None:
        return

    if (voicestate.client.user.id == member.id and after.channel is None) or (
        len(voicestate.channel.members) == 1 and (member.bot is False or voicestate.channel.members[0].bot)):
        await voicestate.disconnect()

        del vclist[voicestate.guild.id]
        return

    if after.channel is not None and after.channel.id == voicestate.channel.id and str(
        member.id) in premium_user_list and after.channel.guild.id not in premium_server_list:
        premium_server_list.append(after.channel.guild.id)
        embed = discord.Embed(
            title="Premium Mode",
            color=discord.Colour.yellow(),
            description="プレミアムモードに切り替わりました。"
        )
        try:
            await after.channel.guild.get_channel(vclist[after.channel.guild.id]).send(embed=embed)
        except:
            pass

    if await getdatabase(member.guild.id, "is_readjoin", False, "guild"):
        if after.channel is not None and before.channel is not None and after.channel.id == before.channel.id:
            return
        pattern_emoji = "\<.+?\>"
        name = member.display_name
        name = await henkan_private_dict(member.guild.id, name)
        name = await henkan_private_dict(9686, name)
        name = re.sub(pattern_emoji, "", name)
        name = emoji.replace_emoji(name, "")
        if await getdatabase(member.guild.id, "is_readsan", False, "guild"):
            name += "さん"
        if after.channel is not None and after.channel.id == voicestate.channel.id:
            await yomiage(member.guild.me, member.guild, f"{name}が入室したのだ、")
        elif before.channel.id == voicestate.channel.id:
            await yomiage(member.guild.me, member.guild, f"{name}が退出したのだ、")


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
    text = str(len(vclist)) + "/" + str(len(bot.guilds)) + " 読み上げ中"
    await bot.change_presence(activity=discord.CustomActivity(text))





@tasks.loop(hours=24)
async def premium_user_check_loop():
    if stripe.api_key is None:
        return
    global premium_user_list
    for d in stripe.Subscription.search(limit=100,
                                        query="status:'active' AND -metadata['discord_user_id']:null").auto_paging_iter():
        premium_user_list.append(d['metadata']['discord_user_id'])
    print(len(premium_user_list))

    with open('custom_emoji.json', 'wt') as f:
        json.dump(voice_cache_dict, f, ensure_ascii=False)
    voice_cache_dict.clear()
    voice_cache_counter_dict.clear()


@tasks.loop(minutes=1)
async def init_loop():
    await bot.change_presence(activity=discord.Game("起動中..."))
    global pool
    pool = await get_connection()

    global voice_cache_dict
    with open("./cache/voice_cache.json") as f:
        voice_cache_dict = json.load(f)

    await initdatabase()
    await init_voice_list()
    status_update_loop.start()
    premium_user_check_loop.start()
    bot.add_view(ActivateButtonView())
    bot.loop.create_task(connect_nodes())
    await updatedict()
    while datetime.datetime.now().minute % 10 != 0:
        await asyncio.sleep(0.1)


async def connect_nodes():
    """Connect to our Lavalink nodes."""
    await bot.wait_until_ready()
    if is_lavalink is False:
        print("lavalink無効")
        return
    print(len(wavelink.NodePool.nodes))
    node: wavelink.Node = wavelink.Node(uri='http://127.0.0.1:2333', password='youshallnotpass')
    await wavelink.NodePool.connect(client=bot, nodes=[node])
    print(len(wavelink.NodePool.nodes))


async def save_customemoji(custom_emoji, kana):
    with open("custom_emoji.json") as f:
        json_data = json.load(f)
    json_data.update({custom_emoji: {"ja": " " + kana + " "}})
    with open('custom_emoji.json', 'wt') as f:
        json.dump(json_data, f, ensure_ascii=False)
    importlib.reload(emoji)
    emoji.EMOJI_DATA.update(json_data)


async def updatedict():
    '''with open("custom_emoji.json", ) as f:
        json_data = json.load(f)
    emoji.EMOJI_DATA.update(json_data)'''

    headers = {'Content-Type': 'application/json', }
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'http://{host}/user_dict',
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


@bot.slash_command(description="辞書に単語を追加するのだ(サーバー個別)", name="adddict")
async def adddict_local(ctx, surface: discord.Option(input_type=str, description="辞書に登録する単語"),
                        pronunciation: discord.Option(input_type=str, description="カタカナでの読み方")):
    print(surface)
    if surface == "":
        embed = discord.Embed(
            title="**Error**",
            description=f"空文字は登録できません。",
            color=discord.Colour.brand_red(),
        )
        await ctx.respond(embed=embed)
        return
    await update_private_dict(ctx.guild.id, surface, pronunciation)
    embed = discord.Embed(
        title="**Add Dict**",
        description=f"辞書に単語を登録しました。",
        color=discord.Colour.brand_green(),
    )
    embed.add_field(name="surface", value=surface)
    embed.add_field(name="pronunciation", value=pronunciation)
    await ctx.respond(embed=embed)


@bot.slash_command(description="辞書から単語を削除するのだ(サーバー個別)", name="deletedict")
async def deletedict_local(ctx, surface: discord.Option(input_type=str, description="辞書から削除する単語")):
    print(surface)
    await delete_private_dict(ctx.guild.id, surface)
    embed = discord.Embed(
        title="**Delete Dict**",
        description=f"辞書から単語を削除しました。",
        color=discord.Colour.brand_red(),
    )
    embed.add_field(name="surface", value=surface)

    await ctx.respond(embed=embed)


@bot.slash_command(description="辞書の単語を表示するのだ(サーバー個別)", name="showdict")
async def showdict_local(ctx, ):
    embed = discord.Embed(
        title="**Show Dict**",
        description=f"辞書の内容を表示します。",
        color=discord.Colour.brand_green(),
    )
    try:
        json_file = discord.File(os.path.dirname(os.path.abspath(__file__)) + "/user_dict/" + f"{ctx.guild.id}.json")
    except:
        embed.description = "辞書は設定されていません。"
        await ctx.respond(embed=embed)
        return

    await ctx.respond(embed=embed, file=json_file)


async def henkan_private_dict(server_id, source):
    try:
        with open(os.path.dirname(os.path.abspath(__file__)) + "/user_dict/" + f"{server_id}.json", "r",
                  encoding='utf-8') as f:
            json_data = json.load(f)
    except:
        json_data = {}
    dict_data = sorted(json_data.keys(), key=len)
    dict_data.reverse()
    for k in dict_data:
        source = source.replace(k, json_data[k])
    return source


async def update_private_dict(server_id, source, kana):
    try:
        with open(os.path.dirname(os.path.abspath(__file__)) + "/user_dict/" + f"{server_id}.json", "r",
                  encoding='utf-8') as f:
            json_data = json.load(f)
    except:
        json_data = {}
    json_data[source] = kana
    sorted_json_data = json_data
    with open(os.path.dirname(os.path.abspath(__file__)) + "/user_dict/" + f"{server_id}.json", 'wt',
              encoding='utf-8') as f:
        json.dump(sorted_json_data, f, ensure_ascii=False)


async def delete_private_dict(server_id, source):
    try:
        with open(os.path.dirname(os.path.abspath(__file__)) + "/user_dict/" + f"{server_id}.json", "r",
                  encoding='utf-8') as f:
            json_data = json.load(f)
    except:
        json_data = {}
    json_data.pop(source)
    sorted_json_data = json_data
    with open(os.path.dirname(os.path.abspath(__file__)) + "/user_dict/" + f"{server_id}.json", 'wt',
              encoding='utf-8') as f:
        json.dump(sorted_json_data, f, ensure_ascii=False)


if __name__ == '__main__':
    bot.loop.create_task(init_loop())
    bot.run(token)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

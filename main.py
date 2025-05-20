# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import asyncio
import base64
import datetime
import json
import logging
import os
import random
import re
import sys
import time
import importlib
import urllib
import uuid
from dataclasses import dataclass

import aiofiles as aiofiles
import aiohttp
import asyncpg as asyncpg
import discord
import lavalink
import stripe
import websockets
from aiohttp import FormData, ClientTimeout
from discord import VoiceChannel
from discord.ext import tasks, pages
from lavalink import ClientError
from requests import ReadTimeout
from ko2kana import toKana
from dotenv import load_dotenv
import translators as ts
from watchfiles import watch, awatch

import emoji
import romajitable
import unicodedata

from LavalinkClient import LavalinkWavelink, LavalinkPlayer, Filters

load_dotenv()

token = os.environ.get("BOT_TOKEN", "BOT_TOKEN_HERE")
host = os.environ.get("VOICEVOX_HOST", "127.0.0.1:50021")
query_host = os.environ.get("VOICEVOX_QUERY_HOST", "192.168.10.8:50121")
premium_host_list = os.environ.get("VOICEVOX_HOSTS", "127.0.0.1:50021").split(",")
host_count = 0
stripe.api_key = os.environ.get("STRIPE_TOKEN", None)
is_lavalink = True
coeiroink_host = os.environ.get("COEIROINK_HOST", "127.0.0.1:50032")
sharevox_host = os.environ.get("SHAREVOX_HOST", "127.0.0.1:50025")
aivoice_host = os.environ.get("AIVOICE_HOST", "127.0.0.1:8001")
aivis_host = os.environ.get("AIVIS_HOST", "127.0.0.1:8001")
lavalink_host_list = os.environ.get("LAVALINK_HOST", "http://127.0.0.1:2333").split(",")
lavalink_uploader = os.environ.get("LAVALINK_UPLOADER", None)
use_lavalink_upload: bool = bool(os.getenv("USE_LAVALINK_UPLOAD", "True") == "True")
gpu_host = os.environ.get("GPU_HOST", host)
check_count_id = os.environ.get("CHECK_STATS_COUNT_ID", None)
DictChannel = 1057517276674400336
ManagerGuilds = [888020016660893726,864441028866080768]
intents = discord.Intents.none()
intents.message_content = True
intents.guilds = True
intents.voice_states = True
intents.guild_messages = True
is_use_gpu_server_time = False

vclist = {}
voice_select_dict = {}
premium_user_list = []
premium_server_list = []
premium_server_list_300 = []
premium_server_list_500 = []
premium_server_list_1000 = []
premium_guild_dict = {}
voice_cache_dict = {}
voice_cache_counter_dict = {}
generating_guild_set = set()
voice_generate_time_list = []
voice_generate_time_list_p = []
generating_guilds = set()
text_limit = 50
text_limit_100 = 100
text_limit_300 = 300
text_limit_500 = 500
text_limit_1000 = 1000
counter = 0
voiceapi_counter = 0
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "maikura123")
tips_list = ["/setvc　で自分の声を変更できます",
             "[プレミアムプラン](https://lenlino.com/?page_id=2510)(月100円～)あります",
             "[要望・不具合募集中](https://forms.gle/1TvbqzHRz6Q1vSfq9)",
             "使い方やコマンド一覧は[こちら](https://lenlino.com/?page_id=2171)",
             "音声が途切れる場合は音声チャンネル設定の地域を変更することで修正される場合があります",
             "ずんだもん(ノーマル、あまあま)、春日部つむぎ(ノーマル)、ちび式じい(ノーマル)のボイスはすべてのサーバーで高速なGPUによる生成を使用しています",
             "A.I.VOICEのボイスについては配信・録画は禁止されています",
             "プレミアムプランでは開発版のずんだもんαが利用できます。追加は[サポートサーバー](https://discord.gg/MWnnkbXSDJ)内から可能です",
             "/set　で自分の声、速度、ピッチを変更できます",
             "/server-set　で入退室、名前の読み上げ・自動接続などを設定できます",
             "/adddict　で辞書の登録が可能です",
             "コマンドが表示されない場合はDiscordアプリを最新版にすると治る場合があります",
             "VOICEVOXの音声はVOICEVOX:ずんだもんの表記を行えば配信等でも利用可能です。\n"
             "詳しくは[VOICEVOXホームページ](https://voicevox.hiroshiba.jp/term/)をご確認ください",
             "1000円プランではVOICEVOX APIの利用が可能です。詳しくは[こちら](https://lnetwork.jp/page-74/)",
             "[500円以上のプラン](https://lenlino.com/?page_id=2510)ではすべてのVOICEVOX音声が高速なGPUによる生成を利用しています",
             "A.I.VOICE 琴葉茜・葵に対応しました! /setvcコマンドより変更できます"]
USAGE_LIMIT_PRICE: int = int(os.getenv("USAGE_LIMIT_PRICE", 0))
GLOBAL_DICT_CHECK: bool = bool(os.getenv("GLOBAL_DICT_CHECK", "True") == "True")
BOT_NICKNAME = os.getenv("BOT_NICKNAME", "ずんだもんβ")
EEW_WEBHOOK_URL = os.getenv("EEW_WEBHOOK_URL", None)
voice_id_list = []
non_premium_user = []

generating_guilds = {}
pool = None

logger = logging.getLogger('discord')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter("%(message)s"))
handler = logging.FileHandler(filename=os.path.dirname(os.path.abspath(__file__)) + "/logs/"
                                       + f'discord-{"{:%Y-%m-%d-%H-%M}".format(datetime.datetime.now())}.log',
                              encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logging.basicConfig(handlers=[stream_handler, handler])

default_conn = None
default_gpu_conn = None
premium_conn = None

is_use_gpu_server_enabled: bool = bool(os.getenv("IS_GPU", "False") == "True")
is_use_gpu_server = False
gpu_start_time = datetime.datetime.strptime(os.getenv("START_TIME", "21:00"), "%H:%M").time()
gpu_end_time = datetime.datetime.strptime(os.getenv("END_TIME", "02:00"), "%H:%M").time()

user_dict_loc = os.getenv("DICT_LOC", os.path.dirname(os.path.abspath(__file__)) + "/user_dict")
member_cache_flags = discord.MemberCacheFlags.from_intents(intents=intents)
bot = discord.AutoShardedBot(intents=intents, chunk_guilds_at_startup=False, member_cache_flags=member_cache_flags)

class LavalinkVoiceClient(discord.VoiceProtocol):
    """
    This is the preferred way to handle external voice sending
    This client will be created via a cls in the connect method of the channel
    see the following documentation:
    https://discordpy.readthedocs.io/en/latest/api.html#voiceprotocol
    """

    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel
        self.guild_id = channel.guild.id
        self._destroyed = False
        self.filters = Filters()

        if not hasattr(self.client, 'lavalink'):
            # Instantiate a client if one doesn't exist.
            # We store it in `self.client` so that it may persist across cog reloads,
            # however this is not mandatory.
            self.client.lavalink = lavalink.Client(client.user.id)
            """Connect to our Lavalink nodes."""
            if is_lavalink is False:
                print("lavalink無効")
                return
            nodes = []
            for lavalink_host in lavalink_host_list:
                print(f'{lavalink_host.split(":")[0].replace("http://", "")} {int(lavalink_host.split(":")[1])}')
                self.client.lavalink.add_node(host=lavalink_host.split(":")[0].replace("http://", ""),
                                              port=int(lavalink_host.split(":")[1]),
                                              password='youshallnotpass', region='us', name='default-node')

        # Create a shortcut to the Lavalink client here.
        self.lavalink = self.client.lavalink

    @property
    def node(self):
        """Return the first node from the lavalink client's node_manager."""
        if hasattr(self, 'lavalink') and hasattr(self.lavalink, 'node_manager'):
            nodes = self.lavalink.node_manager.nodes
            return nodes[0] if nodes else None
        return None

    @property
    def guild(self):
        """Return the guild associated with this voice client."""
        return self.channel.guild if self.channel else None

    @property
    def playing(self):
        """Return whether the player is currently playing audio."""
        player = self.lavalink.player_manager.get(self.guild_id)
        return player is not None and player.is_playing

    @property
    def connected(self):
        """Return whether the client is connected to a voice channel."""
        player = self.lavalink.player_manager.get(self.guild_id)
        return player is not None and player.is_connected

    async def play(self, track, filters=None, **kwargs):
        """Play a track with the specified filters."""
        player = self.lavalink.player_manager.get(self.guild_id)
        if player is None:
            raise ValueError("No player available for this guild")

        # Apply filters if provided
        if filters is not None and hasattr(player, 'filters'):
            for filter_name, filter_instance in filters.__dict__.items():
                if hasattr(filter_instance, 'active') and filter_instance.active:
                    if not hasattr(player.filters, filter_name):
                        continue
                    player_filter = getattr(player.filters, filter_name)
                    if hasattr(filter_instance, 'to_dict'):
                        filter_dict = filter_instance.to_dict()
                        for key, value in filter_dict.items():
                            if hasattr(player_filter, key):
                                setattr(player_filter, key, value)
                    player_filter.active = True

            # Apply the filters to the player
            await player._apply_filters()

        # Play the track
        await player.play(track, **kwargs)
        return player

    async def on_voice_server_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
            't': 'VOICE_SERVER_UPDATE',
            'd': data
        }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        channel_id = data['channel_id']

        if not channel_id:
            await self._destroy()
            return

        self.channel = self.client.get_channel(int(channel_id))

        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
            't': 'VOICE_STATE_UPDATE',
            'd': data
        }

        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool, self_deaf: bool = False, self_mute: bool = False) -> None:
        """
        Connect the bot to the voice channel and create a player_manager
        if it doesn't exist yet.
        """
        # ensure there is a player_manager when creating a new voice_client
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel, self_mute=self_mute, self_deaf=self_deaf)

    async def disconnect(self, *, force: bool = False) -> None:
        """
        Handles the disconnect.
        Cleans up running player and leaves the voice client.
        """
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        # no need to disconnect if we are not connected
        if not force and not player.is_connected:
            return

        # None means disconnect
        await self.channel.guild.change_voice_state(channel=None)

        # update the channel_id of the player to None
        # this must be done because the on_voice_state_update that would set channel_id
        # to None doesn't get dispatched after the disconnect
        player.channel_id = None
        await self._destroy()

    async def _destroy(self):
        self.cleanup()

        if self._destroyed:
            # Idempotency handling, if `disconnect()` is called, the changed voice state
            # could cause this to run a second time.
            return

        self._destroyed = True

        try:
            await self.lavalink.player_manager.destroy(self.guild_id)
        except ClientError:
            pass

# Set up global exception handler
def global_exception_handler(exctype, value, traceback):
    sys.__excepthook__(exctype, value, traceback)

sys.excepthook = global_exception_handler

# Set up asyncio exception handler
def asyncio_exception_handler(loop, context):
    exception = context.get('exception')

async def connect_nodes():
    """Connect to our Lavalink nodes."""
    if is_lavalink is False:
        print("lavalink無効")
        return

    # Create a client instance
    if not hasattr(bot, 'lavalink'):
        bot.lavalink = lavalink.Client(bot.user.id)

    # Add nodes
    for lavalink_host in lavalink_host_list:
        host_text = lavalink_host.replace("http://", "")
        bot.lavalink.add_node(
            host=host_text.split(":")[0],
            port=int(host_text.split(":")[1]),
            password='youshallnotpass',
            region='us',
            name='default-node'
        )
    print(f"Node count: {len(bot.lavalink.nodes)}")

asyncio.get_event_loop().set_exception_handler(asyncio_exception_handler)


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
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS is_joinnotice boolean;')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS is_eew boolean;')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS is_translate boolean;')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS premium_user char(20);')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS lang char(2);')
        await conn.execute('ALTER TABLE guild ADD COLUMN IF NOT EXISTS mute_list bigint[];')


async def init_voice_list():
    headers = {'Content-Type': 'application/json', }
    json = []
    async with aiohttp.ClientSession() as session:

        async with session.get(
            f'http://{host}/speakers',
            headers=headers,
            timeout=10
        ) as response2:
            json2: list = await response2.json()
            for voice_info in json2:
                voice_info["name"] = "VOICEVOX:" + voice_info["name"]
            json.extend(json2)
        try:
            async with session.get(
                f'http://{aivoice_host}/speakers',
                headers=headers,
                timeout=10
            ) as response3:
                json2: list = await response3.json()
                for voice_info in json2:
                    voice_info["name"] = "A.I.VOICE:" + voice_info["name"]
                    for style_info in voice_info["styles"]:
                        style_info["id"] += 3000

                json.extend(json2)
        except:
            print("AIVOICE接続なし")
        try:
            async with session.get(
                f'http://{aivis_host}/speakers',
                headers=headers,
                timeout=10
            ) as response3:
                json2: list = await response3.json()
                for voice_info in json2:
                    voice_info["name"] = "Aivis:" + voice_info["name"]

                json.extend(json2)
        except:
            print("Aivis接続なし")
        try:
            async with session.get(
                f'http://{coeiroink_host}/speakers',
                headers=headers,
                timeout=10
            ) as response3:
                json2: list = await response3.json()
                for voice_info in json2:
                    voice_info["name"] = "COEIROINK:" + voice_info["name"]
                    for style_info in voice_info["styles"]:
                        style_info["id"] += 1000

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
        super().__init__(disable_on_timeout=True)
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
                description=f"この音声はプレミアムプラン限定です",
                color=discord.Colour.brand_red(),
            )
        else:
            await setdatabase(interaction.user.id, "voiceid", str(id))
        if 4000 > int(id) >= 3000:
            embed.description = f"**{self.name}({self.values[0]})** id:{id}に変更したのだ\n**A.I.VOICEは録音・配信での利用はできません**"
        #print(f"**{self.name}({self.values[0]})**")
        await interaction.response.send_message(embed=embed)
        await interaction.message.delete()


class ActivateButtonView(discord.ui.View):  # Create a class called MyView that subclasses discord.ui.View

    def __init__(self):
        super().__init__(timeout=None)  # timeout of the view must be set to None

    @discord.ui.button(label="Activate", style=discord.ButtonStyle.primary, custom_id="activate_button")
    async def activate_button_callback(self, button, interaction):
        await interaction.response.send_modal(ActivateModal(title="Activate"))

    @discord.ui.button(label="API TOKEN生成(1000円プラン用)", style=discord.ButtonStyle.primary,
                       custom_id="api_token_button")
    async def token_button_callback(self, button, interaction):
        await interaction.response.defer()
        embed = discord.Embed(title="Failed",
                              description="有効なプレミアムプランが存在しないかアクティベートされていません。")
        if str(interaction.user.id) not in premium_user_list:
            await interaction.followup.send(embeds=[embed], ephemeral=True)
            return
        target_subscription = []
        for subscription in stripe.Subscription.search(
            query=f"status:'active' AND metadata['discord_user_id']:'{interaction.user.id}'").auto_paging_iter():
            target_subscription.append(subscription)
            break
        for subscription in stripe.Subscription.search(
            query=f"status:'trialing' AND metadata['discord_user_id']:'{interaction.user.id}'").auto_paging_iter():
            target_subscription.append(subscription)
            break

        amount = target_subscription[0]["plan"]["amount"]

        if amount < 1000:
            embed.description = "1000円未満のプランのため発行が行えませんでした。"
            await interaction.followup.send(embeds=[embed], ephemeral=True)
            return
        subscription_id = target_subscription[0]["id"]
        api_token = uuid.uuid4()
        stripe.Subscription.modify(subscription_id, metadata={"voicevox_token": str(api_token)})
        embed.title = "Success"
        embed.description = "APIトークンを発行しました。利用方法などはホームページをご確認ください。"
        embed.add_field(name="Token", value=str(api_token))
        await interaction.followup.send(embeds=[embed], ephemeral=True)


class ActivateModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(
            discord.ui.InputText(label="メールアドレスを入力してください。(登録状況の参照にのみ使用されます。)"))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        mail = self.children[0].value
        customer: list = stripe.Customer.search(query=f"email: '{mail}'")["data"]
        if len(customer) == 0:
            embed = discord.Embed(title="fail", color=discord.Colour.brand_red())
            embed.description = "ユーザーが存在しません。"
            await interaction.followup.send(embeds=[embed], ephemeral=True)
            return
        customer_ids = []
        for customer_set in customer:
            customer_ids.append(customer_set["id"])
        target_subscription = []
        for subscription in stripe.Subscription.search(
            query=f"status:'active' AND metadata['discord_user_id']:null").auto_paging_iter():
            if subscription["customer"] in customer_ids:
                target_subscription.append(subscription)
                break
        if len(target_subscription) == 0:
            if str(interaction.user.id) in premium_user_list:
                embed = discord.Embed(title="success", color=discord.Colour.brand_green())
                embed.description = "すでにアクティベート済みです"
                await interaction.followup.send(embeds=[embed], ephemeral=True)
                return
            embed = discord.Embed(title="fail", color=discord.Colour.brand_red())
            embed.description = "有効なサブスクリプションが存在しません"
            await interaction.followup.send(embeds=[embed], ephemeral=True)
            return

        subscription_id = target_subscription[0]["id"]
        stripe.Subscription.modify(subscription_id, metadata={"discord_user_id": interaction.user.id})
        embed = discord.Embed(title="success", color=discord.Colour.brand_green())
        embed.description = "プレミアムプランへの登録が完了しました"
        amount = target_subscription[0]["plan"]["amount"]
        add_premium_user(interaction.user.id, amount)
        if amount == 100:
            await interaction.user.add_roles(discord.Object(1057789025731235860))
        elif amount == 300:
            await interaction.user.add_roles(discord.Object(1079176775675941064))
        elif amount == 500:
            await interaction.user.add_roles(discord.Object(1076650449534451792))
        elif amount == 1000:
            await interaction.user.add_roles(discord.Object(1057789043540242523))
        await interaction.followup.send(embeds=[embed], ephemeral=True)


def add_premium_user(user_id, amount):
    premium_user_list.append(str(user_id))
    if amount == 300:
        premium_server_list_300.append(str(user_id))
    elif amount == 500:
        premium_server_list_500.append(str(user_id))
    elif amount == 1000:
        premium_server_list_1000.append(str(user_id))


@bot.slash_command(description="読み上げを開始・終了するのだ")
async def vc(ctx):
    await ctx.defer()
    if ctx.author.voice is None:
        await ctx.send_followup("音声チャンネルに入っていないため操作できません。")
        return
    if ctx.guild.voice_client is not None and ctx.guild.voice_client.connected and ctx.guild.id in vclist:
        del vclist[ctx.guild.id]
        remove_premium_guild_dict(ctx.guild.id)
        await ctx.guild.voice_client.disconnect()
        embed = discord.Embed(
            title="Disconnect",
            color=discord.Colour.brand_red()
        )
        if await getdatabase(ctx.guild.id, "is_joinnotice", True, "guild"):
            await ctx.send_followup(embed=embed)
        else:
            await ctx.send_followup(embed=embed, delete_after=0)
        return
    else:
        guild_premium_user_id = int(await getdatabase(ctx.guild.id, "premium_user", 0, "guild"))
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
        elif (USAGE_LIMIT_PRICE > 0 and (
            await is_premium_check(ctx.author.id, USAGE_LIMIT_PRICE) or await is_premium_check(guild_premium_user_id,
                                                                                               USAGE_LIMIT_PRICE)) is False):
            embed = discord.Embed(
                title="Error",
                color=discord.Colour.brand_red(),
                description=f"{USAGE_LIMIT_PRICE}円以上のプランが必要です"
            )
            await ctx.send_followup(embed=embed)
            return

        if is_lavalink:
            try:
                # Check if already connected to a voice channel
                if ctx.guild.voice_client is not None:
                    logger.info("Already connected to a voice channel, using existing connection")
                    vclist[ctx.guild.id] = ctx.channel.id
                else:
                    await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
                    vclist[ctx.guild.id] = ctx.channel.id
            except Exception as e:
                logger.error(e)
                await ctx.send_followup("現在起動中です。")
                return
        else:
            await ctx.author.voice.channel.connect()
            vclist[ctx.guild.id] = ctx.channel.id
        if (ctx.author.voice.channel.permissions_for(ctx.guild.me)).deafen_members:
            await ctx.me.edit(deafen=True)
        embed = discord.Embed(
            title="Connect",
            color=discord.Colour.brand_green(),
            description="tips: " + random.choice(tips_list)
        )
        if ctx.guild.id in premium_server_list:
            premium_server_list.remove(ctx.guild.id)
        if str(ctx.author.id) in premium_user_list:
            premium_server_list.append(ctx.guild.id)
            embed.set_author(name=f"Premium {await add_premium_guild_dict(ctx.author.id, ctx.guild.id)}")
        elif str(
            int(guild_premium_user_id)) in premium_user_list:
            premium_server_list.append(ctx.guild.id)
            embed.set_author(name=f"Premium {await add_premium_guild_dict(ctx.guild.id, ctx.guild.id)}")
        if await getdatabase(ctx.guild.id, "is_joinnotice", True, "guild"):
            await ctx.send_followup(embed=embed)
        else:
            await ctx.send_followup(embed=embed, delete_after=0)
        return


async def add_premium_guild_dict(search_id: str, guild_id: str):
    if await is_premium_check(search_id, 1000):
        premium_guild_dict[guild_id] = 1000
        return 1000
    elif await is_premium_check(search_id, 500):
        premium_guild_dict[guild_id] = 500
        return 500
    elif await is_premium_check(search_id, 300):
        premium_guild_dict[guild_id] = 300
        return 300
    elif await is_premium_check(search_id, 100):
        premium_guild_dict[guild_id] = 100
        return 100
    return 0


def remove_premium_guild_dict(id: str):
    premium_guild_dict.pop(id, None)


@bot.slash_command(description="色々な設定なのだ")
async def set(ctx, key: discord.Option(str, choices=[
    discord.OptionChoice(name="ボイス(voice)", value="voice"),
    discord.OptionChoice(name="速度(speed)", value="speed"),
    discord.OptionChoice(name="ピッチ(pitch)", value="pitch"),
    discord.OptionChoice(name="プレミアム利用サーバー1(premium_guild1)", value="premium_guild1"),
    discord.OptionChoice(name="プレミアム利用サーバー2(premium_guild2)", value="premium_guild2"),
    discord.OptionChoice(name="プレミアム利用サーバー3(premium_guild3)", value="premium_guild3")],
                                       description="設定項目"),
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
            value = toLowerCase(value)
            if value.isdecimal() is False:
                embed = discord.Embed(
                    title="**Error**",
                    description=f"valueは数字なのだ",
                    color=discord.Colour.brand_red(),
                )
                print(f"**errorid**")
                await ctx.send_followup(embed=embed)
                return
            elif 2000 > int(value) >= 1000 and str(ctx.author.id) not in premium_user_list:
                embed = discord.Embed(
                    title="**Error**",
                    description=f"この音声はプレミアムプラン限定なのだ",
                    color=discord.Colour.brand_red(),
                )
                print(f"**errorvoice**")
                await ctx.send_followup(embed=embed)
                return

            name = ""
            for speaker in voice_id_list:
                if name != "":
                    break
                for style in speaker["styles"]:
                    if str(style["id"]) == value:
                        name = f"{speaker['name']}({style['name']})"
                        break
            if name == "":
                embed = discord.Embed(
                    title="**Error**",
                    description=f"存在しないボイスidです。[こちら](https://lenlino.com/?page_id=2171)のボイス一覧を参照"
                                f"または/setvcのみで実行することで選択方式で設定できます。",
                    color=discord.Colour.brand_red(),
                )
                print(f"**errorempyvoice**")
                await ctx.send_followup(embed=embed)
                return
            await setdatabase(ctx.author.id, "voiceid", value)
            embed = discord.Embed(
                title="**Changed Voice**",
                description=f"**{name}** id:{value}に変更したのだ",
                color=discord.Colour.brand_green(),
            )
            if 4000 > int(value) >= 3000:
                embed.description = f"**{name}** id:{value}に変更したのだ\n**A.I.VOICEは録音・配信での利用はできません**"
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
        if int(value) < 50:
            embed = discord.Embed(
                title="**Error**",
                description=f"50以上の数字で設定できます。",
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
        await setdatabase(str(ctx.author.id), key, str(ctx.guild.id))
        await setdatabase(str(ctx.guild.id), "premium_user", str(ctx.author.id), "guild")
        embed = discord.Embed(
            title="**Changed Premium Guild**",
            description=f"{key}　のサーバーを サーバーid({ctx.guild.id}) に設定したのだ",
            color=discord.Colour.brand_green(),
        )
        await ctx.send_followup(embed=embed)


async def get_server_set_value(ctx: discord.AutocompleteContext):
    setting_type = ctx.options["key"]
    bool_settings = ["reademoji", "readname", "readurl", "readjoinleave", "readsan", "joinnotice", "eew", "translate",
                     "autojoin"]
    if setting_type in bool_settings:
        return ["off", "on"]
    elif setting_type == "lang":
        return ["ja", "ko"]
    else:
        return ["off"]


@bot.slash_command(description="サーバーの色々な設定なのだ", name="server-set",
                   default_member_permissions=discord.Permissions.manage_guild)
@discord.commands.default_permissions(manage_messages=True)
async def server_set(ctx, key: discord.Option(str, choices=[
    discord.OptionChoice(name="自動接続(autojoin)", value="autojoin"),
    discord.OptionChoice(name="絵文字の読み上げ(reademoji)", value="reademoji"),
    discord.OptionChoice(name="名前の読み上げ(readname)", value="readname"),
    discord.OptionChoice(name="URLの読み上げ(readurl)", value="readurl"),
    discord.OptionChoice(name="入退室の読み上げ(readjoinleave)", value="readjoinleave"),
    discord.OptionChoice(name="言語(lang)", value="lang"),
    discord.OptionChoice(name="さん付け(readsan)", value="readsan"),
    discord.OptionChoice(name="参加退出表示(joinnotice)", value="joinnotice"),
    discord.OptionChoice(name="緊急地震速報通知(eew)", value="eew"),
    discord.OptionChoice(name="翻訳(translate)", value="translate")], description="設定項目"),
                     value: discord.Option(str, description="設定値", required=False,
                                           autocomplete=get_server_set_value), ):
    await ctx.defer()
    guild_id = ctx.guild_id
    if key == "autojoin":
        text_channel_id = ctx.channel_id
        if value == "off":
            await update_guild_setting(ctx.guild.id, "text_channel_id", 1)
            await update_guild_setting(ctx.guild.id, "voice_channel_id", 1)
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
        await update_guild_setting(ctx.guild.id, "text_channel_id", text_channel_id)
        await update_guild_setting(ctx.guild.id, "voice_channel_id", voice_channel_id)
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
    elif key == "joinnotice":
        embed = discord.Embed(
            title="Changed readsan",
            description="名前",
            color=discord.Colour.brand_green()
        )
        if value is None:
            embed.description = "参加退出表示をオンにしました（デフォルト）"
            await setdatabase(ctx.guild.id, "is_joinnotice", True, "guild")
        elif value == "off":
            embed.description = "参加退出表示をオフにしました"
            await setdatabase(ctx.guild.id, "is_joinnotice", False, "guild")
        elif value == "on":
            embed.description = "参加退出表示をオンにしました"
            await setdatabase(ctx.guild.id, "is_joinnotice", True, "guild")
        else:
            embed.title = "Error"
            embed.description = "on/offをvalueに指定してください。"
            embed.color = discord.Colour.brand_red()
        await ctx.send_followup(embed=embed)
    elif key == "translate":
        embed = discord.Embed(
            title="Changed translate",
            description="名前",
            color=discord.Colour.brand_green()
        )
        if value is None:
            embed.description = "自動翻訳をオフにしました（デフォルト）"
            await setdatabase(ctx.guild.id, "is_translate", False, "guild")
        elif value == "off":
            embed.description = "自動翻訳をオフにしました"
            await setdatabase(ctx.guild.id, "is_translate", False, "guild")
        elif value == "on":
            embed.description = "自動翻訳をオンにしました"
            await setdatabase(ctx.guild.id, "is_translate", True, "guild")
        else:
            embed.title = "Error"
            embed.description = "on/offをvalueに指定してください。"
            embed.color = discord.Colour.brand_red()
        await ctx.send_followup(embed=embed)
    elif key == "eew":
        embed = discord.Embed(
            title="Changed eew",
            description="名前",
            color=discord.Colour.brand_green()
        )
        if value is None:
            embed.description = "緊急地震速報通知をオンにしました（デフォルト）"
            await setdatabase(ctx.guild.id, "is_eew", True, "guild")
        elif value == "off":
            embed.description = "緊急地震速報通知をオフにしました"
            await setdatabase(ctx.guild.id, "is_eew", False, "guild")
        elif value == "on":
            embed.description = "緊急地震速報通知をオンにしました"
            await setdatabase(ctx.guild.id, "is_eew", True, "guild")
        else:
            embed.title = "Error"
            embed.description = "on/offをvalueに指定してください。"
            embed.color = discord.Colour.brand_red()
        await ctx.send_followup(embed=embed)


@bot.slash_command(description="自分の声を変更できるのだ")
async def setvc(ctx, voiceid: discord.Option(required=False, input_type=int,
                                             description="指定しない場合は一覧が表示されます"),
                speed: discord.Option(required=False, input_type=int, description="速度"),
                pitch: discord.Option(required=False, input_type=int, description="ピッチ")):
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

    elif 2000 > int(voiceid) >= 1000 and str(ctx.author.id) not in premium_user_list:
        embed = discord.Embed(
            title="**Error**",
            description=f"この音声はプレミアムプラン限定です。",
            color=discord.Colour.brand_red(),
        )
        print(f"**errorvoice**")
        await ctx.send_followup(embed=embed)
        return

    name = ""
    for speaker in voice_id_list:
        if name != "":
            break
        for style in speaker["styles"]:
            if str(style["id"]) == voiceid:
                name = f"{speaker['name']}({style['name']})"
                break
    if name == "":
        embed = discord.Embed(
            title="**Error**",
            description=f"存在しないボイスidです。[こちら](https://lenlino.com/?page_id=2171)のボイス一覧を参照"
                        f"または/setvcのみで実行することで選択方式で設定できます。",
            color=discord.Colour.brand_red(),
        )
        print(f"**errorempyvoice**")
        await ctx.send_followup(embed=embed)
        return
    await setdatabase(ctx.author.id, "voiceid", voiceid)
    embed = discord.Embed(
        title="**Changed voice**",
        description=f"**{name}** id:{voiceid}に変更したのだ",
        color=discord.Colour.brand_green(),
    )
    if 4000 > int(voiceid) >= 3000:
        embed.description = f"**{name}** id:{voiceid}に変更したのだ\n**A.I.VOICEは録音・配信での利用はできません**"
    #print(f"**{name}**")
    if speed is not None:
        if speed.isdecimal() is False:
            embed = discord.Embed(
                title="**Error**",
                description=f"speedは数字なのだ",
                color=discord.Colour.brand_red(),
            )
            await ctx.send_followup(embed=embed)
            return
        if int(speed) < 50:
            embed = discord.Embed(
                title="**Error**",
                description=f"speedは50以上の数字で設定できます。",
                color=discord.Colour.brand_red(),
            )
            await ctx.send_followup(embed=embed)
            return
        await setdatabase(ctx.author.id, "speed", speed)
        embed.description += f"\n読み上げ速度を {speed} に変更したのだ"
    if pitch is not None:
        try:
            int(pitch)
        except ValueError:
            embed = discord.Embed(
                title="**Error**",
                description=f"valueは数字なのだ",
                color=discord.Colour.brand_red(),
            )
            await ctx.send_followup(embed=embed)
            return

        await setdatabase(ctx.author.id, "pitch", pitch)
        embed.description += f"\n読み上げピッチを {pitch} に変更したのだ"
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
        description=f"Activateボタンを押してプランのアクティベートを行えます",
        color=discord.Colour.gold(),
    )
    await ctx.respond(embed=embed, view=ActivateButtonView())


@bot.slash_command(description="ユーザーをプレミアム登録するのだ(modonly)", guild_ids=ManagerGuilds, name="stop")
async def stop_bot(ctx, message: discord.Option(input_type=str, description="カスタムメッセージ",
                                                default="ずんだもんの再起動を行います。数分程度ご利用いただけません。")):
    await ctx.defer()
    await stop(message)
    await ctx.send_followup("送信しました。")
    await bot.close()


async def stop(message="ずんだもんの再起動を行います。数分程度ご利用いただけません。"):
    embed = discord.Embed(
        title="Notice",
        description=message,
        color=discord.Colour.red(),
    )
    logger.warn(f"停止中... {message}")
    await save_join_list()
    for server_id, text_ch_id in vclist.copy().items():
        guild = bot.get_guild(server_id)
        if guild.voice_client is None:
            continue
        try:
            await guild.get_channel(text_ch_id).send(embed=embed)
        except:
            pass
    await bot.close()
    sys.exit()

async def save_join_list():
    savelist = []
    for server_id, text_ch_id in vclist.copy().items():
        guild = bot.get_guild(server_id)
        if guild.voice_client is None:
            continue
        savelist.append({"guild": server_id, "text_ch_id": text_ch_id, "voice_ch_id": guild.voice_client.channel.id,
                         "is_premium": server_id in premium_guild_dict,
                         "premium_value": premium_guild_dict.get(server_id, 0)})
    with open(os.path.dirname(os.path.abspath(__file__)) + "/" + 'bot_stop.json', 'wt', encoding='utf-8') as f:
        json.dump(savelist, f, ensure_ascii=False)


async def auto_join():
    embed = discord.Embed(
        title="Notice",
        description="復帰しました",
        color=discord.Colour.green(),
    )
    with open(os.path.dirname(os.path.abspath(__file__)) + "/" + "bot_stop.json", encoding='utf-8') as f:
        json_list = json.load(f)
        print(json_list)
        for server_json in json_list:
            try:
                guild = bot.get_guild(server_json["guild"])
                await guild.get_channel(server_json["text_ch_id"]).send(embed=embed)
                voice_channel: VoiceChannel = guild.get_channel(server_json["voice_ch_id"])
                if len(voice_channel.voice_states) == 0:
                    continue
                # Check if already connected to a voice channel
                if guild.voice_client is not None:
                    logger.info(f"Already connected to a voice channel in guild {guild.id}, using existing connection")
                    vclist[guild.id] = server_json["text_ch_id"]
                else:
                    await voice_channel.connect(cls=LavalinkVoiceClient)
                    vclist[guild.id] = server_json["text_ch_id"]
                await guild.get_channel(server_json["text_ch_id"]).send(embed=embed)
            except Exception as e:
                logging.warning(f"Error: {e}")
                pass

            if server_json["is_premium"] is True and "premium_value" in server_json:
                premium_server_list.append(guild.id)
                premium_guild_dict[server_json["guild"]] = server_json["premium_value"]



@bot.slash_command(description="辞書に単語を追加するのだ(全サーバー)", guild_ids=ManagerGuilds)
async def addglobaldict(ctx, surface: discord.Option(input_type=str, description="辞書に登録する単語"),
                  pronunciation: discord.Option(input_type=str, description="カタカナでの読み方", required=False),
                audio_file: discord.Option(discord.Attachment, description="ボイス辞書用音声ファイル(wav, mp3)", required=False)):
    print(surface)
    if surface == "":
        embed = discord.Embed(
            title="**Error**",
            description=f"空文字は登録できません。",
            color=discord.Colour.brand_red(),
        )
        await ctx.respond(embed=embed)
        return
    if pronunciation is None and audio_file is None:
        embed = discord.Embed(
            title="**Error**",
            description=f"pronunciationまたはaudio_fileを指定してください",
            color=discord.Colour.brand_red(),
        )
        await ctx.respond(embed=embed)
        return
    # 音声ファイル辞書登録
    if audio_file is not None and False:
        if await is_premium_check(ctx.author.id, 100) is False:
            embed = discord.Embed(
                title="**Error**",
                description=f"ボイス辞書はプレミアム限定機能です。",
                color=discord.Colour.brand_red(),
            )
            await ctx.respond(embed=embed)
            return
        if audio_file.size > 10 * 1024 * 1024:
            embed = discord.Embed(
                title="**Error**",
                description=f"ファイルサイズは最大10MBまでです。",
                color=discord.Colour.brand_red(),
            )
            await ctx.respond(embed=embed)
            return
        print(audio_file.content_type)
        if str(audio_file.content_type) not in ["audio/x-wav"]:
            embed = discord.Embed(
                title="**Error**",
                description=f"wavファイルのみ利用できます。mp3などの場合はファイル変換サイトなどでwavに変換が必要です。",
                color=discord.Colour.brand_red(),
            )
            await ctx.respond(embed=embed)
            return

        file_name = f"{uuid.uuid4()}.wav"
        voice_path = (f"{user_dict_loc}/audio_data"
                      f"/9686")
        pronunciation = f"#%&${file_name}#%&$"
        os.makedirs(voice_path, exist_ok=True)
        if len(surface) > 50:
            embed = discord.Embed(
                title="**Error**",
                description=f"50文字以下の単語のみ登録できます。",
                color=discord.Colour.brand_red(),
            )
            await ctx.respond(embed=embed)
            return

        embed = discord.Embed(
            title="**Add Dict**",
            description=f"グローバル辞書に音声登録を申請しました。",
            color=discord.Colour.brand_green(),
        )
        embed.add_field(name="surface", value=surface)
        embed.add_field(name="pronunciation", value=audio_file.url)
        await ctx.respond(embed=embed, attachments=audio_file)
        return

    # await update_private_dict(9686, surface, pronunciation)
    embed = discord.Embed(
        title="**Add Dict**",
        description="グローバル辞書に単語登録を申請しました。",
        color=discord.Colour.brand_green(),
    )
    embed.add_field(name="surface", value=surface)
    embed.add_field(name="pronunciation", value=pronunciation)
    res = await ctx.respond(embed=embed)
    message = await res.original_response()
    await message.add_reaction("⭕")
    await message.add_reaction("❌")

    # await updatedict()


@bot.slash_command(description="辞書から単語を削除するのだ(全サーバー)", guild_ids=ManagerGuilds)
async def deleteglobaldict(ctx, uuid: discord.Option(input_type=str, description="辞書から削除する単語", required=True)):
    headers = {'Content-Type': 'application/json', }
    embed = discord.Embed(
        title="**Delete Dict**",
        description=f"グローバル辞書に単語削除を申請しました。",
        color=discord.Colour.brand_red(),
    )
    # await delete_private_dict(9686, uuid)
    """for d_host in premium_host_list:
        response2 = requests.delete(
            f'http://{d_host}/user_dict_word/{uuid}',
            headers=headers,
            timeout=(3.0, 10)
        )
        embed.add_field(name="uuid", value=response2.text)"""
    embed.add_field(name="削除する単語", value=uuid)

    res = await ctx.respond(embed=embed)
    message = await res.original_response()
    await message.add_reaction("⭕")
    await message.add_reaction("❌")

'''@bot.slash_command(description="目覚ましや時報などを設定できます")
async def alart(ctx, time: discord.Option(input_type=str, description="時刻 例 19:00", required=True),
                loop: discord.Option(input_type=discord.Option.input_type.boolean, description="ループ設定", required=False, default=True)):
    pass'''


async def get_connection():
    return await asyncpg.create_pool('postgresql://{user}:{password}@{host}:{port}/{dbname}'
    .format(
        user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, dbname=DB_NAME
    ))


async def getdatabase(userid, id, default=None, table="voice"):
    global pool
    if pool is None:
        logger.error("pool is None/get database")
        pool = await get_connection()
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
    global pool
    async with pool.acquire() as conn:
        rows = await conn.fetchrow(f'SELECT {id} from {table} where "id" = $1;', (str(userid)))
        if rows is None:
            await conn.execute(f'INSERT INTO {table} (id) VALUES ($1);', (str(userid)))
            rows = await conn.fetchrow(f'SELECT {id} from {table} where id = $1;', (str(userid)))
        await conn.execute(f'UPDATE {table} SET {id} = $1 WHERE "id" = $2;', value, str(userid))
        return rows[0]


async def text2wav(text, voiceid, is_premium: bool, speed="100", pitch="0", guild_id="0", is_self_upload=False):


    if voiceid >= 4000:
        target_host = f"{aivis_host}"
    elif voiceid >= 3000:
        target_host = f"{aivoice_host}"
        voiceid -= 3000
    elif voiceid >= 2000:
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

    filename = None
    '''if voice_cache_dict.get(voiceid, {}).get(text):
        path = os.path.dirname(os.path.abspath(__file__)) + "/" + voice_cache_dict.get(voiceid).get(text)
        if use_lavalink_upload:
            async with aiofiles.open(path,
                                     mode='rb') as f:
                return await f.read()
        else:
            return path
    if voice_cache_counter_dict.get(voiceid, None) is None:
        voice_cache_counter_dict[voiceid] = {}
        voice_cache_dict[voiceid] = {}
    voice_cache_counter_dict[voiceid][text] = voice_cache_counter_dict.get(voiceid, {}).get(text, 0) + 1

    if voice_cache_counter_dict[voiceid][text] > 50:
        filename = f"cache/{text}-{voiceid}.wav"
        voice_cache_dict[voiceid][text] = filename
        is_self_upload = True'''
    return await generate_wav(text, voiceid, filename, target_host=target_host,
                              is_premium=is_premium, speed=speed, pitch=pitch, guild_id=guild_id, is_self_upload=is_self_upload)


async def generate_wav(text, speaker=1, filepath=None, target_host='localhost', target_port=50021,
                       is_premium=False, speed="100", pitch="0", guild_id="0", is_self_upload=False):
    params = (
        ('text', text),
        ('speaker', speaker),
    )


    if int(speed) < 80:
        speed = 100

    global is_use_gpu_server
    global vclist_len
    use_gpu_server = False
    if is_use_gpu_server and (speaker == 3 or speaker == 1 or speaker == 42 or speaker == 8):
        use_gpu_server = True
    elif is_use_gpu_server and is_premium:
        if vclist_len >= 1500:
            use_gpu_server = True
        elif vclist_len >= 800 and await is_premium_check(guild_id, 300):
            use_gpu_server = True
        elif await is_premium_check(guild_id, 500):
            use_gpu_server = True
    len_limit = 80
    if is_premium:
        conn = premium_conn
        len_limit = 160
    elif is_use_gpu_server:
        conn = default_gpu_conn
    else:
        conn = default_conn

    # Generate audio data directly
    try:
        # Create a temporary file path if needed
        if filepath is None:
            filepath = "output/" + get_temp_name()

        # COEIROINKAPI用に対応
        if coeiroink_host == target_host or sharevox_host == target_host:
            # return await synthesis_coeiroink(target_host, conn, text, speed, pitch, speaker, filepath)
            return await synthesis(target_host, conn, params, speed, pitch, len_limit, speaker, filepath, volume=0.8)
        elif aivoice_host == target_host:
            return await synthesis(target_host, conn, params, speed, pitch, len_limit, speaker, filepath)
        elif aivis_host == target_host:
            return await synthesis(target_host, conn, params, speed, pitch, len_limit, speaker, filepath, query_host=target_host)
        else:
            return await synthesis(target_host, conn, params, speed, pitch, len_limit, speaker, filepath,
                                use_gpu_server=use_gpu_server, query_host=query_host, is_self_upload=is_self_upload)
    except Exception as e:
        logger.error(f"音声生成中にエラーが発生しました: {e}")
        return "failed"


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


def get_temp_name():
    global counter
    counter += 1
    if counter > 500:
        counter = 0
    return "temp" + str(counter) + ".wav"


async def synthesis(target_host, conn, params, speed, pitch, len_limit, speaker, filepath=None, volume=1.0,
                    use_gpu_server=False, query_host=None, is_self_upload=False):
    try:
        global is_use_gpu_server
        if query_host is None:
            query_host = target_host
        if filepath is not None:
            dir = os.path.dirname(os.path.abspath(__file__)) + "/" + filepath
        async with aiohttp.ClientSession(connector_owner=False, connector=conn, timeout=ClientTimeout(connect=5)) as private_session:
            async with private_session.post(f'http://{query_host}/audio_query',
                                            params=params,
                                            timeout=ClientTimeout(total=5)) as response1:
                if response1.status != 200:
                    logger.warning(await response1.json())
                    return "failed"

                # 同一IPで出力
                if response1.headers.get("x-address"):
                    target_host = response1.headers.get("x-address")

                #AIVOICEは１回で終了
                if target_host == aivoice_host:

                    try:
                        if use_lavalink_upload:
                            return await response1.read()
                        if filepath is None:
                            dir = os.path.dirname(os.path.abspath(__file__)) + "/output/" + get_temp_name()
                        async with aiofiles.open(dir,
                                                 mode='wb') as f:
                            await f.write(await response1.read())
                        return dir
                    except ReadTimeout:
                        return "failed"

                headers = {'Content-Type': 'application/json', }
                query_json = await response1.json()
                query_json["speedScale"] = int(speed) / 100
                query_json["pitchScale"] = int(pitch) / 100
                query_json["outputStereo"] = False
                query_json["volumeScale"] = volume

                '''print(query_json)

                for phrase in query_json["accent_phrases"]:
                    for mora in phrase["moras"]:
                        mora["vowel_length"] /= 2
                        if mora["consonant_length"] is not None:
                            mora["consonant_length"] /= 2

                print(query_json)'''

            if len(query_json["kana"]) > len_limit:
                #print(query_json["kana"])
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
                #print(ikaryaku)
                params_len = (
                    ('text', ikaryaku),
                    ('speaker', speaker),
                    ('is_kana', "true")
                )
                async with private_session.post(f'http://{query_host}/accent_phrases',
                                                params=params_len) as response3:
                    query_json["accent_phrases"] = await response3.json()

            if use_gpu_server and is_use_gpu_server:
                target_host = gpu_host
            async with private_session.post(f'http://{target_host}/synthesis',
                                            headers=headers,
                                            params=params,
                                            data=json.dumps(query_json)) as response2:
                if response2.status != 200:
                    '''if use_gpu_server:
                        is_use_gpu_server = False'''
                    logger.warning(await response2.json())
                    return "failed"
                response2_data = await response2.read()

            try:
                if lavalink_uploader is None:
                    if use_lavalink_upload:
                        return response2_data
                    if filepath is None:
                        dir = os.path.dirname(os.path.abspath(__file__)) + "/output/" + get_temp_name()
                    async with aiofiles.open(dir,
                                             mode='wb') as f:
                        await f.write(response2_data)
                else:
                    #ugokanaiyo
                    formdata = FormData()
                    formdata.add_field('file', await response2.read())
                    async with private_session.post(f'http://{lavalink_uploader}/send_wav',
                                                    data=formdata) as response3:
                        res_text = await response3.text()
                        if res_text != "error":
                            return res_text
                        else:
                            return "failed"
                return dir
            except ReadTimeout:
                return "failed"
    except:
        '''if use_gpu_server:
            is_use_gpu_server = False'''
        print(f"failed ({target_host}: {params} {speaker} use_gpu: {use_gpu_server})")
        import traceback
        traceback.print_exc()
        return "failed"


@bot.event
async def on_ready():
    print("起動しました")


@bot.event
async def on_message(message):
    voice = message.guild.voice_client
    if voice and (message.channel.id == vclist.get(message.guild.id) or message.channel.id == voice.channel.id):
        await add_yomiage_queue(message.author, message.guild, message.content)

@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    # Log the error
    logger.error(f"Application command error: {error}")

    # Send a user-friendly error message
    try:
        await ctx.respond("コマンドの実行中にエラーが発生しました。しばらく経ってからもう一度お試しください。", ephemeral=True)
    except discord.errors.InteractionResponded:
        try:
            await ctx.send_followup("コマンドの実行中にエラーが発生しました。しばらく経ってからもう一度お試しください。", ephemeral=True)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

@dataclass
class YomiageQueue:
    member: discord.member
    guild: discord.guild
    text: str
    no_read_name: bool = False


yomiage_queue = {}

async def add_yomiage_queue(member, guild, text: str, no_read_name=False):
    yomiage_queue.setdefault(guild.id, []).append(YomiageQueue(member, guild, text, no_read_name))
    if len(yomiage_queue.get(guild.id, [])) == 1:
        queue = yomiage_queue.get(guild.id, [])[0]
        await yomiage(queue.member, queue.guild, queue.text, queue.no_read_name)


async def yomiage(member, guild, text: str, no_read_name=False):
    is_premium = False
    time_sta = time.time()
    source = None
    try:
        if text == "zundamon!!stop":
            del yomiage_queue[guild.id]
            print(f"クリアしました。guild: {guild.id}")
            return
        elif text.startswith("!") or text.startswith("！"):
            return
        elif member.id in await getdatabase(guild.id, "mute_list", [], "guild"):
            return
        pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-@]+"
        pattern_emoji = "\<.+?\>"

        pattern_spoiler = "\|\|.*?\|\|"
        voice_id = None
        is_premium = guild.id in premium_server_list
        if stripe.api_key is None:
            is_premium = True
        output = text
        output = re.sub("\n", "", output)

        if output == "":
            return

        if await getdatabase(guild.id, "is_readname", False, "guild") and not no_read_name:
            if await getdatabase(member.guild.id, "is_readsan", False, "guild"):
                output = member.display_name + "さん " + output
            else:
                output = member.display_name + " " + output

        if is_premium:
            '''if len(output) > text_limit_300 and guild.id in premium_server_list_300:
                output = output[:(text_limit_300 + 50)]
            elif len(output) > text_limit_500 and guild.id in premium_server_list_500:
                output = output[:(text_limit_500 + 50)]
            elif len(output) > text_limit_1000 and guild.id in premium_server_list_1000:
                output = output[:(text_limit_1000 + 50)]
            else:
                output = output[:(text_limit_100 + 50)]'''
            output = output[:(text_limit_100 + 50)]
        else:
            output = output[:100]

        lang = await getdatabase(guild.id, "lang", "ja", "guild")

        pattern_voice = "\.v[0-9]*"
        if guild.id in premium_server_list:

            if re.search(pattern_voice, text) is not None:
                cmd = re.search(pattern_voice, text).group()
                if re.search("[0-9]", cmd) is not None:
                    voice_id = re.sub(r"\D", "", cmd)
            '''if re.search(pattern, text) is not None and await getdatabase(guild.id, "is_readurl", True,
                                                                          "guild"):
                url = re.search(pattern, text).group()
                async with aiohttp.ClientSession() as session:
                    async with session.get(url=url, timeout=5) as response:
                        html = await response.text()
                        title = re.findall('<title>(.*)</title>', html)[0]
                        if title is not None:
                            if len(re.findall('<img(.*)>', html)) != 1:
                                output = re.sub(pattern, "ユーアールエル " + title, output)
                            else:
                                output = re.sub(pattern, "ユーアールエル画像省略", output)'''

        if voice_id is None:
            voice_id = await getdatabase(member.id, "voiceid", 0)

        if lang == "ko":
            output = re.sub(pattern, "유알엘생략", output)
        elif lang == "ja":
            output = re.sub(pattern, "ユーアールエル省略", output)

        output = await henkan_private_dict(guild.id, output)
        output = await henkan_private_dict(9686, output)

        if await getdatabase(guild.id, "is_reademoji", True, "guild"):
            output = emoji.demojize(output, language="ja")

        output = re.sub(pattern_emoji, "", output)
        output = re.sub(pattern_voice, "", output)
        output = re.sub(pattern_spoiler, "", output)

        if len(output) <= 0:
            return

        split_output = output.split("#%&$")

        if is_premium:
            for i in range(len(split_output)):
                split_text = split_output[i].replace("/", "")
                voice_path = (f"{user_dict_loc}/audio_data"
                              f"/{guild.id}/{split_text}")
                voice_global_path = (f"{user_dict_loc}/audio_data"
                              f"/9686/{split_text}")
                if split_text.endswith(".wav") and os.path.isfile(voice_path):
                    split_output[i] = split_text
                elif split_text.endswith(".wav") and os.path.isfile(voice_global_path):
                    split_output[i] = f"global_{split_text}"
                else:
                    split_output[i] = await honyaku_and_ikaryaku(lang, split_output[i], voice_id, member.id, guild.id,
                                                                 is_premium)
        else:
            split_output = [await honyaku_and_ikaryaku(lang, output, voice_id, member.id, guild.id, is_premium)]

        if guild.voice_client is None:
            return
        #print(output)
        filename = ""

        done = True
        retry_count = 0
        output_list = []
        if len(split_output) > 1:
            output_list = split_output
        elif len(split_output[0]) > 10000:
            for i in range(0, len(split_output[0]), 100):
                output_list.append(split_output[0][i:i + 100])
        else:
            output_list.append(split_output[0])

        speed = await getdatabase(member.id, "speed", 100)
        pitch = await getdatabase(member.id, "pitch", 0)

        wav_list = []
        is_self_gen = len(output_list) > 1
        for gen_text in output_list:
            if gen_text == "":
                continue
            if gen_text.endswith(".wav"):
                if gen_text.startswith("global_"):
                    filename = (f"{user_dict_loc}/audio_data"
                                f"/9686/{gen_text}")
                else:
                    filename = (f"{user_dict_loc}/audio_data"
                                f"/{guild.id}/{gen_text}")
                if use_lavalink_upload:
                    async with aiofiles.open(filename,
                                             mode='rb') as f:
                        filename = await f.read()
                        wav_list.append(filename)
                else:
                    wav_list.append(filename)
                continue

            if not is_premium and check_count_id is not None:
                logger.error(f"{guild.id} {voice_id} {await is_premium_check(guild.id, 100)} "
                             f"{await is_premium_check(member.id, 100)}")

            filename = await text2wav(gen_text, int(voice_id), is_premium,
                                      speed="100",
                                      pitch="0", guild_id=guild.id, is_self_upload=is_self_gen)
            if filename != "failed":
                wav_list.append(filename)
                continue
            else:
                logger.error("合成失敗")
                return
        if len(wav_list) > 1:
            filename = await connect_waves(wave_list=wav_list)
            if filename is None:
                logger.error("結合失敗")
                return

        if is_lavalink:
            try:
                player: lavalink.Player = guild.voice_client
                source_serch = await asyncio.wait_for(
                    LavalinkWavelink.Playable.search(filename, source=None, node=player.node),
                    timeout=5.0  # タイムアウトを5秒に設定
                )
            except asyncio.TimeoutError:
                logger.error("検索がタイムアウトしました！")
                return
            except Exception as e:
                logger.error(f"エラーが発生しました: {e}")
                return
            if len(source_serch) == 0:
                logger.error("結果が見つかりませんでした。")
                return
            source = source_serch[0]
        else:
            source = await discord.FFmpegOpusAudio.from_probe(source=filename)


    except Exception as e:
        logger.error(e)
        logger.error(f"{output} {voice_id}")
    else:
        if source is None:
            print(f"source is None/ {output}")
            return
        # 時間測定
        time_end = time.time()
        tim = time_end - time_sta
        if is_premium:
            premium_text = "P"
            voice_generate_time_list_p.append(tim)
        else:
            premium_text = ""
            voice_generate_time_list.append(tim)
        if tim > 3:
            print(f"{premium_text} v:{voice_id} s:{speed} p:{pitch} t:{str(tim)} text:{output}")

        if is_lavalink:
            player = guild.voice_client
            filters = player.filters
            speed = float(float(speed) / 100)
            pitch = float(float(pitch) / 100) + 1
            filters.timescale.set(speed=speed, pitch=pitch)
            loop = 0
            while player.playing is True:
                await asyncio.sleep(1)
                loop += 1
                if loop > 10:
                    print(f"player: {player.ping} ms {player.position} s {player.paused}")
                    print(f"player: {player.connected} {output} {guild.id}")
                    logger.info(loop)
                if loop > 30:
                    logger.info("再接続")
                    channel = player.channel
                    await player.disconnect()
                    await asyncio.sleep(3)
                    if is_lavalink:
                        try:
                            await channel.connect(cls=LavalinkVoiceClient)
                        except Exception as e:
                            logger.error(e)
                            return
                    else:
                        await channel.connect()
                    logger.info("再接続完了")
                    break
            await player.play(source, filters=filters)
        else:
            guild.voice_client.play(source)
    finally:
        yomiage_queue.get(guild.id, []).pop(0)
        if len(yomiage_queue.get(guild.id, [])) > 0:
            queue = yomiage_queue.get(guild.id, [])[0]
            await yomiage(queue.member, queue.guild, queue.text, queue.no_read_name)
        else:
            del yomiage_queue[guild.id]


async def connect_waves(wave_list):
    bytes_list = []
    if use_lavalink_upload:
        for wave_dir in wave_list:
            bytes_list.append(base64.b64encode(wave_dir).decode('utf-8'))

    else:
        for wave_dir in wave_list:
            async with aiofiles.open(wave_dir,
                                 mode='rb') as f:
                bytes_list.append(base64.b64encode(await f.read()).decode('utf-8'))

    try:
        headers = {'Content-Type': 'application/json', }
        async with aiohttp.ClientSession(connector_owner=False, connector=premium_conn) as private_session:
            async with private_session.post(f'http://{host}/connect_waves',
                                            data=json.dumps(bytes_list), headers=headers,
                                            timeout=10) as response1:
                if response1.status != 200:
                    print((await response1.json())["detail"])
                    return None
                res_data = await response1.read()

        if use_lavalink_upload:
            return res_data
        filename = get_temp_name()
        try:
            dir = os.path.dirname(os.path.abspath(__file__)) + "/output/" + filename
            async with aiofiles.open(dir,
                                     mode='wb') as f:
                await f.write(res_data)
            return dir
        except ReadTimeout:
            return None

    except Exception as ex:
        logger.error(ex)
        return None

def remove_symbols_except_last(text):
    # 非記号（アルファベット、数字、空白、ひらがな、カタカナ、漢字）を全て許可
    symbols = re.findall(r'[^\w\sぁ-んァ-ヶ一-龥]', text)

    if symbols:
        # 最後の記号を取得
        last_symbol = symbols[-1]
        # 最後の記号以外の記号をすべて削除
        text = re.sub(r'[^\w\sぁ-んァ-ヶ一-龥]', '', text)
        # 最後の記号を末尾に追加
        text = text + last_symbol

    return text



async def honyaku_and_ikaryaku(lang, output, voice_id, member_id, guild_id, is_premium):
    if lang == "ko":

        if len(output) <= 0:
            return ""
        output = re.sub("w{4,100}", "ㅋ", output)
        if re.search("[^w]", output) is None:
            output = "ㅋ"

        if voice_id is None:
            voice_id = await getdatabase(member_id, "voiceid", 0)
        if len(output) > 50:
            if is_premium:
                if len(output) > 100:
                    output = output[:100] + "이하 약어"
            else:
                output = output[:50] + "이하 약어"
        output = toKana(output)
        output = output.replace(" ", "")
    elif lang == "ja":
        if (await is_premium_check(guild_id, 300) and re.match("[ぁ-んァ-ヶー一-龯]", output) is None
            and await getdatabase(guild_id, "is_translate", False, "guild")):
            #print(output)
            output = ts.translate_text(output, to_language="ja")
            #print("翻訳")

        output = (await romajitable.to_kana(output)).katakana
        if len(output) <= 0:
            return ""
        output = re.sub("w{4,100}", "ワラ", output)
        if re.search("[^w]", output) is None:
            output = "ワラ"


        if is_premium:
            '''if len(output) > text_limit_300 and guild.id in premium_server_list_300:
                output = output[:(text_limit_300)] + "以下略"
            elif len(output) > text_limit_500 and guild.id in premium_server_list_500:
                output = output[:(text_limit_500)] + "以下略"
            elif len(output) > text_limit_1000 and guild.id in premium_server_list_1000:
                output = output[:(text_limit_1000)] + "以下略"
            elif len(output) > text_limit_1000 and guild.id in premium_server_list:'''
            if len(output) > text_limit_100:
                output = output[:(text_limit_100)] + "以下略"
        else:
            if len(output) > 50:
                output = output[:50] + "以下略"

    if 4000 > int(voice_id) >= 3000:
        output = remove_symbols_except_last(output)

    return output



@bot.event
async def on_voice_state_update(member, before, after):
    voicestate = member.guild.voice_client
    if after.channel is not None and voicestate is None and member.bot is False and (len(after.channel.members) == 1
                                                                                     or after.channel.guild.id in vclist.keys()):
        if after.channel.user_limit != 0 and after.channel.user_limit <= len(after.channel.members):
            return
        elif (after.channel.permissions_for(member.guild.me)).connect is False:
            return
        elif member.guild.me.timed_out is True:
            return

        json_str = await get_guild_setting(after.channel.guild.id)
        if json_str is None:
            return
        autojoin = json_str
        if int(autojoin.get("voice_channel_id", 1)) == int(after.channel.id):

            guild_premium_user_id = int(await getdatabase(after.channel.guild.id, "premium_user", 0, "guild"))
            #print(guild_premium_user_id)
            #print(type(guild_premium_user_id))
            if (USAGE_LIMIT_PRICE > 0 and (
                await is_premium_check(member.id, USAGE_LIMIT_PRICE) or await is_premium_check(guild_premium_user_id,
                                                                                               USAGE_LIMIT_PRICE)) is False):
                return
            embed = discord.Embed(
                title="Connect",
                color=discord.Colour.brand_green(),
                description="tips: " + random.choice(tips_list)
            )
            if after.channel.guild.id in premium_server_list:
                premium_server_list.remove(after.channel.guild.id)
            if str(member.id) in premium_user_list:
                embed.set_author(name=f"Premium {await add_premium_guild_dict(member.id, after.channel.guild.id)}")
                premium_server_list.append(after.channel.guild.id)
            elif str(
                int(guild_premium_user_id)) in premium_user_list:
                embed.set_author(
                    name=f"Premium {await add_premium_guild_dict(guild_premium_user_id, after.channel.guild.id)}")
                premium_server_list.append(after.channel.guild.id)

            try:
                # 時間開けないと２重接続？
                await asyncio.sleep(1)
                # Check again if the bot is already connected to a voice channel
                if after.channel.guild.voice_client is not None:
                    logger.info("Already connected to a voice channel, skipping connection attempt")
                    return
                await after.channel.guild.get_channel(after.channel.id).connect(cls=LavalinkVoiceClient)
                vclist[after.channel.guild.id] = autojoin["text_channel_id"]
                if (after.channel.permissions_for(after.channel.guild.me)).deafen_members:
                    await after.channel.guild.me.edit(deafen=True)
                if await getdatabase(after.channel.guild.id, "is_joinnotice", True, "guild"):
                    await after.channel.guild.get_channel(autojoin["text_channel_id"]).send(embed=embed)
            except Exception as e:
                logger.error(e)
                logger.error("自動接続")
                return


        return

    if voicestate is None:
        return

    if bot.user.id == member.id:
        return

    if (bot.user.id == member.id and after.channel is None) or (member.bot is not True and is_bot_only(voicestate.channel)):
        await voicestate.disconnect()

        del vclist[voicestate.guild.id]
        remove_premium_guild_dict(voicestate.guild.id)
        return

    if after.channel is not None and after.channel.id == voicestate.channel.id and str(
        member.id) in premium_user_list and after.channel.guild.id not in premium_server_list:
        premium_server_list.append(after.channel.guild.id)
        await add_premium_guild_dict(member.id, after.channel.guild.id)
        embed = discord.Embed(
            title="Premium Mode",
            color=discord.Colour.yellow(),
            description="プレミアムモードに切り替わりました。"
        )
        try:
            await after.channel.guild.get_channel(vclist[after.channel.guild.id]).send(embed=embed)
        except Exception as e:
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
            await add_yomiage_queue(member, member.guild, f"{name}が入室したのだ、", no_read_name=True)
        elif before.channel is not None and before.channel.id == voicestate.channel.id:
            await add_yomiage_queue(member, member.guild, f"{name}が退出したのだ、", no_read_name=True)


# ボットのみか確認
def is_bot_only(channel):
    for member in channel.members:
        if member.bot is False:
            return False
    return True


@bot.event
async def on_guild_join(guild):
    await guild.get_member(bot.user.id).edit(nick=BOT_NICKNAME)

vclist_len = 0

@tasks.loop(minutes=1)
async def status_update_loop():
    for key in list(vclist):
        try:
            guild = bot.get_guild(key)
            if guild is None:
                del vclist[key]
                continue
            if guild.voice_client is None or guild.voice_client.channel is None:
                del vclist[key]
                remove_premium_guild_dict(str(guild.id))
                continue

            setting_json = await get_guild_setting(guild.id)
            alarm_setting_json = setting_json.get("alarm", [])
            now_datetime = datetime.datetime.now()
            now_youbi = now_datetime.weekday()
            for alarm in alarm_setting_json:
                alarm_datetime = datetime.datetime.strptime(alarm.get("time", "2023/4/1 11:11"), "%Y/%m/%d %H:%M")
                alarm_youbi_list = alarm.get("loop", "1111111")
                if now_datetime.hour != alarm_datetime.hour or now_datetime.minute != alarm_datetime.minute:
                    continue
                if alarm_youbi_list[now_youbi] == "0":
                    continue
                alarm_message = alarm.get('message', 'アラームなのだ')
                asyncio.create_task(add_yomiage_queue(guild.me, guild, f"{alarm_message}"))

                asyncio.create_task(guild.get_channel(vclist[key]).send(embed=discord.Embed(
                        title=f"Alarm",
                        description=f"{alarm_message}",
                        color=discord.Color.gold()
                    )))
        except Exception as e:
            logger.error(e)
            pass

    if len(voice_generate_time_list) != 0 and len(voice_generate_time_list_p) != 0:
        avarage = sum(voice_generate_time_list) / len(voice_generate_time_list)
        avarage_p = sum(voice_generate_time_list_p) / len(voice_generate_time_list_p)
    else:
        avarage = 0
        avarage_p = 0
    global is_use_gpu_server
    is_use_gpu_server = is_use_gpu_server_enabled
    global vclist_len
    local_vclen = len(vclist)
    text = f"{str(local_vclen)}/{str(len(bot.guilds))}読み上げ中\n N:{round(avarage, 1)}s P:{round(avarage_p, 1)}s"
    if check_count_id is not None:
        beta_count = await get_server_count()
        if beta_count is None:
            vclist_len = local_vclen
        else:
            print(beta_count)
            vclist_len = beta_count
    else:
        vclist_len = local_vclen
    logger.info(text)
    voice_generate_time_list_p.clear()
    voice_generate_time_list.clear()
    non_premium_user.clear()
    await bot.wait_until_ready()
    await bot.change_presence(activity=discord.CustomActivity(text))

    if is_use_gpu_server_enabled:
        now_time = datetime.datetime.now().time()
        global is_use_gpu_server_time
        # 日を跨ぐもののみ対応
        is_use_gpu_server_time = gpu_start_time < now_time or now_time < gpu_end_time

async def get_server_count():
    url = check_count_id
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    text = await response.text()  # レスポンスのテキストを取得
                    server_count = int(text.strip())  # 取得した値を整数に変換
                    return server_count
                else:
                    print(f"エラー: ステータスコード {response.status}")
                    return None
    except aiohttp.ClientError as e:
        print(f"リクエストエラー: {e}")
        return None
    except ValueError:
        print("取得した値を整数に変換できませんでした。")
        return None


async def add_premium_lopp(d):
    global premium_user_list
    global premium_server_list_300
    global premium_server_list_500
    global premium_server_list_1000
    user_id = d['metadata']['discord_user_id']
    premium_user_list.append(user_id)
    premium_guild_list = []
    for i in range(1, 4):
        p_guild = await getdatabase(str(user_id).replace(" ", ""), f"premium_guild{i}", "0")
        if p_guild.replace(" ", "") == "0":
            continue
        premium_guild_list.append(str(p_guild))

    amount = d["plan"]["amount"]
    if amount == 300:
        premium_server_list_300.append(user_id)
        premium_server_list_300.extend(premium_guild_list)
    elif amount == 500:
        premium_server_list_500.append(user_id)
        premium_server_list_500.extend(premium_guild_list)
    elif amount == 1000:
        premium_server_list_1000.append(user_id)
        premium_server_list_1000.extend(premium_guild_list)
    elif amount == 100:
        premium_user_list.extend(premium_guild_list)


@tasks.loop(hours=24)
async def dict_and_cache_loop():
    print(voice_cache_dict)
    with open(os.path.dirname(os.path.abspath(__file__)) + "/cache/" + f"voice_cache.json", 'wt',
              encoding='utf-8') as f:
        json.dump(voice_cache_dict, f, ensure_ascii=False)
    voice_cache_counter_dict.clear()
    await bot.wait_until_ready()
    global GLOBAL_DICT_CHECK
    if GLOBAL_DICT_CHECK is True:
        print("実行")
        # 辞書登録チェック
        channel = bot.get_channel(DictChannel)
        async for mes in channel.history(before=(datetime.datetime.now() + datetime.timedelta(days=-1))):
            if len(mes.embeds) == 0:
                continue
            embed = mes.embeds[0]
            embed_fields = embed.fields
            reactions = mes.reactions
            if embed.description == "グローバル辞書に単語登録を申請しました。":
                tango = embed_fields[0].value
                yomi = embed_fields[1].value
                if reactions[0].count >= reactions[1].count:
                    await update_private_dict(9686, tango, yomi)
                    embed.description = "グローバル辞書に単語が登録されました。"
                else:
                    embed.description = "適切な登録ではないため登録が拒否されました。"
                await mes.edit(embed=embed)
            elif embed.description == "グローバル辞書に音声登録を申請しました。":
                tango = embed_fields[0].value
                yomi = embed_fields[1].value
                if reactions[0].count >= reactions[1].count:
                    file_name = f"{uuid.uuid4()}.wav"
                    voice_path = (f"{user_dict_loc}/audio_data"
                                  f"/9686")
                    pronunciation = f"#%&${file_name}#%&$"
                    await update_private_dict(9686, tango, pronunciation)
                    try:
                        async with aiofiles.open(voice_path + "/" + file_name,
                                                 mode='wb') as f:
                            await f.write(await mes.attachments[0].read())
                    except ReadTimeout:
                        return
                    embed.description = "グローバル辞書に音声が登録されました。"
                else:
                    embed.description = "適切な登録ではないため登録が拒否されました。"
                await mes.edit(embed=embed)
            elif embed.description == "グローバル辞書に単語削除を申請しました。":
                tango = embed_fields[0].value
                if reactions[0].count >= reactions[1].count:
                    await delete_private_dict(9686, tango)
                    embed.description = "グローバル辞書から単語が削除されました。"
                else:
                    embed.description = "適切な削除ではないため削除が拒否されました。"
                await mes.edit(embed=embed)


@tasks.loop(minutes=10)
async def save_join_list_task():
    await save_join_list()


@tasks.loop(minutes=10)
async def premium_user_check_loop():
    if stripe.api_key is None:
        return
    global premium_user_list
    global premium_server_list_300
    global premium_server_list_500
    global premium_server_list_1000
    premium_user_list.clear()
    premium_server_list_300.clear()
    premium_server_list_500.clear()
    premium_server_list_1000.clear()
    count = 0

    async for d in (await stripe.Subscription.search_auto_paging_iter_async(limit=100,
                                        query="status:'active' AND -metadata['discord_user_id']:null")):
        count += 1
        await add_premium_lopp(d)
    async for d in (await stripe.Subscription.search_auto_paging_iter_async(limit=100,
                                        query="status:'trialing' AND -metadata['discord_user_id']:null")):
        count += 1
        await add_premium_lopp(d)
    print(f"プレミアム数: {count}")


@tasks.loop(minutes=1, count=1)
async def init_loop():
    global default_conn
    global default_gpu_conn
    global premium_conn
    default_conn = aiohttp.TCPConnector(limit=20, limit_per_host=5)
    default_gpu_conn = aiohttp.TCPConnector(limit=20, limit_per_host=5)
    premium_conn = aiohttp.TCPConnector(limit=20, limit_per_host=5)

    global voice_cache_dict
    with open(os.path.dirname(os.path.abspath(__file__)) + "/cache/voice_cache.json", "r", encoding='utf-8') as f:
        voice_cache_dict = json.load(f)
        print("起動")
        print(voice_cache_dict)

    global pool
    pool = await get_connection()

    await initdatabase()
    await init_voice_list()
    status_update_loop.start()
    auto_restart.start()

    dict_and_cache_loop.start()
    bot.add_view(ActivateButtonView())
    bot.loop.create_task(connect_nodes())
    bot.loop.create_task(connect_websocket())
    await updatedict()
    premium_user_check_loop.start()
    await bot.wait_until_ready()
    await auto_join()
    save_join_list_task.start()

    # ファイル変更検知・自動再起動
    async for changes in awatch(os.path.dirname(os.path.abspath(__file__)) + "/main.py"):
        print(changes)
        await stop()
        break
    while datetime.datetime.now().minute % 10 != 0:
        await asyncio.sleep(0.1)


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
async def adddict_local(ctx, surface: discord.Option(input_type=str, description="辞書に登録する単語", required=False),
                        pronunciation: discord.Option(input_type=str, description="カタカナでの読み方", required=False),
                        audio_file: discord.Option(discord.Attachment, description="ボイス辞書用音声ファイル(wav, mp3)", required=False),
                        dict_file: discord.Option(discord.Attachment, description="インポート用辞書ファイル(json)", required=False)):
    print(surface)
    if dict_file is not None:
        print(dict_file.content_type)
        if str(dict_file.content_type).split(";")[0] not in ["application/json"]:
            embed = discord.Embed(
                title="**Error**",
                description=f"JSONファイルを指定してください。",
                color=discord.Colour.brand_red(),
            )
            await ctx.respond(embed=embed)
            return
        import_dict: dict = json.loads((await dict_file.read()).decode('utf-8'))
        for content in import_dict.keys():
            if await update_private_dict(ctx.guild.id, content, import_dict.get(content)) is not True:
                embed = discord.Embed(
                    title="**Error**",
                    description=f"登録数の上限に達しました。(サポートサーバーへお問い合わせください。)\n"
                                f"{content}まで登録しました。",
                    color=discord.Colour.brand_red(),
                )
                await ctx.respond(embed=embed)
                return
        embed = discord.Embed(
            title="**Import Dict**",
            description=f"{len(import_dict)}件を辞書に登録しました。",
            color=discord.Colour.brand_green(),
        )
        await ctx.respond(embed=embed)
        return


    if surface is None or surface == "":
        embed = discord.Embed(
            title="**Error**",
            description=f"空文字は登録できません。",
            color=discord.Colour.brand_red(),
        )
        await ctx.respond(embed=embed)
        return
    if pronunciation is None and audio_file is None:
        embed = discord.Embed(
            title="**Error**",
            description=f"pronunciationまたはaudio_fileを指定してください",
            color=discord.Colour.brand_red(),
        )
        await ctx.respond(embed=embed)
        return

    # 音声ファイル辞書登録
    if audio_file is not None:
        if await is_premium_check(ctx.author.id, 100) is False:
            embed = discord.Embed(
                title="**Error**",
                description=f"ボイス辞書はプレミアム限定機能です。",
                color=discord.Colour.brand_red(),
            )
            await ctx.respond(embed=embed)
            return
        if audio_file.size > 10*1024*1024:
            embed = discord.Embed(
                title="**Error**",
                description=f"ファイルサイズは最大10MBまでです。",
                color=discord.Colour.brand_red(),
            )
            await ctx.respond(embed=embed)
            return
        print(audio_file.content_type)
        if str(audio_file.content_type) not in ["audio/x-wav"]:
            embed = discord.Embed(
                title="**Error**",
                description=f"wavファイルのみ利用できます。mp3などの場合はファイル変換サイトなどでwavに変換が必要です。",
                color=discord.Colour.brand_red(),
            )
            await ctx.respond(embed=embed)
            return

        file_name = f"{uuid.uuid4()}.wav"
        voice_path =  (f"{user_dict_loc}/audio_data"
                       f"/{ctx.guild.id}")
        pronunciation = f"#%&${file_name}#%&$"
        os.makedirs(voice_path, exist_ok=True)
        if len(surface) > 50:
            embed = discord.Embed(
                title="**Error**",
                description=f"50文字以下の単語のみ登録できます。",
                color=discord.Colour.brand_red(),
            )
            await ctx.respond(embed=embed)
            return
        if await update_private_dict(ctx.guild.id, surface, pronunciation) is not True:
            embed = discord.Embed(
                title="**Error**",
                description=f"登録数の上限に達しました。(サポートサーバーへお問い合わせください。)",
                color=discord.Colour.brand_red(),
            )
            await ctx.respond(embed=embed)
            return

        try:
            async with aiofiles.open(voice_path + "/" + file_name,
                                     mode='wb') as f:
                await f.write(await audio_file.read())
        except ReadTimeout:
            return


        embed = discord.Embed(
            title="**Add Dict**",
            description=f"辞書に音声を登録しました。",
            color=discord.Colour.brand_green(),
        )
        embed.add_field(name="surface", value=surface)
        embed.add_field(name="pronunciation", value=audio_file.url)
        await ctx.respond(embed=embed)
        return


    if len(surface) > 50 or len(pronunciation) > 50:
        embed = discord.Embed(
            title="**Error**",
            description=f"50文字以下の単語のみ登録できます。",
            color=discord.Colour.brand_red(),
        )
        await ctx.respond(embed=embed)
        return
    if await update_private_dict(ctx.guild.id, surface, pronunciation) is not True:
        embed = discord.Embed(
            title="**Error**",
            description=f"登録数の上限に達しました。(サポートサーバーへお問い合わせください。)",
            color=discord.Colour.brand_red(),
        )
        await ctx.respond(embed=embed)
        return
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
        json_file = discord.File(user_dict_loc + "/" + f"{ctx.guild.id}.json")
    except:
        embed.description = "辞書は設定されていません。"
        await ctx.respond(embed=embed)
        return

    await ctx.respond(embed=embed, file=json_file)


@bot.slash_command(description="ミュートを設定するのだ", default_member_permissions=discord.Permissions.manage_guild)
@discord.commands.default_permissions(manage_messages=True)
async def mute(ctx, target: discord.Option(discord.Member)):
    mute_list = await getdatabase(ctx.guild.id, "mute_list", [], "guild")
    if target.id in mute_list:
        embed = discord.Embed(
            title="**Error**",
            description=f"すでにミュートされています",
            color=discord.Colour.brand_red(),
        )
        await ctx.respond(embed=embed)
        return
    elif len(mute_list) >= 25:
        embed = discord.Embed(
            title="**Error**",
            description=f"ミュート登録数上限に達しました",
            color=discord.Colour.brand_red(),
        )
        await ctx.respond(embed=embed)
        return
    mute_list.append(target.id)
    await setdatabase(ctx.guild.id, "mute_list", mute_list, "guild")
    embed = discord.Embed(
        title="**Success**",
        description=f"{target.name}をミュートしました",
        color=discord.Colour.brand_green(),
    )
    await ctx.respond(embed=embed)


@bot.slash_command(description="ミュートを解除するのだ", default_member_permissions=discord.Permissions.manage_guild)
@discord.commands.default_permissions(manage_messages=True)
async def unmute(ctx, target: discord.Option(discord.Member)):
    mute_list = await getdatabase(ctx.guild.id, "mute_list", [], "guild")
    if target.id not in mute_list:
        embed = discord.Embed(
            title="**Error**",
            description=f"すでにミュートされていません",
            color=discord.Colour.brand_red(),
        )
        await ctx.respond(embed=embed)
        return
    mute_list.remove(target.id)
    await setdatabase(ctx.guild.id, "mute_list", mute_list, "guild")
    embed = discord.Embed(
        title="**Success**",
        description=f"{target.name}のミュートを解除しました",
        color=discord.Colour.brand_green(),
    )
    await ctx.respond(embed=embed)


@bot.command(description="ミュート一覧を表示するのだ", default_member_permissions=discord.Permissions.manage_guild)
@discord.commands.default_permissions(manage_messages=True)
async def showmute(ctx):
    mute_list = await getdatabase(ctx.guild.id, "mute_list", [], "guild")
    list_text = ""
    for mute_id in mute_list:
        mute_member = ctx.guild.get_member(mute_id)
        if mute_member is None:
            continue
        list_text += f"{mute_member.mention}, "
    embed = discord.Embed(
        title="**ミュート一覧**",
        description=f"{list_text}\n計{len(mute_list)}ユーザー",
        color=discord.Colour.brand_green(),
    )
    await ctx.respond(embed=embed)


async def henkan_private_dict(server_id, source):
    try:
        with open(user_dict_loc + "/" + f"{server_id}.json", "r",
                  encoding='utf-8') as f:
            json_data = json.load(f)
    except:
        json_data = {}
    source = toLowerCase(source)
    dict_data = sorted(json_data.keys(), key=len)
    dict_data.reverse()
    limit = text_limit_100 + 50
    output = ""

    split_1 = source.split("#%&$")

    for split_num in range(len(split_1)):
        split_text = split_1[split_num]
        if split_num%2 != 0:
            output += f"#%&${split_text}#%&$"
            continue
        for k in dict_data:
            if json_data[k].startswith("#%&$"):
                split_text = split_text.replace(k, json_data[k])
                if len(split_text) > limit:
                    split_text = split_text[:(text_limit_100 + 50)]
        output += split_text

    spilit_2 = output.split("#%&$")
    output = ""

    for split_num in range(len(spilit_2)):
        split_text = spilit_2[split_num]
        if split_num % 2 != 0:
            output += f"#%&${split_text}#%&$"
            continue
        for k in dict_data:
            if json_data[k].startswith("#%&$"):
                continue
            split_text = split_text.replace(k, json_data[k])
            if len(split_text) > limit:
                split_text = split_text[:(text_limit_100 + 50)]
        output += split_text
    return output


async def update_private_dict(server_id, source, kana):
    try:
        with open(user_dict_loc + "/" + f"{server_id}.json", "r",
                  encoding='utf-8') as f:
            json_data = json.load(f)
    except:
        json_data = {}
    if len(json_data) > 1000:
        return False
    json_data[toLowerCase(source)] = kana
    sorted_json_data = json_data
    with open(user_dict_loc + "/" + f"{server_id}.json", 'wt',
              encoding='utf-8') as f:
        json.dump(sorted_json_data, f, ensure_ascii=False)
    return True


async def delete_private_dict(server_id, source):
    try:
        with open(user_dict_loc + "/" + f"{server_id}.json", "r",
                  encoding='utf-8') as f:
            json_data = json.load(f)
    except:
        json_data = {}
    pop_yomi  = json_data.pop(toLowerCase(source))

    # ファイル削除
    split_output = pop_yomi.split("#%&$")
    print(split_output)
    for i in range(len(split_output)):
        split_text = split_output[i].replace("/", "")
        voice_path = (f"{user_dict_loc}/audio_data"
                      f"/{server_id}/{split_text}")
        if split_text.endswith(".wav") and os.path.isfile(voice_path):
            os.remove(voice_path)

    sorted_json_data = json_data
    with open(user_dict_loc + "/" + f"{server_id}.json", 'wt',
              encoding='utf-8') as f:
        json.dump(sorted_json_data, f, ensure_ascii=False)


async def update_guild_setting(server_id, setting, value):
    try:
        with open(os.path.dirname(os.path.abspath(__file__)) + f"/guild_setting/{server_id}.json", "r",
                  encoding='utf-8') as f:
            setting_dict = json.load(f)
    except:
        setting_dict = {}
    setting_dict[setting] = value
    with open(os.path.dirname(os.path.abspath(__file__)) + f"/guild_setting/{server_id}.json", 'wt',
              encoding='utf-8') as f:
        json.dump(setting_dict, f, ensure_ascii=False)


async def get_guild_setting(server_id):
    try:
        with open(os.path.dirname(os.path.abspath(__file__)) + f"/guild_setting/{server_id}.json", "r",
                  encoding='utf-8') as f:
            setting_dict = json.load(f)
    except:
        setting_dict = {}
    return setting_dict


def toLowerCase(text):
    text = unicodedata.normalize('NFKC', text)
    text = text.lower()
    return text


async def is_premium_check(id, value):
    id_str = str(id)
    is_check = False
    if 100 >= value > 0:
        is_check = id_str in premium_user_list or id_str in premium_server_list_300 or id_str in premium_server_list_500 or id_str in premium_server_list_1000
    elif 300 >= value > 100:
        is_check = id_str in premium_server_list_300 or id_str in premium_server_list_500 or id_str in premium_server_list_1000
    elif 500 >= value > 300:
        is_check = id_str in premium_server_list_500 or id_str in premium_server_list_1000
    elif 1000 >= value > 500:
        is_check = id_str in premium_server_list_1000
    if is_check is False and id in premium_guild_dict:
        is_check = premium_guild_dict[id] >= value

    if is_check is False and id not in non_premium_user:
        non_premium_user.append(id)
        guild_premium_user_id = int(await getdatabase(id, "premium_user", 0, "guild"))
        if guild_premium_user_id != 0:
            is_check = await is_premium_check(guild_premium_user_id, value)
            if is_check is True:
                add_premium_user(id, value)

    if is_check is False and id in premium_guild_dict:
        if premium_guild_dict.get(id) >= value:
            is_check = True

    '''elif id not in non_premium_user and value > 0:
        non_premium_user.append(id)
        for d in stripe.Subscription.search(limit=100,
                                            query=f"status:'active' AND -metadata['discord_user_id']:{id}").auto_paging_iter():
            add_premium_user(id, value)
            return d["plan"]["amount"] > value'''
    return is_check


# 地震情報WebSocket
async def connect_websocket():
    if EEW_WEBHOOK_URL is None:
        return
    async for websocket in websockets.connect(EEW_WEBHOOK_URL):
        try:
            eew_dict = json.loads(await websocket.recv())
            if eew_dict["code"] == 556:

                prefs = []
                prefs_str = ""
                is_first = True
                for area in eew_dict["areas"]:
                    pref = area["pref"]
                    if pref in prefs:
                        continue
                    prefs.append(pref)
                    if is_first:
                        is_first = False
                        prefs_str += pref
                    else:
                        prefs_str += f"、{pref}"

                print(prefs)
                embed = discord.Embed(
                    title="**緊急地震速報（警報）**",
                    description=f"{prefs_str}\n\n以上の地域で震度4以上の揺れが予測されます\n\n"
                                f"[Yahoo地震情報](https://typhoon.yahoo.co.jp/weather/jp/earthquake/) | "
                                f"[BSC24](https://www.youtube.com/watch?v=ZeZ049BUy8Q)",
                    color=discord.Colour.brand_red(),
                )
                embed.set_thumbnail(url="https://free-icons.net/wp-content/uploads/2020/09/symbol018.png")
                embed.set_footer(text="気象庁の情報を利用")
                logger.info(prefs_str)
                for guild_id in premium_server_list:
                    guild = bot.get_guild(guild_id)
                    if await getdatabase(guild.id, "is_eew", True, "guild"):
                        try:
                            channel = guild.get_channel(vclist[guild.id])
                            await channel.send(embed=embed)
                        except:
                            pass
                        await add_yomiage_queue(guild.me, guild, f"緊急地震速報　{prefs_str}")

        except websockets.ConnectionClosed as e:
            logger.error(e)
            continue

@tasks.loop(time=datetime.time(hour=6, minute=0, second=0,
                               tzinfo=datetime.timezone(datetime.timedelta(hours=+9), 'JST')))
async def auto_restart():
    await stop("ずんだもんの定期再起動を行います")

if __name__ == '__main__':
    bot.loop.create_task(init_loop())
    bot.load_extension('commands.SetAlarmCommand')
    bot.run(token)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

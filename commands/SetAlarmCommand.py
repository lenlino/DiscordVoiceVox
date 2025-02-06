import discord
import unicodedata
from discord.ext import commands
from discord.ui import Select, Button, View
import datetime

import main


class SetAlarmCommand(commands.Cog):


    async def get_alarm_settings(ctx: discord.AutocompleteContext):
        setting_json = await main.get_guild_setting(ctx.interaction.guild.id)
        alarm_setting_json = setting_json.get("alarm", [])
        result = []

        def truncate_text(text: str, limit: int = 30) -> str:
            """文字数を制限し、超える場合に '...' を付ける"""
            if len(text) > limit:
                return text[:limit] + '...'
            return text

        for i in range(len(alarm_setting_json)):
            alarm = alarm_setting_json[i]
            alarm_datetime = datetime.datetime.strptime(alarm.get("time", "2023/4/1 11:11"), "%Y/%m/%d %H:%M")
            alarm_message = alarm.get('message', 'アラームなのだ')
            option_name_message = truncate_text(alarm_message, 30)
            result.append(discord.OptionChoice(name=f"{alarm_datetime.hour}:{alarm_datetime.minute} {option_name_message}",
                                               value=str(i)))
        return result

    @discord.slash_command(name="setalarm", description="アラーム設定(alarm setting)")
    @discord.commands.default_permissions(manage_messages=True)
    async def set_alarm_command(self, ctx, action: discord.Option(required=True, input_type=str, description="リスト", choices=["add", "del", "list"]),
                           time: discord.Option(required=False, input_type=str, description="時刻(例[5:10]: 0510)", min_length=4, max_length=4),
                           loop: discord.Option(required=False, input_type=str, description="繰り返し(例[月木日]: 1001001)", default="1111111", min_length=7, max_length=7),
                           message: discord.Option(required=False, input_type=discord.SlashCommandOptionType.string, description="アラームメッセージ", default="アラームなのだ"),
                           delete_target: discord.Option(required=False, input_type=discord.SlashCommandOptionType.integer, description="削除するアラーム",
                                                         autocomplete=discord.utils.basic_autocomplete(get_alarm_settings))):
        await ctx.defer()
        embed = discord.Embed(
            title="**Error**",
            description=f"50文字以下の単語のみ登録できます。",
            color=discord.Colour.brand_red(),
        )
        if await main.is_premium_check(ctx.author.id, 100) is False and await main.is_premium_check(ctx.guild.id, 100):
            embed.description = "プレミアムプラン限定機能です"
            await ctx.send_followup(embed=embed)
            return
        setting_json = await main.get_guild_setting(ctx.guild.id)
        alarm_setting_json = setting_json.get("alarm", [])
        if action == "add":
            if time is None:
                embed.description = "時刻(time)を指定してください。"
                await ctx.send_followup(embed=embed)
                return
            time = unicodedata.normalize('NFKC', time)
            loop = unicodedata.normalize('NFKC', loop)
            minutes = int(f"{time[-2]}{time[-1]}")
            hours = int(f"{time[-4]}{time[-3]}")
            alarm_datatime = datetime.datetime(2023, 4, 1, hours, minutes)
            alarm_setting_json.append({
                "time": alarm_datatime.strftime("%Y/%m/%d %H:%M"),
                "loop": loop,
                "message": message
            })
            await main.update_guild_setting(ctx.guild.id, "alarm", alarm_setting_json)
            embed = discord.Embed(
                title="**Success**",
                description=f"アラームを登録しました",
                color=discord.Colour.brand_green(),
            )
            embed.add_field(name="時刻(time)", value=f"{hours}:{minutes}")
            embed.add_field(name="繰り返し", value=f"{loop}")
            embed.add_field(name="メッセージ", value=f"{message}")
            await ctx.send_followup(embed=embed)
            return
        elif action == "del":
            pop_alarm = alarm_setting_json.pop(int(delete_target))
            await main.update_guild_setting(ctx.guild.id, "alarm", alarm_setting_json)
            embed = discord.Embed(
                title="**Success**",
                description=f"アラームを削除しました",
                color=discord.Colour.brand_green(),
            )
            embed.add_field(name="メッセージ", value=f"{pop_alarm.get('message', 'アラームなのだ')}")
            await ctx.send_followup(embed=embed)
            pass
        elif action == "list":
            setting_json = await main.get_guild_setting(ctx.guild.id)
            alarm_setting_json = setting_json.get("alarm", [])
            result = ""

            for i in range(len(alarm_setting_json)):
                alarm = alarm_setting_json[i]
                alarm_datetime = datetime.datetime.strptime(alarm.get("time", "2023/4/1 11:11"), "%Y/%m/%d %H:%M")
                alarm_message = alarm.get('message', 'アラームなのだ')
                result += f"{alarm_datetime.hour}:{alarm_datetime.minute} {alarm_message}\n"
            await main.update_guild_setting(ctx.guild.id, "alarm", alarm_setting_json)
            embed = discord.Embed(
                title="**アラーム設定一覧**",
                description=f"{result}",
                color=discord.Colour.brand_green(),
            )
            await ctx.send_followup(embed=embed)
            pass

def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(SetAlarmCommand(bot))  # add the cog to the bot



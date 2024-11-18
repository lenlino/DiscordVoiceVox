class SetAlarmCommand(commands.Cog):
    @discord.slash_command(name="card", description="アラーム設定(alarm setting)", guilds=["86444102886608076"])
    async def card_command(self, ctx, action: discord.Option(required=False, input_type=int, description="リスト"), ):
        await ctx.defer()

        pass
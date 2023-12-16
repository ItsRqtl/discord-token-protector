"""
Cog module for the slash commands.
"""

import discord

from src.client.i18n import I18n, option, slash_command
from src.main import BaseCog, Bot


class Commands(BaseCog):
    """
    The cog class for the slash commands.
    """

    @slash_command("opt-out")
    async def opt_out(self, ctx: discord.ApplicationContext) -> None:
        """
        The slash command for opting out of the bot.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        """
        await ctx.defer(ephemeral=True)
        data = await self.database.get_user(ctx.author.id)
        status = not data["opt_out"] if data else True
        lang = data["language"] if data else ctx
        await self.database.opt_out(ctx.author.id, status)
        await ctx.respond(I18n.get(f"slash.opt-out.success.{status}", lang))

    @slash_command("language")
    @option(
        identifier="language",
        parameter_name="lang",
        choices=[
            discord.OptionChoice(name="English", value="en-US"),
            discord.OptionChoice(name="繁體中文", value="zh-TW"),
            discord.OptionChoice(name="简体中文", value="zh-CN"),
        ],
    )
    async def language(self, ctx: discord.ApplicationContext, lang: str) -> None:
        """
        The slash command for changing the language.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param lang: The language to change to.
        :type lang: str
        """
        await ctx.defer(ephemeral=True)
        await self.database.set_language(ctx.author.id, lang)
        await ctx.respond(I18n.get("slash.language.success", lang))


def setup(bot: Bot) -> None:
    """
    The setup function of the cog.
    """
    bot.add_cog(Commands(bot))

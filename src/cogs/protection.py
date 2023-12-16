"""
Cog module for the token protection functions.
"""

import discord

from src.client.i18n import I18n
from src.main import BaseCog, Bot
from src.utils.token_detection import TokenDetector


class Protection(BaseCog):
    """
    The cog class for the token protection functions.
    """

    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)
        self._features = self.config["features"]
        self.check_attachments = self._features["check-attachments"]
        self.check_textfile = self._features["check-textfile"]
        self.check_archive = self._features["check-archive"]

    async def delete_message(self, message: discord.Message, locale: str) -> None:
        """
        Delete the message and send a warning.

        :param message: The message object.
        :type message: discord.Message
        :param locale: The locale for the warning message.
        :type locale: str
        """
        if message.channel.permissions_for(message.guild.me).manage_messages:
            await message.reply(
                I18n.get("event.protection.deleted", locale, author=message.author.mention)
            )
            await message.delete()
        else:
            await message.channel.send(
                I18n.get("event.protection.missing-perms", locale, author=message.author.mention)
            )

    @BaseCog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        The event handler for the message event.

        :param message: The message object.
        :type message: discord.Message
        """
        if (
            message.author.bot  # ignore bots
            or not message.guild  # ignore DMs
            or not message.channel.permissions_for(
                message.guild.me
            ).send_messages  # skip if the bot can't send warnings anyways
            or not (message.content or message.attachments)  # skip if there's no content to check
        ):
            return

        user = await self.database.get_user(message.author.id)
        if user and user["opt_out"]:
            return  # user has opted out of protection

        locale = user["language"] if user else message.guild.preferred_locale or "en-US"

        if message.content and TokenDetector.detect(message.content):
            return await self.delete_message(message, locale)

        if self.check_attachments:
            for i in message.attachments:
                if await TokenDetector.scan_attachment(i, self.check_textfile, self.check_archive):
                    return await self.delete_message(message, locale)


def setup(bot: Bot) -> None:
    """
    The setup function of the cog.
    """
    bot.add_cog(Protection(bot))

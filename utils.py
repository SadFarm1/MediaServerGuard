import discord
from discord import TextChannel

import constants


def get_member_id(member):
    member = member.replace('<', '')
    member = member.replace('>', '')
    member = member.replace('@', '')
    member = member.replace('!', '')
    member = member.replace('#', '')
    return int(member)


def is_user(member, target_member) -> bool:
    return str(member) == target_member


def ping_calculation(client) -> str:
    return f'{round(client.latency * 1000)}ms'


async def alert_admins(client, user_name: str, user_id: str, details: str, guild_name: str):
    admin_channel: TextChannel = discord.utils.get(client.get_all_channels(),
                                                   guild__name=constants.ADMIN_GUILD_NAME,
                                                   name=constants.ADMIN_GUILD_ALERT_CHANNEL_NAME)
    embed = discord.Embed(title="Guard Alert",
                          description=f"For {user_name} ``{user_id}``",
                          color=0xff0000)
    embed.add_field(
        name=f"Report manually submitted by {guild_name}",
        value=details,
        inline=False
    )
    await admin_channel.send(embed=embed)


class Alert:
    def __init__(self, guild, channel, message):
        self.guild = guild
        self.channel = channel
        self.message = message

    def __str__(self):
        return f'Guild: {self.guild} | Channel: {self.channel} | Message: {self.message}'


class ResponseChecker:
    def __init__(self, ctx):
        self._ctx = ctx

    def check(self, message) -> bool:
        return message.author == self._ctx.author and message.channel == self._ctx.message.channel


class HelpConfigField:
    def __init__(self, value, description):
        self._value = value
        self.description = description

    def get_value(self, prefix: str):
        return self._value


class HelpConfigCommand(HelpConfigField):
    def __init__(self, command, description):
        super().__init__(value=command, description=description)

    def get_value(self, prefix: str):
        return f"``{prefix}{self._value}``"


class HelpConfig:
    def __init__(self):
        self.entries: list[HelpConfigField] = []

    def add_command(self, command, description):
        self.entries.append(HelpConfigCommand(command, description))

    def add_command_config(self, config: HelpConfigCommand):
        self.entries.append(config)

    def add_field(self, value, description):
        self.entries.append(HelpConfigField(value, description))

    def add_field_config(self, config: HelpConfigField):
        self.entries.append(config)


class Help:
    def __init__(self, prefix: str, title: str, description: str, config: HelpConfig, title_color: int = 0x00ff00,
                 footer_text: str = None):
        self.prefix = prefix
        self.title = title
        self.title_color = title_color
        self.description = description
        self.config = config
        self.footer_text = footer_text

    @property
    def embed(self):
        embed = discord.Embed(title=self.title, description=self.description, color=self.title_color)
        for entry in self.config.entries:
            embed.add_field(name=entry.description, value=entry.get_value(prefix=self.prefix), inline=False)
        if self.footer_text:
            embed.set_footer(text=self.footer_text)
        return embed

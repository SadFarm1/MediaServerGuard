import asyncio
import os
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv, find_dotenv

import constants
import utils
from watchlist import Watchlist

intents = discord.Intents.all()
client = commands.Bot(command_prefix=constants.DISCORD_PREFIX, intents=intents)
client.remove_command('help')
client.load_extension('jishaku')

load_dotenv(find_dotenv())

watchlist = Watchlist(creds_json_file_path=constants.GOOGLE_SHEETS_CREDS_FILE)


@client.event
async def on_ready():
    print('Bot is ready!')
    for guild in client.guilds:
        print(guild.name)


@client.event
async def on_guild_join(guild):
    await guild.create_text_channel(constants.ALERTS_CHANNEL_NAME)
    channel = discord.utils.get(client.get_all_channels(),
                                guild__name=str(guild),
                                name=constants.ALERTS_CHANNEL_NAME)

    await channel.send(constants.JOIN_MESSAGE)


@client.command(name="obey")
async def obey(ctx):
    if utils.is_user(ctx.message.author, constants.MASTER_USERNAME):
        await ctx.send(constants.MASTER_OBEY_MESSAGE)
    else:
        await ctx.send(constants.NOT_MASTER_OBEY_MESSAGE)


@client.command(name="die")
@commands.is_owner()
async def die(ctx):
    await ctx.send(constants.DEATH_MESSAGE)
    sys.exit()


@client.command(name="ping")
async def ping(ctx):
    await ctx.send(f'Pong! {utils.ping_calculation(client)}')


@client.command(name="help")
async def help(ctx):
    help_config = utils.HelpConfig()
    help_config.add_command('ping', 'Ping Bot')
    help_config.add_command('report', 'Report Users')
    help_config.add_command('manualreport', 'Manually Report Users')
    help_config.add_field(constants.WATCHLIST_SPREADSHEET, 'Watchlist Link')
    help_config.add_command("scan", 'Scan Server for Users on Watchlist')
    help_config.add_command("invite", 'Invite Bot')
    help_config.add_command('help', 'See Help Menu')

    help_menu = utils.Help(prefix=client.command_prefix,
                           title=constants.HELP_MENU_TITLE,
                           description=constants.HELP_MENU_DESCRIPTION,
                           config=help_config,
                           title_color=constants.HELP_MENU_TITLE_COLOR,
                           footer_text=constants.HELP_MENU_FOOTER_TEXT)

    await ctx.send(embed=help_menu.embed)


@client.command(name="manualreport")
@commands.has_permissions(kick_members=True)
async def manual_report(ctx):
    if ctx.message.author.id in constants.IGNORE_USER_IDS:
        return

    response_checker = utils.ResponseChecker(ctx=ctx)

    user_name_embed = discord.Embed(
        title="Type the name of the user (Ex: SadFarm1#3217)",
        color=0x009933
    )

    user_name_msg = await ctx.send(embed=user_name_embed)

    try:
        user_name = await client.wait_for('message', check=response_checker.check, timeout=300)

        if '#' not in user_name.content:
            await ctx.send('Invalid username! Please try running this command again')
            return
    except asyncio.TimeoutError:
        await ctx.send(constants.REQUEST_TIME0UT_MESSAGE)
        return

    user_id_embed = discord.Embed(
        title="Type the ID of the user (Ex: 453959267347595276)",
        color=0x009933
    )

    user_id_msg = await ctx.send(embed=user_id_embed)

    try:
        user_id = await client.wait_for('message', check=response_checker.check, timeout=300)
    except asyncio.TimeoutError:
        await ctx.send(constants.REQUEST_TIME0UT_MESSAGE)
        return

    user_report_embed = discord.Embed(
        title="Type report for the user (Ex: Scammer)",
        color=0x009933
    )

    user_report_msg = await ctx.send(embed=user_report_embed)

    try:
        user_report = await client.wait_for('message', check=response_checker.check, timeout=300)
    except asyncio.TimeoutError:
        await ctx.send(constants.REQUEST_TIME0UT_MESSAGE)
        return

    user_name = user_name.content
    user_id = user_id.content
    user_report = user_report.content

    watchlist.add_entry(
        username=user_name,
        user_id=user_id,
        details=user_report,
        guild_name=ctx.message.guild.name
    )

    await utils.alert_admins(client=client,
                             user_name=user_name,
                             user_id=user_id,
                             details=user_report,
                             guild_name=ctx.message.guild.name)

    await ctx.send('Report sent!')


@client.command(name="report")
@commands.has_permissions(kick_members=True)
async def report(ctx):
    if ctx.message.author.id in constants.IGNORE_USER_IDS:
        return

    response_checker = utils.ResponseChecker(ctx=ctx)

    user_tag_embed = discord.Embed(
        title="Ping the user (Ex: @SadFarm1)",
        color=0x009933
    )

    user_tag_msg = await ctx.send(embed=user_tag_embed)
    try:
        user_tag = await client.wait_for('message', check=response_checker.check, timeout=300)

        if '@' not in user_tag.content:
            await ctx.send('Invalid tag! Please try running this command again')
            return
        else:
            user_id = utils.get_member_id(user_tag.content)
            user_name = str(client.get_user(user_id))

    except asyncio.TimeoutError:
        await ctx.send(constants.REQUEST_TIME0UT_MESSAGE)
        return

    user_report_embed = discord.Embed(
        title="Type report for the user (Ex: Scammer)",
        color=0x009933
    )

    user_report_msg = await ctx.send(embed=user_report_embed)

    try:
        user_report = await client.wait_for('message', check=response_checker.check, timeout=300)
    except asyncio.TimeoutError:
        await ctx.send(constants.REQUEST_TIME0UT_MESSAGE)
        return

    user_report = user_report.content

    watchlist.add_entry(
        username=user_name,
        user_id=user_id,
        details=user_report,
        guild_name=ctx.message.guild.name
    )

    await utils.alert_admins(client=client,
                             user_name=user_name,
                             user_id=user_id,
                             details=user_report,
                             guild_name=ctx.message.guild.name)

    await ctx.send('Report sent!')


@report.error
async def report_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Please tag a user to report them!")


@client.command(name="invite")
async def invite(ctx):
    await ctx.send(constants.INVITE_LINK)


@client.command(name="scan")
async def scan(ctx):
    await ctx.send('Scan initiated! This may take a bit.')

    guild = ctx.message.guild

    watchlist_matches = watchlist.get_all_watchlist_matches(members=guild.members)

    for match in watchlist_matches:
        await ctx.send(embed=match.embed)

    await ctx.send("Scan Complete!")


async def process_if_member_joined_admin_guild(member):
    if member.guild.id == constants.ADMIN_GUILD_ID:
        admin_channel = discord.utils.get(client.get_all_channels(),
                                          guild__name=constants.ADMIN_GUILD_NAME,
                                          name=constants.ADMIN_GUILD_VERIFY_CHANNEL_NAME)
        message = constants.ADMIN_GUILD_MEMBER_JOIN_MESSAGE
        await admin_channel.send(message)


@client.event
async def on_member_join(member):
    await process_if_member_joined_admin_guild(member=member)

    watchlist_match = watchlist.get_watchlist_match(member=member)

    if watchlist_match:
        channel = discord.utils.get(client.get_all_channels(),
                                    guild__name=str(member.guild),
                                    name=constants.ALERTS_CHANNEL_NAME)
        await channel.send(embed=watchlist_match.embed)


key = os.getenv(constants.DISCORD_KEY_ENV)
client.run(key)

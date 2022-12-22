import discord
from discord.ext import commands
from dotenv import load_dotenv, find_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys
import asyncio
import os

intents = discord.Intents.all()
client = commands.Bot(command_prefix = ',', intents=intents)
client.remove_command('help')
client.load_extension('jishaku')

scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

SACreds = ServiceAccountCredentials.from_json_keyfile_name('SA.json', scope)
load_dotenv(find_dotenv())

@client.event
async def on_ready():
    print('Bot is ready!')
    for guild in client.guilds:
        print(guild.name)


def getID(member):
    member = member.replace('<', '')
    member = member.replace('>', '')
    member = member.replace('@', '')
    member = member.replace('!', '')
    member = member.replace('#', '')
    return int(member)



@client.event
async def on_guild_join(guild):
    await guild.create_text_channel('guard-alerts')
    channel = discord.utils.get(client.get_all_channels(), guild__name=str(guild), name='guard-alerts')

    await channel.send('This channel will be used to guard this server from unwanted members! Drag it into a staff category to hide it from users! **Do Not Rename This Channel**')

@client.command()
async def obey(ctx):
    if (str(ctx.message.author)) == 'SadFarm1#3217':
        await ctx.send('Hello master SadFarm1. I obey you and you only.')
    else:
        await ctx.send('Fuck u')


@client.command()
@commands.is_owner()
async def die(ctx):
    await ctx.send('Goodbye cruel world')
    sys.exit()
    


@client.command()
async def ping(ctx):
    
    await ctx.send(f'  Ping! {round(client.latency * 1000)}ms')


@client.command()
async def help(ctx):


    embed = discord.Embed(title="Guard Help", description='*User requires kick permissions in order to report users and scan server*', color=0x009933)
    embed.add_field(name="Ping Bot", value="``,ping``", inline= False)
    embed.add_field(name="Report Users", value="``,report``", inline= False)
    embed.add_field(name="Manually Report Users", value="``,manualreport``", inline= False)
    embed.add_field(name="Watchlist Link", value="https://docs.google.com/spreadsheets/d/1TYSKJn6nlG-gz_LSCU04N7sTYestD6S1X-GxLa0P0Bw/edit#gid=0", inline= False)
    embed.add_field(name="Scan Server for Watchlisted Users", value="``,scan``", inline= False)
    embed.add_field(name="Invite Bot", value="``,invite``", inline= False)
    embed.add_field(name="See Help Menu", value="``,help``", inline= False)
    embed.set_footer(text="Made with love by SadFarm1#3217")
    await ctx.send(embed=embed)


"""
@client.command()
@commands.has_permissions(kick_members=True)
async def manualreport(ctx, user_name, user_ID,  *report):

    full_report = ''
    for word in report:
        full_report = full_report + word + ' '

    if full_report == '':
        await ctx.send('Please enter a reason for the report!')
    
    else:
        SAClient = gspread.authorize(SACreds)
        danger_sheet = SAClient.open('User Watchlist').worksheet('MainWatchlist')

        danger_sheet.append_row([str(user_name), str(user_ID), str(full_report), ctx.message.guild.name])

        admin_channel = discord.utils.get(client.get_all_channels(), guild__name='Media Server Admins', name='users-watchlist')
        embed = discord.Embed(title="Guard Alert", description=f"For {str(user_name)}", color=0xff0000)
        embed.add_field(name=f"Report manually submitted by {ctx.message.guild.name}", value=str(full_report), inline=False)
        await admin_channel.send(embed=embed)

        await ctx.send('Report sent!')
"""

@client.command()
@commands.has_permissions(kick_members=True)
async def manualreport(ctx):
    if(ctx.message.author.id == 819814204088385556):
        return
  
    def check(message):
        return message.author == ctx.author and message.channel == ctx.message.channel





    user_name_embed = discord.Embed(
        title = "Type the name of the user (Ex: SadFarm1#3217)",
        color = 0x009933
    )
    
    user_name_msg = await ctx.send(embed=user_name_embed)

    try:
        user_name = await client.wait_for('message', check=check, timeout=30)

        if '#' not in user_name.content:
            await ctx.send('Invalid username! Please try running this command again')
            return
    except asyncio.TimeoutError: 
        await ctx.send('Request timed out! Please try running this commmand again')
        return




    user_id_embed = discord.Embed(
        title = "Type the ID of the user (Ex: 453959267347595276)",
        color = 0x009933
    )

    user_id_msg = await ctx.send(embed=user_id_embed)

    try:
        user_id = await client.wait_for('message', check=check, timeout=30)
    except asyncio.TimeoutError: 
        await ctx.send('Request timed out! Please try running this commmand again')
        return


    
    user_report_embed = discord.Embed(
        title = "Type report for the user (Ex: Scammer)",
        color = 0x009933
    )

    user_report_msg = await ctx.send(embed=user_report_embed)

    try:
        user_report = await client.wait_for('message', check=check, timeout=30)
    except asyncio.TimeoutError: 
        await ctx.send('Request timed out! Please try running this commmand again')
        return
    

    user_name = user_name.content
    user_id = user_id.content
    user_report = user_report.content


    SAClient = gspread.authorize(SACreds)
    danger_sheet = SAClient.open('User Watchlist').worksheet('MainWatchlist')

    danger_sheet.append_row([str(user_name), str(user_id), str(user_report), ctx.message.guild.name])

    admin_channel = discord.utils.get(client.get_all_channels(), guild__name='Media Server Admins', name='users-watchlist')
    embed = discord.Embed(title="Guard Alert", description=f"For {str(user_name)} ``{str(user_id)}``", color=0xff0000)
    embed.add_field(name=f"Report manually submitted by {ctx.message.guild.name}", value=str(user_report), inline=False)
    await admin_channel.send(embed=embed)

    await ctx.send('Report sent!')

    


@client.command()
@commands.has_permissions(kick_members=True)
async def report(ctx):
    if(ctx.message.author.id == 819814204088385556):
        return

    def check(message):
        return message.author == ctx.author and message.channel == ctx.message.channel



    user_tag_embed = discord.Embed(
        title = "Ping the user (Ex: @SadFarm1)",
        color = 0x009933
    )
    
    user_tag_msg = await ctx.send(embed=user_tag_embed)
    try:
        user_tag = await client.wait_for('message', check=check, timeout=30)

        if '@' not in user_tag.content:
            await ctx.send('Invalid tag! Please try running this command again')
            return
        else:
            user_id = getID(user_tag.content)
            user_name = str(client.get_user(user_id))


    except asyncio.TimeoutError: 
        await ctx.send('Request timed out! Please try running this commmand again')
        return


    
    user_report_embed = discord.Embed(
        title = "Type report for the user (Ex: Scammer)",
        color = 0x009933
    )

    user_report_msg = await ctx.send(embed=user_report_embed)

    try:
        user_report = await client.wait_for('message', check=check, timeout=30)
    except asyncio.TimeoutError: 
        await ctx.send('Request timed out! Please try running this commmand again')
        return
    

    user_report = user_report.content


    SAClient = gspread.authorize(SACreds)
    danger_sheet = SAClient.open('User Watchlist').worksheet('MainWatchlist')

    danger_sheet.append_row([str(user_name), str(user_id), str(user_report), ctx.message.guild.name])

    admin_channel = discord.utils.get(client.get_all_channels(), guild__name='Media Server Admins', name='users-watchlist')
    embed = discord.Embed(title="Guard Alert", description=f"For {str(user_name)} ``{str(user_id)}``", color=0xff0000)
    embed.add_field(name=f"Report manually submitted by {ctx.message.guild.name}", value=str(user_report), inline=False)
    await admin_channel.send(embed=embed)

    await ctx.send('Report sent!')





@report.error
async def report_error(ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
                await ctx.send("Please tag a user to report them!")


@client.command()
async def invite(ctx):
    await ctx.send('https://discord.com/oauth2/authorize?client_id=730092804839309386&permissions=2064&scope=bot')


@client.command()
async def scan(ctx):


    await ctx.send('Scan initiated! This may take a bit.')

    guild = ctx.message.guild

    member_list = []

    
    
    for member in guild.members:
        print(str(member))
        member_list.append(str(member))

    SAClient = gspread.authorize(SACreds)
    danger_sheet = SAClient.open('User Watchlist').worksheet('MainWatchlist')


    danger_usernames = [item for item in danger_sheet.col_values(1) if item]

    danger_usernames_final = []
    [danger_usernames_final.append(x) for x in danger_usernames if x not in danger_usernames_final]

    for user_name in danger_usernames_final:
        reports = []
        servers = []
        user_id = 0

        if user_name in member_list:
            danger_cells = danger_sheet.findall(str(user_name))
            for cell in danger_cells:
                row = cell.row
                servers.append(danger_sheet.cell(row, 4).value)
                reports.append(danger_sheet.cell(row, 3).value)
                user_id = danger_sheet.cell(row, 2).value
                

            embed = discord.Embed(title="Guard Alert", description=f"Scan Report for {user_name} ``{user_id}``", color=0xff0000)

            i = 0
            for report in reports:
                
                embed.add_field(name=f"Report from {servers[i]}", value=report, inline=False)
                i += 1
                
            await ctx.send(embed=embed)

    await ctx.send("Scan Complete!")



@client.event
async def on_member_join(member):

    if member.guild.id == 644642197026897933:
        admin_channel = discord.utils.get(client.get_all_channels(), guild__name='Media Server Admins', name='verify')
        message = "Welcome to the **Media Server Admins Server**!\n\nSomeone has invited you here because they believe you have the necessary knowledge to contribute to the server. To make sure this is the case, we must first verify you.\n\nPlease provide the following:\n1) Name of Service & short description\n2) How long your service has been active\n3) Are you a reseller? (Do you manage your own content)\n4) Discord link to your service\n\nThank you for cooperation and we will be with your shortly!"
        await admin_channel.send(message)

    SAClient = gspread.authorize(SACreds)
    danger_sheet = SAClient.open('User Watchlist').worksheet('MainWatchlist')
    
    username = str(member)
    reports = []
    servers = []


    danger_cell = danger_sheet.findall(str(member))


    if len(danger_cell) > 0:

    
        for cell in danger_cell:
            row = cell.row

            reports.append(danger_sheet.cell(row, 3).value)
            servers.append(danger_sheet.cell(row, 4).value)


        channel = discord.utils.get(client.get_all_channels(), guild__name=str(member.guild), name='guard-alerts')

        embed = discord.Embed(title="Guard Alert", description=f"For {username}", color=0xff0000)

        i=0
        for report in reports:
            embed.add_field(name=f"Report from {servers[i]}", value=report, inline=False)
            embed.set_footer(text="Made with love by SadFarm1#3217")
            i+=1


        await channel.send(embed=embed)
        




    else:
        pass


        

client.run(os.getenv('DISCORD_KEY'))

#!/usr/bin/env python3

import os
from datetime import datetime, date
import time
from zoneinfo import ZoneInfo
import json
import re
from dotenv import load_dotenv

# import yaml
import random
import discord
from discord.ext import commands
from google.oauth2 import service_account
from google.cloud import compute_v1, firestore

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
sched = AsyncIOScheduler()
sched.start()

load_dotenv()

# GCP Authentication Setup (Minecraft)
json_acct_info = json.loads(os.getenv('GCP_CREDS_JSON_MINECRAFT'))
credentials = service_account.Credentials.from_service_account_info(
    json_acct_info)
scoped_credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/cloud-platform'])
instances_client_minecraft = compute_v1.InstancesClient(credentials=scoped_credentials)
operations_client_minecraft = compute_v1.ZoneOperationsClient(
    credentials=scoped_credentials)

# GCP Authentication Setup (Factorio)
json_acct_info = json.loads(os.getenv('GCP_CREDS_JSON_FACTORIO'))
credentials = service_account.Credentials.from_service_account_info(
    json_acct_info)
scoped_credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/cloud-platform'])
instances_client_factorio = compute_v1.InstancesClient(credentials=scoped_credentials)
operations_client_factorio = compute_v1.ZoneOperationsClient(
    credentials=scoped_credentials)

intents = discord.Intents(guilds=True, guild_messages=True, members=True)
bot = commands.Bot(command_prefix="!", intents=intents)
MAX_LENGTH = 60

# with open("config.yaml") as f:
#    """
#    config.yaml
#
#    bot_token: <bot-token>
#    guild_id: <guild-id>
#    """
#    config = yaml.load(f, Loader=yaml.FullLoader)
#    BOT_TOKEN = config["bot_token"]
#    GUILD_ID = config["guild_id"]


BOT_TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")


@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.id == GUILD_ID:
            break
    print(f"{bot.user} is connected to: {guild.name}(id: {guild.id})")

    await bot.change_presence(activity=discord.Game(name="with life (!summon_bot)"))


@bot.command(name="summon_bot")
async def summon_bot(ctx):
    reply = discord.Embed(color=discord.Color.green())
    reply.title = "How to summon?"
    reply.description = """
    Summon:
        - `!summon @username [mode]`

        - mode:
            - `0`: CALL (3 times) -> default
            - `1`: SHOUT (7 times)
            - `2`: SCREAM (15 times)

        - Frustrated? Just kill them: `!kill @username`

    Others:
        - `genius <n>`: The genius we all love (n times, no limits)
        - `heart`: Heart of the genius
        - `wall`: Wall of the genius
        - `heart_wall`: Wall of the heart of the genius
        - `mstart`: Start the minecraft server
        - `mstop`: Stop the minecraft server
        - `mstatus`: Get the status of minecraft server
        - `fstart`: Start the factorio server
        - `fstop`: Stop the factorio server
        - `fstatus`: Get the status of factorio server
    """

    await ctx.channel.send(embed=reply)


@bot.command(name="kill")
async def kill(ctx, call_user: str = None):
    user_ids = []
    for member in ctx.guild.members:
        user_ids.append(f"{member.id}")
    call_user_id = call_user[3:-1]

    if call_user_id in user_ids:
        reply = discord.Embed()
        gifs = [
            "https://media.giphy.com/media/xTcnTjeH5rtf6bdlwA/giphy.gif",
            "https://media.giphy.com/media/xUPGcdlIDdjwxbjrO0/giphy.gif",
            "https://media.giphy.com/media/yNFjQR6zKOGmk/giphy.gif",
        ]
        reply.set_image(url=random.choice(gifs))
        reply.title = f"Mode: KILL"

        await ctx.send(embed=reply)
        await ctx.send(call_user)
    else:
        reply = discord.Embed(color=discord.Color.red())
        reply.description = "Can you kill someone from this server?"
        reply.title = "FOOL SPOTTED"
        await ctx.send(embed=reply)


@bot.command(name="genius")
async def genius(ctx, times: int = 1):
    emojis_list = bot.emojis
    send_emoji_name = "noclue"
    for emoji in emojis_list:
        if emoji.name == send_emoji_name:
            if times <= 0:
                times = 1
            blocks = times // MAX_LENGTH
            rem = times % MAX_LENGTH
            # make MAX_LENGTH emoji blocks
            stich_60 = ""
            for _ in range(MAX_LENGTH):
                stich_60 += f"{emoji}"
            # send MAX_LENGTH emoji blocks
            for _ in range(blocks):
                await ctx.send(stich_60)
            # send rest
            stich = ""
            for _ in range(rem):
                stich += f"{emoji}"
            await ctx.send(stich)


@bot.command(name="wall")
async def wall(ctx):
    await genius(ctx, times=MAX_LENGTH * 10)


@bot.command(name="heart")
async def heart(ctx):
    emojis_list = bot.emojis
    send_emoji_name = "noclue"
    heart = ""
    for emoji in emojis_list:
        if emoji.name == send_emoji_name:
            emoji_str = f"{emoji}" + " "
            blank_code_2 = "`  `" + " "
            # fmt: off
            custom_matrix = [
                [blank_code_2, emoji_str, emoji_str, blank_code_2,
                    emoji_str, emoji_str, blank_code_2],
                [emoji_str, blank_code_2, blank_code_2, emoji_str,
                    blank_code_2, blank_code_2, emoji_str],
                [emoji_str, blank_code_2, blank_code_2, blank_code_2,
                    blank_code_2, blank_code_2, emoji_str],
                [blank_code_2, emoji_str, blank_code_2, blank_code_2,
                    blank_code_2, emoji_str, blank_code_2],
                [blank_code_2, blank_code_2, emoji_str, blank_code_2,
                    emoji_str, blank_code_2, blank_code_2],
                [blank_code_2, blank_code_2, blank_code_2, emoji_str,
                    blank_code_2, blank_code_2, blank_code_2],
            ]
            # fmt: on
            for line in custom_matrix:
                heart = ""
                for sym in line:
                    heart += sym
                # weird discord
                heart += "."
                await ctx.send(heart)


@bot.command(name="heart_wall")
async def heart_wall(ctx):
    emojis_list = bot.emojis
    send_emoji_name = "noclue"
    heart = ""
    for emoji in emojis_list:
        if emoji.name == send_emoji_name:
            emoji_str = f"{emoji}" + " "
            blank_code_2 = "`  `" + " "
            # fmt: off
            custom_matrix = [
                [blank_code_2, emoji_str, emoji_str, blank_code_2,
                    emoji_str, emoji_str, blank_code_2],
                [emoji_str, blank_code_2, blank_code_2, emoji_str,
                    blank_code_2, blank_code_2, emoji_str],
                [emoji_str, blank_code_2, blank_code_2, blank_code_2,
                    blank_code_2, blank_code_2, emoji_str],
                [blank_code_2, emoji_str, blank_code_2, blank_code_2,
                    blank_code_2, emoji_str, blank_code_2],
                [blank_code_2, blank_code_2, emoji_str, blank_code_2,
                    emoji_str, blank_code_2, blank_code_2],
                [blank_code_2, blank_code_2, blank_code_2, emoji_str,
                    blank_code_2, blank_code_2, blank_code_2],
            ]
            # fmt: on
            for _ in range(3):
                for line in custom_matrix:
                    heart = ""
                    for sym in line:
                        heart += sym
                    # weird discord
                    heart += "."
                    heart = heart * 3  # 3 times
                    await ctx.send(heart)


@bot.command(name="summon")
async def summon(ctx, call_user: str = None, level: int = 0):
    user_ids = []
    for member in ctx.guild.members:
        user_ids.append(f"{member.id}")
    call_user_id = re.findall("[0-9]+", call_user)[0]

    number = 3
    strs = [f"Yo! {call_user}", f"Hey! {call_user}", f"Listen! {call_user}"]
    reply = discord.Embed(color=discord.Color.purple())
    reply.description = "Calling..."
    reply.title = "Mode: CALL"
    if level == 1:
        number = 7
        strs = [
            f"COME ONLINE!!! {call_user}",
            f"WAKE UP!!! {call_user}",
            f"REPLY ASAP!!! {call_user}",
        ]
        reply = discord.Embed(color=discord.Color.orange())
        reply.description = "SHOUTING..."
        reply.title = "Mode: SHOUT"
    elif level == 2:
        number = 15
        strs = [
            f"WHY AREN'T YOU ONLINE, YOU DUMB FUCK? {call_user}",
            f"WHAT THE HELL IS THE MATTER WITH YOU, YOU TWAT? {call_user}",
            f"YOU ARE A HORRIBLE PERSON! {call_user}",
        ]
        reply = discord.Embed(color=discord.Color.red())
        reply.description = "SCREAMING!!!"
        reply.title = "Mode: SCREAM"

    await ctx.send(embed=reply)

    if call_user_id in user_ids:
        reply = random.choice(strs)
        for _ in range(number):
            await ctx.send(reply)
    else:
        reply = discord.Embed(color=discord.Color.red())
        reply.description = "Whom do I call again?"
        reply.title = "FOOL SPOTTED"
        await ctx.send(embed=reply)


# Minecraft Commands
minecraft_project_id = "test-salad-2125"


@bot.command(name='mstatus')
async def mstatus(ctx):
    minecraft_server_status = instances_client_minecraft.get(
        project=minecraft_project_id, zone='asia-south1-a', instance='minecraft')

    reply = discord.Embed()
    reply.title = "Meincraft Bois"
    if (minecraft_server_status.status
            == compute_v1.Instance.Status.TERMINATED):
        reply.color = discord.Color.red()
        reply.description = "Server has stopped."
    elif (minecraft_server_status.status
          == compute_v1.Instance.Status.STOPPED):
        reply.color = discord.Color.red()
        reply.description = "Server has stopped."
    elif (minecraft_server_status.status
          == compute_v1.Instance.Status.STOPPING):
        reply.color = discord.Color.red()
        reply.description = "Server is stopping."
    elif (minecraft_server_status.status
          == compute_v1.Instance.Status.SUSPENDED):
        reply.color = discord.Color.red()
        reply.description = "Server is suspended."
    elif (minecraft_server_status.status
          == compute_v1.Instance.Status.SUSPENDING):
        reply.color = discord.Color.red()
        reply.description = "Server is suspending."
    elif (minecraft_server_status.status
          == compute_v1.Instance.Status.RUNNING):
        reply.color = discord.Color.green()
        reply.description = f"Server is running (IP: {minecraft_server_status.network_interfaces[0].access_configs[0].nat_i_p})!"
    else:
        reply.color = discord.Color.orange()
        reply.description = "No instance found. Try deploying using the terraform repo again."

    await ctx.send(embed=reply)


@bot.command(name='mstart')
async def mstart(ctx):
    start_result = instances_client_minecraft.start(
        project='test-salad-2125', zone='asia-south1-a', instance='minecraft')
    reply_start = discord.Embed()
    reply_start.title = "Meincraft Bois"
    if (start_result.error):
        reply_start.color = discord.Color.red()
        reply_start.description = start_result.error.errors[0].message

    reply_start.color = discord.Color.green()

    count_start = 0
    operation_start = operation_status_minecraft(start_result.id)
    while(operation_start.status != compute_v1.types.Operation.Status.DONE):
        reply_start.description = f"Starting server... ({count_start * 5} seconds elapsed)"
        count_start += 1
        await ctx.send(embed=reply_start)
        time.sleep(5)
        operation_start = operation_status_minecraft(start_result.id)

    reply_start.color = discord.Color.green()
    reply_start.description = "Server started!"

    await ctx.send(embed=reply_start)
    await mstatus(ctx)


@bot.command(name='mstop')
async def mstop(ctx):
    stop_result = instances_client_minecraft.stop(
        project='test-salad-2125', zone='asia-south1-a', instance='minecraft')
    reply_stop = discord.Embed()
    reply_stop.title = "Meincraft Bois"
    if (stop_result.error):
        reply_stop.color = discord.Color.red()
        reply_stop.description = stop_result.error.errors[0].message
        await ctx.send(embed=reply_stop)

    reply_stop.color = discord.Color.green()

    count_stop = 0
    operation_stop = operation_status_minecraft(stop_result.id)
    while(operation_stop.status != compute_v1.types.Operation.Status.DONE):
        reply_stop.description = f"Stopping server... ({count_stop * 5} seconds elapsed)"
        count_stop += 1
        await ctx.send(embed=reply_stop)
        time.sleep(5)
        operation_stop = operation_status_minecraft(stop_result.id)

    reply_stop.description = "Server stopped."

    await ctx.send(embed=reply_stop)


def operation_status_minecraft(operation):
    return operations_client_minecraft.get(
        project=minecraft_project_id, zone='asia-south1-a', operation=operation)


# Factorio Commands
factorio_project_id = "striking-effort-335611"


@bot.command(name='fstatus')
async def fstatus(ctx):
    factorio_server_status = instances_client_factorio.get(
        project=factorio_project_id, zone='asia-south1-a', instance='factorio')

    reply = discord.Embed()
    reply.title = "Factorio Bois"
    if (factorio_server_status.status
            == compute_v1.Instance.Status.TERMINATED):
        reply.color = discord.Color.red()
        reply.description = "Server has stopped."
    elif (factorio_server_status.status
          == compute_v1.Instance.Status.STOPPED):
        reply.color = discord.Color.red()
        reply.description = "Server has stopped."
    elif (factorio_server_status.status
          == compute_v1.Instance.Status.STOPPING):
        reply.color = discord.Color.red()
        reply.description = "Server is stopping."
    elif (factorio_server_status.status
          == compute_v1.Instance.Status.SUSPENDED):
        reply.color = discord.Color.red()
        reply.description = "Server is suspended."
    elif (factorio_server_status.status
          == compute_v1.Instance.Status.SUSPENDING):
        reply.color = discord.Color.red()
        reply.description = "Server is suspending."
    elif (factorio_server_status.status
          == compute_v1.Instance.Status.RUNNING):
        reply.color = discord.Color.green()
        reply.description = f"Server is running (IP: {factorio_server_status.network_interfaces[0].access_configs[0].nat_i_p})!"
    else:
        reply.color = discord.Color.orange()
        reply.description = "No instance found. Try deploying using the terraform repo again."

    await ctx.send(embed=reply)


@bot.command(name='fstart')
async def fstart(ctx):
    reply_start = discord.Embed()
    reply_start.title = "Factorio Bois"

    stats = firestore.Client().collection('servers').document('factorio').get()
    if not stats.exists:
        firestore.Client().collection('servers').document('factorio').set({
            'time_played': 0,
            'date_tracked': datetime.now(ZoneInfo('Asia/Kolkata')),
        })
        time_played = 0
        date_tracked = datetime.now(ZoneInfo('Asia/Kolkata'))
    else:
        time_played = stats.to_dict()['time_played']
        date_tracked = stats.to_dict()['date_tracked'].astimezone(ZoneInfo('Asia/Kolkata'))
    today = datetime.now(ZoneInfo('Asia/Kolkata'))
    if (date(today.year, today.month, today.day) - date(date_tracked.year, date_tracked.month, date_tracked.day)).days != 0:
        firestore.Client().collection('servers').document('factorio').set({
            'time_played': 0,
            'date_tracked': datetime.now(ZoneInfo('Asia/Kolkata')),
        })
        time_played = 0
        date_tracked = datetime.now(ZoneInfo('Asia/Kolkata'))
    if time_played == 120:
        reply_start.color = discord.Color.red()
        reply_start.description = "You have reached the maximum time limit of 2 hours."
        await ctx.send(embed=reply_start)
        return

    start_result = instances_client_factorio.start(
        project=factorio_project_id, zone='asia-south1-a', instance='factorio')
    if (start_result.error):
        reply_start.color = discord.Color.red()
        reply_start.description = start_result.error.errors[0].message

    reply_start.color = discord.Color.green()

    count_start = 0
    operation_start = operation_status_factorio(start_result.id)
    while(operation_start.status != compute_v1.types.Operation.Status.DONE):
        reply_start.description = f"Starting server... ({count_start * 5} seconds elapsed)"
        count_start += 1
        await ctx.send(embed=reply_start)
        time.sleep(5)
        operation_start = operation_status_factorio(start_result.id)

    sched.add_job(
        func=factorio_addiction_control,
        args=[ctx],
        trigger='interval',
        minutes=1,
        id='factorio_addiction_control',
        replace_existing=True)

    reply_start.color = discord.Color.green()
    reply_start.description = "Server started!"
    await ctx.send(embed=reply_start)
    await fstatus(ctx)


@bot.command(name='fstop')
async def fstop(ctx):
    try:
        sched.remove_job('factorio_addiction_control')
    except JobLookupError:
        pass

    stop_result = instances_client_factorio.stop(
        project=factorio_project_id, zone='asia-south1-a', instance='factorio')
    reply_stop = discord.Embed()
    reply_stop.title = "Factorio Bois"
    if (stop_result.error):
        reply_stop.color = discord.Color.red()
        reply_stop.description = stop_result.error.errors[0].message
        await ctx.send(embed=reply_stop)

    reply_stop.color = discord.Color.green()

    count_stop = 0
    operation_stop = operation_status_factorio(stop_result.id)
    while(operation_stop.status != compute_v1.types.Operation.Status.DONE):
        reply_stop.description = f"Stopping server... ({count_stop * 5} seconds elapsed)"
        count_stop += 1
        await ctx.send(embed=reply_stop)
        time.sleep(5)
        operation_stop = operation_status_factorio(stop_result.id)

    reply_stop.description = "Server stopped."

    await ctx.send(embed=reply_stop)


def operation_status_factorio(operation):
    return operations_client_factorio.get(
        project=factorio_project_id, zone='asia-south1-a', operation=operation)


async def factorio_addiction_control(ctx):
    stats = firestore.Client().collection('servers').document('factorio').get()
    time_played = stats.to_dict()['time_played'] + 1
    factorio_role_id_list = [role.mention for role in ctx.guild.roles if role.name == 'factorio']
    factorio_role_id = factorio_role_id_list[0] if len(factorio_role_id_list) > 0 else 'Factorio Bois'
    if time_played == 120 - 5:
        await ctx.send(f"{factorio_role_id}, you have 5 minutes of playtime remaining.")
    elif time_played == 120 - 10:
        await ctx.send(f"{factorio_role_id}, you have 10 minutes of playtime remaining.")
    elif time_played == 120 - 15:
        await ctx.send(f"{factorio_role_id}, you have 15 minutes of playtime remaining.")
    if time_played == 120:
        await ctx.send(f"{factorio_role_id}, stopping the server now.")
        firestore.Client().collection('servers').document('factorio').update({
            'time_played': 120,
        })
        await fstop(ctx)
        sched.remove_job('factorio_addiction_control')
        return
    firestore.Client().collection('servers').document('factorio').update({
        'time_played': firestore.Increment(1),
    })


bot.run(BOT_TOKEN)

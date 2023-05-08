import discord
from discord.ext import commands
from discord.utils import get
from youtube_dl import YoutubeDL
import requests
import sqlite3
import datetime
import time


config = {
    "token": "MTA5NDE4MDE4Mzc0Mjg5NDA4MA.G3Pk1M.NyhrvaZSjHyke3oCL1kEdgNaZgyfNpX1wWCV2c",
    "BOTNAME": "INFYS",
    "ID": 1094180183742894080,
    "prefix": "8"
}
YDL_OPTIONS = {'format': 'worstaudio/best', 'noplaylist': 'False', 'simulate': 'True', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

connection = sqlite3.connect("server.db")
cursor = connection.cursor()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config["prefix"], intents=intents)


@bot.event
async def on_ready():
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    name TEXT,
    server INTEGER,
    id INTEGER,
    cash INTEGER,
    exp_v INTEGER,
    exp_m INTEGER,
    lvl INTEGER
    )
    """)
    for guild in bot.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cursor.execute(f"INSERT INTO users VALUES ('{member}',{member.guild.id} ,{member.id}, 1000, 0, 0, 0)")
            if cursor.execute(f"SELECT server FROM users WHERE id = {member.id}").fetchone()[0] != member.guild.id:
                cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.guild.id}, {member.id}, 1000, 0, 0, 0)")
            else:
                pass
connection.commit()


@bot.event
async def on_member_join(member):
    if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.guild.id}, {member.id}, 1000, 0, 0, 0)")
        connection.commit()
    else:
        pass


@bot.command()
async def voice_exp(ctx):
    await ctx.send(f"""Ваш опыт: {cursor.execute(f"SELECT exp_v FROM users WHERE id = {ctx.author.id} AND server = {ctx.guild.id}").fetchone()[0]}""")
    print("dd")


@bot.command()
async def text_exp(ctx):
    await ctx.send(f"""Ваш опыт: {cursor.execute(f"SELECT exp_m FROM users WHERE id = {ctx.author.id} AND server = {ctx.guild.id}").fetchone()[0]}""")
    print("dd")


@bot.command()
async def info(ctx, *arg):
    await ctx.send("8dog - return random dog image\n8cat - return random cat image\n8gif - return random gif\n8play 'youtube url' or 'song name' - listen music with your friends\n8stop - stop listening music")


@bot.command()
async def balance(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send(embed=discord.Embed(
            description=f"""Баланс пользователя {ctx.author} составляет {cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id} AND server = {ctx.guild.id}").fetchone()[0]}$"""
        ))
        print(ctx.guild.name)
    else:
        await ctx.send(embed=discord.Embed(
            description=f"""Баланс пользователя {member} составляет {cursor.execute(f"SELECT cash FROM users WHERE id = {member.id} AND server = {member.guild.id}").fetchone()[0]}$"""
        ))


@bot.command()
async def add_money(ctx, member: discord.Member = None, amount: int = None):
    if member is None:
        await ctx.send(f"{ctx.author}, укажите пользователя, которому начисляете определённую сумму")
    else:
        if amount is None:
            await ctx.send(f"{ctx.author}, укажите сумму начисления")
        elif amount < 1:
            await ctx.send(f"{ctx.author}, укажите сумму большую 1$")
        else:
            cursor.execute(f"UPDATE users SET cash = cash + {amount} WHERE id = {member.id} AND server = {member.guild.id}")
            connection.commit()
            await ctx.send(f"{ctx.author}, начисление пользователю {member} {amount}$ прошло успешно!")


@bot.command()
async def pay(ctx, member: discord.Member = None, amount: int = None):
    if member is None:
        await ctx.send(f"{ctx.author}, укажите пользователя, которому перечисляете определённую сумму")
    else:
        if amount is None:
            await ctx.send(f"{ctx.author}, укажите сумму начисления")
        elif amount < 1:
            await ctx.send(f"{ctx.author}, укажите сумму большую 1$")
        elif amount > cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id} AND server = {ctx.guild.id}").fetchone()[0]:
            await ctx.send(f"{ctx.author}, у вас недостаточно средств")
        else:
            cursor.execute(f"UPDATE users SET cash = cash + {amount} WHERE id = {member.id} AND server = {member.guild.id}")
            cursor.execute(f"UPDATE users SET cash = cash - {amount} WHERE id = {ctx.author.id} AND server = {ctx.guild.id}")
            connection.commit()
            await ctx.send(f"{ctx.author}, перечисление пользователю {member} {amount}$ прошло успешно!")
            await ctx.send(f"""Ваш баланс: {cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id} AND server = {ctx.guild.id}").fetchone()[0]}$""")


@bot.command(pass_context=True)
async def dog(ctx):
    emb = discord.Embed(title="_Your Dog_", colour=discord.Color.gold())

    emb.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    emb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar)

    req = requests.get(url='https://dog.ceo/api/breeds/image/random').json()['message']
    emb.set_image(url=req)
    emb.set_thumbnail(url="https://media.discordapp.net/attachments/787399310231994429/1079858961244754011/ShOtnik__19_inevitably_a0dfb39b-b8b2-47f3-8e57-60441f994202.png?width=910&height=910")

    await ctx.send(embed=emb)


@bot.command(pass_context=True)
async def cat(ctx):
    emb = discord.Embed(title="_Your Cat_", colour=discord.Color.gold())

    emb.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    emb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar)

    req = requests.get(url="https://api.thecatapi.com/v1/images/search").json()[0]['url']
    emb.set_image(url=req)
    emb.set_thumbnail(url="https://media.discordapp.net/attachments/787399310231994429/1079858961244754011/ShOtnik__19_inevitably_a0dfb39b-b8b2-47f3-8e57-60441f994202.png?width=910&height=910")

    await ctx.send(embed=emb)


@bot.command(pass_context=True)
async def gif(ctx):
    emb = discord.Embed(title="_Your GIF_", colour=discord.Color.gold())

    emb.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    emb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar)

    params = {
        'api_key': 'rmJJGzW28a0N6ga0YxZ6oDwHkeL9JQhz',
    }

    req = requests.get(url='https://api.giphy.com/v1/gifs/random', params=params).json()['data']['images']['fixed_height']['url']

    emb.set_image(url=req)
    emb.set_thumbnail(url="https://media.discordapp.net/attachments/787399310231994429/1079858961244754011/ShOtnik__19_inevitably_a0dfb39b-b8b2-47f3-8e57-60441f994202.png?width=910&height=910")

    await ctx.send(embed=emb)


@bot.command()
async def play(ctx, url):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
    vc = await ctx.message.author.voice.channel.connect()

    with YoutubeDL(YDL_OPTIONS) as ydl:
        if 'https://' in url:
            if "playlist" in url:
                info = ydl.extract_info(url, download=False)['entries'][0]
                for i in info:
                    print(i)
            else:
                info = ydl.extract_info(url, download=False)
        else:
            info = ydl.extract_info(f"ytsearch: {url}", download=False)['entries'][0]

        link = info['formats'][0]['url']

        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=link, **FFMPEG_OPTIONS))


@bot.event
async def on_voice_state_update(member, before, after):
    global t1l
    if before.channel is None and after.channel is not None:
        if member.voice.channel != member.guild.afk_channel:
            t1l = int(time.time() * 1000)
    elif before.channel is not None and after.channel is None:
                t2l = int(time.time() * 1000)
                print(datetime.datetime.now(), " ", t2l)
                if t1l is None:
                    t1l = 0
                td = [t2l, t1l]
                if td[0] - td[1] > 0:
                    print("l")
                    cursor.execute(f"UPDATE users SET exp_v = exp_v + {(td[0] - td[1]) // 1000} WHERE id = {member.id} AND server = {member.guild.id}")
                    connection.commit()


@bot.command()
async def join(ctx):
   global voice

   channel = ctx.message.author.voice.channel
   voice = get(bot.voice_clients, guild=ctx.guild)

   if voice and voice.is_connected():
        await voice.move_to(channel)
   else:
       voice = await channel.connect()
       await ctx.send(f"Бот присоединился к каналу: {channel}")


@bot.command()
async def stop(ctx):
   channel = ctx.message.author.voice.channel
   voice = get(bot.voice_clients, guild=ctx.guild)
   if voice and voice.is_connected():
        await voice.disconnect()


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author != bot.user:
        cursor.execute(f"UPDATE users SET exp_m = exp_m + {int(1)} WHERE id = {message.author.id} AND server = {message.author.guild.id}")
        connection.commit()


bot.run(config['token'])
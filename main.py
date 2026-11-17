import os
import asyncio
import discord
from discord.ext import commands
import wavelink
from flask import Flask
from threading import Thread

# 1. إعداد سيرفر الويب باش Fly.io يلقى بورت مفتوح وما يطفيكش
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. إعدادات البوت والـ Intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    
    # ربط سيرفر Lavalink العام للصوت عالي الجودة
    try:
        node = wavelink.Node(uri='https://lavalink.darrennathanael.com', password='youshallnotpass')
        await wavelink.Pool.connect(nodes=[node], client=bot, cache_capacity=100)
        print("Connected to Lavalink Node successfully!")
    except Exception as e:
        print(f"Failed to connect to Lavalink: {e}")

@bot.command(name='play')
async def play(ctx: commands.Context, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("خاصك تكون داخل لشي قناة صوتية الأول!")

    player = ctx.voice_client
    if not player:
        try:
            channel = ctx.author.voice.channel
            player = await channel.connect(cls=wavelink.Player)
            
            # التحول التلقائي لمتحدث في الـ Stage Channel
            if channel.type == discord.ChannelType.stage_voice:
                await ctx.guild.me.edit(suppress=False)
                
        except Exception as e:
            return await ctx.send(f"ما قدرتش ندخل لقناة الصوت: {e}")

    tracks = await wavelink.Playable.search(search)
    if not tracks:
        return await ctx.send(f"ما لقيت حتى شي نتيجة لـ: **{search}**")

    track = tracks[0]
    await player.play(track)
    await ctx.send(f"🎶 خدامة دابا: **{track.title}**")

@bot.command(name='stop')
async def stop(ctx: commands.Context):
    player = ctx.voice_client
    if player:
        await player.disconnect()
        await ctx.send("⏹️ خرجت من القناة الصوتية.")
    else:
        await ctx.send("أصلاً أنا ماشي في شي قناة صوتية!")

# 3. التشغيل المتزامن للسيرفر والبوت
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.getenv("TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: TOKEN environment variable not found!")
        

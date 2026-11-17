import os
import discord
from discord.ext import commands
import wavelink
from threading import Thread
from flask import Flask

# 1. إنشاء سيرفر ويب مصغر (Flask) باش Fly.io يبقى مسجل بلي البوت خدام وما يطفيهش
app = Flask('')

@app.route('/')
def home():
    return "Bot is online and running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# 2. إعدادات بوت ديسكورد
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    
    # ربط سيرفر Lavalink العام (HD Audio)
    try:
        node = wavelink.Node(uri='https://lavalink.darrennathanael.com', password='youshallnotpass')
        await wavelink.Pool.connect(nodes=[node], client=bot, cache_capacity=100)
        print("Connected to Lavalink Node successfully!")
    except Exception as e:
        print(f"Failed to connect to Lavalink: {e}")

# أمر تشغيل الموسيقى مع التجاوز التلقائي للصوت في الـ Stage Channel
@bot.command(name='play')
async def play(ctx: commands.Context, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("خاصك تكون داخل لشي قناة صوتية (Voice Channel) الأول!")

    player = ctx.voice_client
    if not player:
        try:
            channel = ctx.author.voice.channel
            player = await channel.connect(cls=wavelink.Player)
            
            # إذا كانت القناة Stage Channel، خليه يتحول أوتوماتيكياً إلى متحدث (Speaker)
            if channel.type == discord.ChannelType.stage_voice:
                await ctx.guild.me.edit(suppress=False)
                
        except Exception as e:
            return await ctx.send(f"ما قدرتش ندخل لقناة الصوت أو نولي متحدث: {e}")

    # البحث عن الأغنية
    tracks = await wavelink.Playable.search(search)
    if not tracks:
        return await ctx.send(f"ما لقيت حتى شي نتيجة لـ: **{search}**")

    track = tracks[0]
    await player.play(track)
    await ctx.send(f"🎶 خدامة دابا في الـ Stage: **{track.title}**")

# أمر إيقاف البوت وخروجه من القناة
@bot.command(name='stop')
async def stop(ctx: commands.Context):
    player = ctx.voice_client
    if player:
        await player.disconnect()
        await ctx.send("⏹️ خرجت من القناة الصوتية.")
    else:
        await ctx.send("أصلاً أنا ماشي في شي قناة صوتية!")

# 3. تشغيل السيرفر المصغر مع البوت في نفس الوقت
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.getenv("TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: TOKEN environment variable not found!")
    

import os
import discord
from discord.ext import commands
import wavelink

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    
    # ربط سيرفر Lavalink بالطريقة الصحيحة والحديثة
    try:
        node = wavelink.Node(uri='https://lavalink.darrennathanael.com', password='youshallnotpass')
        await wavelink.Pool.connect(nodes=[node], client=bot)
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

    # البحث عن الأغنية
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

if __name__ == "__main__":
    TOKEN = os.getenv("TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: TOKEN environment variable not found!")
            

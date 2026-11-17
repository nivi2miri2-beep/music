import discord
from discord.ext import commands
import wavelink
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"البوت {bot.user} متصل وشغال!")
    
    # ربط البوت مع سيرفر Lavalink العام المجاني
    node = wavelink.Node(
        uri="https://lavalink.darrennathanael.com",
        password="youshallnotpass"
    )
    try:
        await wavelink.Pool.connect(nodes=[node], client=bot)
        print("تم الاتصال بـ Lavalink بنجاح 100%!")
    except Exception as e:
        print(f"خطأ في الاتصال بـ Lavalink: {e}")

@bot.command(name="play")
async def play(ctx: commands.Context, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("ادخل لقناة صوتية بالاول !")

    player: wavelink.Player = ctx.voice_client

    if not player:
        # الاتصال بالقناة (سواء صوتية عادية أو Stage، بشرط تكوني مفعلاها Speaker للبوت)
        player = await ctx.author.voice.channel.connect(cls=wavelink.Player)

    # البحث عن الأغنية
    tracks = await wavelink.Playable.search(search)
    if not tracks:
        return await ctx.send("لم اجد شيئا بهذا البحث!")

    track = tracks[0]
    await player.play(track)
    await ctx.send(f"شغال الان 🎵: **{track.title}**")

@bot.command(name="stop")
async def stop(ctx: commands.Context):
    player: wavelink.Player = ctx.voice_client
    if player:
        await player.disconnect()
        await ctx.send("تم الخروج من القناة وإيقاف الموسيقى.")
    else:
        await ctx.send("البوت لا يتواجد في اي قناة الان ا!")

# تشغيل البوت عبر التوكن الموجود في المتغيرات البيئية
bot.run(os.getenv("TOKEN"))

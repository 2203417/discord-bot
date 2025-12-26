import os
import discord
from discord.ext import commands, tasks
import requests
import threading

from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, DisconnectEvent

# ================== CONFIGURACIÓN ==================
KICK_USER = "jostrda"
TIKTOK_USER = "jostrda"
CANAL_ANUNCIOS = "《👾》directo"

# ================== INTENTS ==================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# ================== BOT ==================
bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ================== ESTADOS ==================
kick_anunciado = False
tiktok_anunciado = False
tiktok_live = False

# ================== KICK ==================
def check_kick_live(username: str) -> bool:
    url = f"https://kick.com/api/v2/channels/{username}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        return data.get("livestream") is not None
    except Exception as e:
        print("Kick error:", e)
        return False

@tasks.loop(minutes=2)
async def kick_loop():
    global kick_anunciado

    canal = discord.utils.get(bot.get_all_channels(), name=CANAL_ANUNCIOS)
    if not canal:
        return

    en_vivo = check_kick_live(KICK_USER)

    if en_vivo and not kick_anunciado:
        embed = discord.Embed(
            title="🔴 ¡DIRECTO EN KICK!",
            description=f"Ya estamos en vivo en **Kick**",
            color=0x53FC18
        )
        embed.add_field(
            name="🔗 Enlace",
            value=f"https://kick.com/{KICK_USER}",
            inline=False
        )

        await canal.send(embed=embed)
        kick_anunciado = True

    if not en_vivo:
        kick_anunciado = False

# ================== TIKTOK ==================
def start_tiktok_listener(username: str):
    global tiktok_live, tiktok_anunciado

    client = TikTokLiveClient(unique_id=username)

    @client.on(ConnectEvent)
    async def on_connect(event):
        global tiktok_live, tiktok_anunciado
        tiktok_live = True
        tiktok_anunciado = False
        print("🔴 TikTok LIVE detectado")

        canal = discord.utils.get(bot.get_all_channels(), name=CANAL_ANUNCIOS)
        if canal and not tiktok_anunciado:
            embed = discord.Embed(
                title="🔴 ¡DIRECTO EN TIKTOK!",
                description="Ya estamos en vivo en **TikTok**",
                color=0xFF0050
            )
            embed.add_field(
                name="🔗 Enlace",
                value=f"https://www.tiktok.com/@{TIKTOK_USER}",
                inline=False
            )

            await canal.send(embed=embed)
            tiktok_anunciado = True

    @client.on(DisconnectEvent)
    async def on_disconnect(event):
        global tiktok_live
        tiktok_live = False
        print("⚫ TikTok LIVE terminado")

    client.run()

def iniciar_tiktok():
    threading.Thread(
        target=start_tiktok_listener,
        args=(TIKTOK_USER,),
        daemon=True
    ).start()

# ================== EVENTOS ==================
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    kick_loop.start()
    iniciar_tiktok()

@bot.event
async def on_member_join(member):
    canal = discord.utils.get(
        member.guild.text_channels,
        name="《👾》bienvenida"
    )

    if canal:
        embed = discord.Embed(
            title="🎉 ¡Nuevo miembro!",
            description=f"Bienvenido {member.mention} a **{member.guild.name}**",
            color=0x00ffcc
        )

        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)

        embed.add_field(
            name="📌 Reglas",
            value="Por favor lee las reglas en #reglas",
            inline=False
        )

        embed.set_footer(text="Disfruta tu estancia 💙")

        await canal.send(embed=embed)

# ================== COMANDOS ==================
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command()
async def info(ctx):
    await ctx.send(
        f"👤 Usuario: {ctx.author}\n"
        f"🆔 ID: {ctx.author.id}\n"
        f"📆 Cuenta creada: {ctx.author.created_at.strftime('%d/%m/%Y')}"
    )

# ================== INICIO ==================
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("❌ ERROR: No se encontró DISCORD_TOKEN")
else:
    bot.run(TOKEN)

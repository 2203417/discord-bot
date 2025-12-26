import os
import discord
from discord.ext import commands

# ---------- INTENTS ----------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# ---------- BOT ----------
bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ---------- EVENTOS ----------
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.event
async def on_member_join(member):
    # 🔹 CANAL DE BIENVENIDA
    canal = discord.utils.get(member.guild.text_channels, name="《👾》bienvenida")

    
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

# ---------- COMANDOS ----------
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

# ---------- INICIO ----------
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("❌ ERROR: No se encontró DISCORD_TOKEN")
else:
    bot.run(TOKEN)

import discord
from discord.ext import commands
import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
WEBSOCKET_URL = os.getenv('WEBSOCKET_URL')
WEBSOCKET_TOKEN = os.getenv('WEBSOCKET_TOKEN')

WEBSOCKET_URL_WITH_TOKEN = f"{WEBSOCKET_URL}?token={WEBSOCKET_TOKEN}"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='-corinthians ', intents=intents)

def create_base_embed(author, record):
    embed = discord.Embed(
        title=author.get("displayName", "Usuário desconhecido"),
        description=record.get("text", ""),
        color=discord.Color.blue()
    )
    embed.set_author(
        name=author.get("handle", "Usuário desconhecido"),
        icon_url=author.get("avatar", "")
    )
    return embed

def handle_images_in_embed(embed, images):
    if images:
        first_image = images[0].get("fullsize", "")
        if first_image:
            embed.set_image(url=first_image)
        if len(images) > 1:
            second_image = images[1].get("fullsize", "")
            if second_image:
                embed.set_thumbnail(url=second_image)
    return embed

async def send_embed_message(channel, post):
    author = post.get('author', {})
    record = post.get('record', {})
    embed = create_base_embed(author, record)

    if "embed" in post:
        embed_data = post["embed"]
        if embed_data["$type"] == "app.bsky.embed.images#view":
            images = embed_data.get("images", [])
            embed = handle_images_in_embed(embed, images)
        elif embed_data["$type"] == "app.bsky.embed.external#view":
            external = embed_data.get("external", {})
            embed.set_author(name=author.get("displayName", "Autor desconhecido"))
            embed.title = external.get("title", "Sem título")
            embed.description = external.get("description", "Sem descrição")
            embed.set_thumbnail(url=external.get("thumb", ""))
            await send_external_embed(channel, embed, external)
            return

    await channel.send(embed=embed)

async def send_external_embed(channel, embed, external):
    class ExternalLinkView(discord.ui.View):
        def __init__(self, uri):
            super().__init__()
            self.add_item(discord.ui.Button(label="Ver mais", url=uri, style=discord.ButtonStyle.link))

    view = ExternalLinkView(uri=external.get("uri", "#"))
    await channel.send(embed=embed, view=view)

async def websocket_listener():
    async with websockets.connect(WEBSOCKET_URL_WITH_TOKEN) as websocket:
        while True:
            message = await websocket.recv()
            post = json.loads(message)
            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                await send_embed_message(channel, post)

@bot.event
async def on_ready():
    bot.loop.create_task(websocket_listener())
    print(f'{bot.user} está online e conectado ao Discord!')

# Função que retorna a tabela fictícia da Série A
@bot.command(name="tabela")
async def tabela(ctx):
    # Dados fictícios da tabela da Série A
    tabela_serie_a = """
    1. Botafogo - 59 pts
    2. Palmeiras - 50 pts
    3. Grêmio - 48 pts
    4. Flamengo - 47 pts
    5. Corinthians - 46 pts
    ...
    """

    embed = discord.Embed(title="Tabela - Série A", description=tabela_serie_a, color=discord.Color.green())
    await ctx.send(embed=embed)

# Função que retorna os próximos jogos fictícios do Corinthians
@bot.command(name="calendario")
async def calendario(ctx):
    # Dados fictícios dos próximos jogos do Corinthians
    proximos_jogos = """
    30/09 - Corinthians x Palmeiras
    04/10 - Corinthians x Flamengo
    08/10 - Corinthians x São Paulo
    15/10 - Corinthians x Internacional
    22/10 - Corinthians x Fluminense
    """

    embed = discord.Embed(title="Próximos jogos do Corinthians", description=proximos_jogos, color=discord.Color.red())
    await ctx.send(embed=embed)

bot.run(DISCORD_TOKEN)

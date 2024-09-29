import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv
from modules.standings import generate_standings_image, load_previous_standings, save_standings_json
from modules.calendar import generate_matches_list
from datetime import datetime, timedelta
import websockets
import json
import logging
import asyncio

logging.basicConfig(level=logging.INFO)

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
FOOTBALL_API_TOKEN = os.getenv('FOOTBALL_API_TOKEN')
WEBSOCKET_URL = os.getenv('WEBSOCKET_URL')
WEBSOCKET_TOKEN = os.getenv('WEBSOCKET_TOKEN')

WEBSOCKET_URL_WITH_TOKEN = f"{WEBSOCKET_URL}?token={WEBSOCKET_TOKEN}"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='-corinthians ', intents=intents)

@bot.event
async def on_ready():
    logging.info(f'{bot.user} está online!')

    # Criando a tarefa assíncrona para o WebSocket listener
    bot.loop.create_task(websocket_listener())  # Inicia o WebSocket automaticamente

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
    try:
        logging.info(f'Conectando ao WebSocket: {WEBSOCKET_URL_WITH_TOKEN}')
        async with websockets.connect(WEBSOCKET_URL_WITH_TOKEN) as websocket:
            logging.info('Conexão WebSocket estabelecida com sucesso.')
            while True:
                message = await websocket.recv()
                logging.info(f'Mensagem recebida do WebSocket: {message}')
                post = json.loads(message)
                channel = bot.get_channel(CHANNEL_ID)
                if channel:
                    await send_embed_message(channel, post)
    except websockets.ConnectionClosedError as e:
        logging.error(f'Conexão com WebSocket encerrada: {e}')
    except Exception as e:
        logging.error(f'Ocorreu um erro no WebSocket: {e}')


@bot.command(name="tabela")
async def tabela(ctx):
    async with ctx.typing():
        url = "https://api.football-data.org/v4/competitions/BSA/standings"
        headers = {"X-Auth-Token": FOOTBALL_API_TOKEN}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            standings = data['standings'][0]['table']
            previous_standings = load_previous_standings()

            image_path = generate_standings_image(standings, previous_standings)

            embed = discord.Embed(
                title="Tabela - Campeonato Brasileiro Série A",
                description="Confira a tabela atualizada do Brasileirão Série A.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=data['competition']['emblem'])

            with open(image_path, 'rb') as f:
                discord_image = discord.File(f, filename="tabela_brasileirao.png")
                embed.set_image(url="attachment://tabela_brasileirao.png")
                await ctx.send(file=discord_image, embed=embed)

            save_standings_json(standings)

        except requests.exceptions.RequestException as e:
            embed = discord.Embed(
                title="Erro ao buscar dados",
                description=f"Ocorreu um erro ao tentar acessar a API:\n```{str(e)}```",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)


@bot.command(name="calendario")
async def calendario(ctx):
    async with ctx.typing():
        url = "https://api.football-data.org/v4/teams/1779/matches?status=SCHEDULED"
        headers = {"X-Auth-Token": FOOTBALL_API_TOKEN}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            matches = data['matches']
            if not matches:
                await ctx.send("Nenhum jogo agendado encontrado.")
                return

            match_list = generate_matches_list(matches)

            embed = discord.Embed(
                title="Próximos jogos do Corinthians",
                description=match_list,
                color=discord.Color.dark_blue()
            )

            await ctx.send(embed=embed)

        except requests.exceptions.RequestException as e:
            embed = discord.Embed(
                title="Erro ao buscar dados",
                description=f"Ocorreu um erro ao tentar acessar a API:\n```{str(e)}```",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)


bot.run(DISCORD_TOKEN)

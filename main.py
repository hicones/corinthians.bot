import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv
from modules.standings import generate_standings_image, load_previous_standings, save_standings_json
from modules.calendar import generate_matches_list
from datetime import datetime, timedelta

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
FOOTBALL_API_TOKEN = os.getenv('FOOTBALL_API_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='-corinthians ', intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user} está online!')


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

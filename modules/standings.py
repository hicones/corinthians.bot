import json
import os
import imgkit
from .utils import image_to_base64, download_and_save_icon, compare_positions

def load_previous_standings():
    if os.path.exists("ultima_tabela.json"):
        with open("ultima_tabela.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_standings_json(standings):
    with open("ultima_tabela.json", "w", encoding="utf-8") as f:
        json.dump(standings, f, ensure_ascii=False, indent=4)


def generate_html_standings(standings, previous_standings):
    html = """
    <html>
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Sora', sans-serif;
                background-color: #fff;
                padding: 40px;
                color: #333;
            }
            h1 {
                font-size: 3rem;
                font-weight: 600;
                margin-bottom: 2rem;
                text-align: center;
                color: #111;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                text-align: left;
                background-color: #ffffff;
            }
            th, td {
                padding: 16px;
            }
            th {
                background-color: #6d28d9;
                text-transform: uppercase;
                font-size: 1.5rem;
                color: white;
            }
            td {
                font-size: 1.25rem;
                color: #333;
            }
            .team-flex {
                display: flex;
                align-items: center;
                justify-content: flex-start;
            }
            img {
                width: 48px;
                height: 48px;
                margin-right: 16px;
                vertical-align: middle;
            }
            .bg-gray {
                background-color: #f3f4f6;
            }
            .bg-red {
                background-color: #fef2f2;
            }
            .bg-white {
                background-color: #ffffff;
            }
            .bg-light-gray {
                background-color: #f9fafb;
            }
            .points-bold {
                font-weight: 700;
            }
            .pos-indicator {
                font-size: 1.5rem;
                margin-left: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-6xl font-bold mb-8">Campeonato Brasileiro Série A</h1>
            <div>
                <table>
                    <thead>
                        <tr class="bg-purple text-white">
                            <th>Pos</th>
                            <th>Time</th>
                            <th>Pts</th>
                            <th>J</th>
                            <th>V</th>
                            <th>E</th>
                            <th>D</th>
                            <th>G</th>
                            <th>G/S</th>
                            <th>S/G</th>
                        </tr>
                    </thead>
                    <tbody>
    """

    corinthians_tla = "COR"
    total_teams = len(standings)
    for index, team in enumerate(standings):
        position = team['position']
        short_name = team['team']['shortName'][:15]
        crest_base64 = image_to_base64(download_and_save_icon(team['team']['crest'], team['team']['id']))
        crest_img = f'data:image/png;base64,{crest_base64}'
        
        points = team['points']
        played_games = team['playedGames']
        won = team['won']
        draw = team['draw']
        lost = team['lost']
        goals_for = team['goalsFor']
        goals_against = team['goalsAgainst']
        goal_difference = team['goalDifference']

        pos_indicator = compare_positions(str(team['team']['id']), position, previous_standings)
        
        if team['team']['tla'] == corinthians_tla:
            row_class = 'bg-gray'
        elif position > total_teams - 4:
            row_class = 'bg-red'
        else:
            row_class = 'bg-white bg-light-gray'

        html += f"""
        <tr class="{row_class}">
            <td>{position}<span class="pos-indicator">{pos_indicator}</span></td>
            <td>
                <div class="team-flex">
                    <img src="{crest_img}" alt="{short_name} logo">
                    <span>{short_name}</span>  
                </div>
            </td>
            <td class="points-bold">{points}</td>
            <td>{played_games}</td>
            <td>{won}</td>
            <td>{draw}</td>
            <td>{lost}</td>
            <td>{goals_for}</td>
            <td>{goals_against}</td>
            <td>{goal_difference}</td>
        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def generate_standings_image(standings, previous_standings):
    html = generate_html_standings(standings, previous_standings)

    with open("tabela_brasileirao.html", "w", encoding="utf-8") as f:
        f.write(html)

    imgkit.from_file("tabela_brasileirao.html", "tabela_brasileirao.png")

    return "tabela_brasileirao.png"

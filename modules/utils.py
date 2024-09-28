import requests
import base64
import os

def image_to_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


def download_and_save_icon(url, team_id):
    if not os.path.exists("teams_icons"):
        os.makedirs("teams_icons")

    icon_path = os.path.join("teams_icons", f"{team_id}.png")

    if not os.path.exists(icon_path):
        response = requests.get(url)
        with open(icon_path, 'wb') as f:
            f.write(response.content)

    return icon_path


def compare_positions(team_id, current_position, previous_standings):
    if previous_standings is None:
        return "●"

    for team in previous_standings:
        if str(team['team']['id']) == team_id:
            previous_position = team['position']
            if current_position < previous_position:
                return "▲"
            elif current_position > previous_position:
                return "▼"
            else:
                return "●"
    return "●"

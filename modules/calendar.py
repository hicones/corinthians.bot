from datetime import datetime, timedelta

def format_match_date(utc_date):
    utc_datetime = datetime.strptime(utc_date, "%Y-%m-%dT%H:%M:%SZ")
    brasil_datetime = utc_datetime - timedelta(hours=3)
    return brasil_datetime.strftime("%d/%m - %H:%M")


def generate_matches_list(matches):
    match_list = ""

    for match in matches:
        home_team = match["homeTeam"]["shortName"]
        away_team = match["awayTeam"]["shortName"]
        formatted_date = format_match_date(match["utcDate"])

        match_list += f"{formatted_date} - {home_team} x {away_team}\n"

    return match_list

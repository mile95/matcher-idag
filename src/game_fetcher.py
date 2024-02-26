import requests
from typing import List, Dict, Optional
from datetime import datetime


def get_matches_today(association_id: int) -> Optional[List[Dict]]:
    api_url = "/api/matches-today/games/"
    todays_date = get_formatted_date()
    proxy_url = "https://www.gbgfotboll.se"

    headers = {
        "authority": "www.gbgfotboll.se",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en,en-US;q=0.9,nl;q=0.8,sv;q=0.7",
        "referer": "https://www.gbgfotboll.se/tavling/matcher-idag/",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    }

    url = f"{proxy_url}{api_url}?associationId={association_id}&date={todays_date}"

    response = requests.get(url, headers=headers).json()
    return parse(response)


def get_all_locations(resp: Dict) -> List[str]:
    all_locations = set()

    if resp and "competitions" in resp:
        for competition in resp["competitions"]:
            if competition and "games" in competition:
                for game in competition["games"]:
                    if game and "location" in game:
                        all_locations.add(game["location"])

    return list(all_locations)


def parse(resp: Dict) -> List[Dict]:
    parsed_games = []
    for comp in resp.get("competitions", []):
        for game in comp.get("games", []):
            model = {
                "competition": comp.get("name", "").strip(),
                "home": game["homeTeam"]["name"].strip(),
                "away": game["awayTeam"]["name"].strip(),
                "location": game.get("location", "").strip(),
                "timestamp": game.get("date", "").strip(),
            }
            parsed_games.append(model)

    return parsed_games


def get_formatted_date() -> str:
    date = datetime.now()
    year, month, day = (
        pad_number(date.year),
        pad_number(date.month),
        pad_number(date.day),
    )
    return f"{year}-{month}-{day}"


def pad_number(num: int) -> str:
    return f"0{num}" if num < 10 else str(num)

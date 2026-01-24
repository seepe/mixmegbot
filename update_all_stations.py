import requests
import os
from datetime import datetime
import urllib.parse

STATIONS = {
    "mixmegapol": "Mix Megapol",
    "banditrock": "Bandit Rock",
    "starfmse": "Star FM",
    "rixfm": "RIX FM",
    "nrjsweden": "NRJ Sweden",
    "lugnafavoriter": "Lugna Favoriter"
}

BASE_URL = "https://prod.radio-api.net/stations/{}/songs"


def fetch_songs(station_id):
    url = BASE_URL.format(station_id)

    try:
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            print(f"⚠️  Hoppar över {station_id}: API gav {r.status_code}")
            return []

        data = r.json()
        return [item["rawInfo"] for item in data if item.get("rawInfo")]

    except Exception as e:
        print(f"⚠️  Hoppar över {station_id}: API-fel ({e})")
        return []


def update_history(station_id, songs):
    path = f"stations/{station_id}/{station_id}.txt"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            old = [line.strip() for line in f if line.strip()]
    else:
        old = []

    combined = list(dict.fromkeys(old + songs))

    combined = combined[-500:]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(combined))

    return combined


def generate_station_html(station_id, station_name, songs, api_latest, history_latest):
    html_path = f"stations/{station_id}/{station_id}.html"

    html_top = f"""<html>
<head>
<meta charset='UTF-8'>
<title>{station_name}</title>
<link rel="stylesheet" href="../stations.css">
</head>
<body>

<div class="header">
    <h1>{station_name}</h1>
    <div class="underline"></div>
</div>

<div class="info">
    Senaste låt från API:t: <b>{api_latest}</b><br>
    Senaste NY låt i historiken: <b>{history_latest}</b>
</div>

<ul class="songlist">
"""

    html_bottom = """
</ul>
</body>
</html>
"""

    new_limit = 5

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_top)

        for index, raw in enumerate(songs):
            encoded = urllib.parse.quote(raw)
            spotify_url = f"https://open.spotify.com/search/{encoded}"

            if index < new_limit:
                f.write(
                    f"<li><a href='{spotify_url}' target='_blank'>{raw}</a>"
                    f"<span class='new-flag'>NY!</span></li>\n"
                )
            else:
                f.write(
                    f"<li><a href='{spotify_url}' target='_blank'>{raw}</a></li>\n"
                )

        f.write(html_bottom)


def generate_index_html(timestamp):
    html_path = "stations/index.html"

    html = f"""<html>
<head>
<meta charset='UTF-8'>
<title>Radiostationer</title>
<link rel="stylesheet" href="stations.css">
</head>
<body>

<h1 class="index-title">Radiostationer</h1>
<div class="timestamp">Senast uppdaterad: {timestamp}</div>

<div class="container">
"""

    for station_id, station_name in STATIONS.items():
        html_file = f"stations/{station_id}/{station_id}.html"
        exists = os.path.exists(html_file)
        dot_class = "green" if exists else "red"

        html += f"""
<a class="station" href="{station_id}/{station_id}.html">
    <div class="dot {dot_class}"></div>
    {station_name}
</a>
"""

    html += """
</div>
</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)


timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

for station_id, station_name in STATIONS.items():
    print(f"Uppdaterar {station_name}...")

    songs = fetch_songs(station_id)
    history = update_history(station_id, songs)

    api_latest = songs[0] if songs else "Inga låtar från API"
    history_latest = history[-1] if history else "Ingen historik"

    limited_history = history[-500:]

    generate_station_html(station_id, station_name, limited_history, api_latest, history_latest)

generate_index_html(timestamp)

print("Alla stationer uppdaterade.")

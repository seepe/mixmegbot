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

    # ⭐ Begränsa historiken till senaste 500 låtarna
    combined = combined[-500:]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(combined))

    return combined


def generate_station_html(station_id, station_name, songs, api_latest, history_latest):
    html_path = f"stations/{station_id}/{station_id}.html"

    html_top = f"""<html>
<head>
<meta charset='UTF-8'>
<title>{station_name} – Spotifylista</title>
<style>
    body {{
        font-family: Arial, sans-serif;
        background: #121212;
        color: #ffffff;
        margin: 0;
        padding: 0;
    }}

    .banner {{
        background: #1DB954;
        color: #000;
        padding: 20px;
        text-align: center;
        font-size: 26px;
        font-weight: bold;
    }}

    .info {{
        text-align: center;
        margin-top: 20px;
        margin-bottom: 30px;
        font-size: 18px;
        color: #cccccc;
    }}

    ul {{
        list-style: none;
        padding: 0;
        max-width: 700px;
        margin: auto;
    }}

    li {{
        background: #1e1e1e;
        margin: 8px 0;
        padding: 12px 18px;
        border-radius: 8px;
        transition: 0.2s;
        font-size: 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}

    li:hover {{
        background: #2a2a2a;
        transform: scale(1.02);
    }}

    a {{
        color: #1DB954;
        text-decoration: none;
        font-weight: bold;
    }}

    a:hover {{
        text-decoration: underline;
    }}

    .new-flag {{
        background: #1DB954;
        color: #000;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 10px;
    }}
</style>
</head>
<body>

<div class="banner">{station_name}</div>

<div class="info">
    Senaste låt från API:t: <b>{api_latest}</b><br>
    Senaste NY låt i historiken: <b>{history_latest}</b>
</div>

<ul>
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
<style>
    body {{
        background: #121212;
        color: #ffffff;
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
    }}

    h1 {{
        text-align: center;
        margin-top: 30px;
        color: #1DB954;
    }}

    .timestamp {{
        text-align: center;
        color: #bbbbbb;
        margin-bottom: 30px;
        font-size: 16px;
    }}

    .container {{
        max-width: 600px;
        margin: auto;
        padding: 20px;
    }}

    .station {{
        display: block;
        background: #1e1e1e;
        border: 2px solid #1DB954;
        border-radius: 10px;
        padding: 15px 20px;
        margin: 12px 0;
        font-size: 20px;
        color: #ffffff;
        text-decoration: none;
        display: flex;
        align-items: center;
        transition: 0.2s;
    }}

    .station:hover {{
        background: #2a2a2a;
        transform: scale(1.02);
    }}

    .dot {{
        width: 14px;
        height: 14px;
        border-radius: 50%;
        margin-right: 12px;
    }}

    .green {{ background: #1DB954; }}
    .red {{ background: #ff4444; }}
</style>
</head>
<body>

<h1>Radiostationer</h1>
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


# ⭐ Huvudloop
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

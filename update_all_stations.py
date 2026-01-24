import requests
import os
from datetime import datetime
import urllib.parse

STATIONS = {
    "mixmegapol": "Mix Megapol",
    "banditrock": "Bandit Rock",
    "starfmse": "Star FM",
    "rixfm": "RIX FM"
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

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(combined))

    return combined


def generate_html(station_id, station_name, songs):
    html_path = f"stations/{station_id}/{station_id}.html"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

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
        font-size: 22px;
        font-weight: bold;
        letter-spacing: 1px;
    }}

    h1 {{
        text-align: center;
        color: #1DB954;
        font-size: 36px;
        margin-top: 30px;
        margin-bottom: 10px;
    }}

    .timestamp {{
        text-align: center;
        color: #bbbbbb;
        font-size: 16px;
        margin-bottom: 30px;
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

<div class="banner">{station_name} – Senast uppdaterad: {timestamp}</div>

<h1>Spotify-sökningar</h1>
<div class="timestamp">(Genererad automatiskt)</div>

<ul>
"""

    html_bottom = """
</ul>
</body>
</html>
"""

    # Markera de senaste 5 låtarna som NY!
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


for station_id, station_name in STATIONS.items():
    print(f"Uppdaterar {station_name}...")
    songs = fetch_songs(station_id)
    history = update_history(station_id, songs)
    generate_html(station_id, station_name, history)

print("Alla stationer uppdaterade.")

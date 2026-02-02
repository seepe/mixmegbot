import requests
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import urllib.parse

STATIONS = {
    "mixmegapol": "Mix Megapol",
    "banditrock": "Bandit Rock",
    "starfmse": "Star FM",
    "rixfm": "RIX FM",
    "nrjsweden": "NRJ Sweden",
    "lugnafavoriter": "Lugna Favoriter",
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
    combined = combined[-100:]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(combined))

    return combined


def generate_station_html(station_id, station_name, songs, api_latest, history_latest):
    html_path = f"stations/{station_id}/{station_id}.html"

    html_top = f"""<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset='UTF-8'>
<title>{station_name}</title>
<link rel="stylesheet" href="../stations.css">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body class="dark">

<nav class="navbar">
  <a href="/" class="logo">📻</a>
  <div class="nav-right">
    <a href="../index.html" class="theme-btn" style="margin-right:10px;">⬅</a>
    <button id="theme-toggle" class="theme-btn">🌓</button>
  </div>
</nav>

<main class="content">

  <header class="header-area">
    <h1>{station_name}</h1>
    <p class="timestamp">
      Senaste låt från API:t: <b>{api_latest}</b><br>
      Senaste NY låt i historiken: <b>{history_latest}</b>
    </p>
  </header>

  <ul class="songlist">
"""

    html_bottom = """
  </ul>

  <script src="../script.js"></script>
</main>
</body>
</html>
"""

    new_limit = 5

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_top)

        for index, raw in enumerate(reversed(songs)):
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

    html = f"""
<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset='UTF-8'>
<title>Radiostationer</title>
<link rel="stylesheet" href="stations.css">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body class="dark">

<nav class="navbar">
  <a href="/" class="logo">📻</a>
  <div class="nav-right">
    <button id="theme-toggle" class="theme-btn">🌓</button>
  </div>

  <!-- Gamla dropdownen (Spotlistr) – orörd -->
  <div id="spotlistrHeaderTool" style="display:flex; gap:8px; align-items:center;">
    <select id="stationSelect" class="pantex-select" style="height:36px;">
      <option value="">🎵</option>
      <option value="banditrock">Bandit Rock</option>
      <option value="lugnafavoriter">Lugna Favoriter</option>
      <option value="mixmegapol">Mix Megapol</option>
      <option value="nrjsweden">NRJ Sweden</option>
      <option value="rixfm">Rix FM</option>
      <option value="starfmse">Star FM</option>
    </select>

    <button id="createPlaylistBtn" class="btn-accent" style="height:36px; padding:0 16px;">
      Spotlistr
    </button>
  </div>

  <div id="spotlistrPopup" style="display:none;"></div>
</nav>

<main class="content">

  <header class="header-area">
    <h1>Radiostationer</h1>
    <p class="timestamp">Senast uppdaterad: {timestamp}</p>
  </header>

  <!-- ⭐ NY PREMIUM LIVE-RADIO HÖGST UPP -->
  <section class="live-radio-top">
    <div class="live-radio-left">
      <span class="live-dot"></span>
      <span id="liveStationName">Ingen station vald</span>
      <div class="live-eq"><div></div><div></div><div></div></div>
    </div>

    <select id="liveStationSelect" class="live-select">
      <option value="">📶</option>
      <option value="p2">P2</option>
      <option value="p3">P3</option>
      <option value="p4sth">P4</option>
    </select>

    <button class="live-play-btn" id="livePlayToggle">▶</button>

    <audio id="liveAudio" preload="none" playsinline webkit-playsinline>
      <source id="liveSource" src="" type="audio/aac">
    </audio>
  </section>
  <!-- ⭐ SLUT PÅ NY LIVE-RADIO -->

  <section class="station-grid">
"""

    # Station cards
    for station_id, station_name in STATIONS.items():
        html_file = f"stations/{station_id}/{station_id}.html"
        exists = os.path.exists(html_file)
        dot_class = "green" if exists else "red"

        html += f"""
    <a class="station-card" href="{station_id}/{station_id}.html">
      <span class="dot {dot_class}"></span>
      <span class="station-name">{station_name}</span>
    </a>
"""

    html += """
  </section>

  <!-- Hidden trigger button -->
  <div class="trigger-wrapper">
    <button class="trigger-btn" onclick="fetch('trigger.php').then(()=>alert('Uppdatering skickad!'))">
      ⟳ Hämta ny data
    </button>
  </div>

</main>

<script src="script.js"></script>
</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)


# -----------------------------
# MAIN SCRIPT
# -----------------------------

timestamp = datetime.now(ZoneInfo("Europe/Stockholm")).strftime("%Y-%m-%d %H:%M")

for station_id, station_name in STATIONS.items():
    print(f"Uppdaterar {station_name}...")

    songs = fetch_songs(station_id)
    history = update_history(station_id, songs)

    api_latest = songs[0] if songs else "Inga låtar från API"
    history_latest = history[-1] if history else "Ingen historik"

    limited_history = history[-100:]

    generate_station_html(station_id, station_name, limited_history, api_latest, history_latest)

generate_index_html(timestamp)

print("Alla stationer uppdaterade.")

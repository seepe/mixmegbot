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


# ---------------------------------------------------------
#   CLEAN, MINIMAL STATION PAGE (NO PLAYER, NO SPOTLISTR)
# ---------------------------------------------------------
def generate_station_html(station_id, station_name, songs, api_latest, history_latest):
    html_path = f"stations/{station_id}/{station_id}.html"

    html = f"""<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="UTF-8">
  <title>{station_name}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="../stations.css">
</head>

<body class="dark">

<!-- NAVBAR -->
<nav class="navbar">
  <a href="../index.html" class="logo">⬅</a>

  <div class="nav-right">
    <button id="theme-toggle" class="theme-btn">🌓</button>
  </div>
</nav>

<!-- MAIN CONTENT -->
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

    # Song list
    new_limit = 5
    for index, raw in enumerate(reversed(songs)):
        encoded = urllib.parse.quote(raw)
        spotify_url = f"https://open.spotify.com/search/{encoded}"

        if index < new_limit:
            html += f"<li><a href='{spotify_url}' target='_blank'>{raw}</a><span class='new-flag'>NY!</span></li>\n"
        else:
            html += f"<li><a href='{spotify_url}' target='_blank'>{raw}</a></li>\n"

    html += """
  </ul>

</main>

<script src="../script.js"></script>

</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)


# ---------------------------------------------------------
#   PREMIUM INDEX PAGE (WITH PLAYER + SPOTLISTR)
# ---------------------------------------------------------
def generate_index_html(timestamp):
    html_path = "stations/index.html"

    html = f"""<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="UTF-8">
  <title>Radiostationer</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="stations.css">
</head>

<body class="dark">

<!-- NAVBAR -->
<nav class="navbar">
  <a href="/" class="logo">📻</a>

  <div class="nav-right">

    <!-- CUSTOM DROPDOWN -->
    <div class="dropdown" id="stationDropdown">
      <button class="dropdown-btn">🎵</button>
      <div class="dropdown-list">
        <div data-value="banditrock">🤘 Bandit Rock</div>
        <div data-value="lugnafavoriter">💗 Lugna Favoriter</div>
        <div data-value="mixmegapol">🎤 Mix Megapol</div>
        <div data-value="nrjsweden">🔥 NRJ Sweden</div>
        <div data-value="rixfm">⭐ RIX FM</div>
        <div data-value="starfmse">🌟 Star FM</div>
      </div>
    </div>

    <select id="stationSelect" style="display:none;">
      <option value="">🎵</option>
      <option value="banditrock">Bandit Rock</option>
      <option value="lugnafavoriter">Lugna Favoriter</option>
      <option value="mixmegapol">Mix Megapol</option>
      <option value="nrjsweden">NRJ Sweden</option>
      <option value="rixfm">RIX FM</option>
      <option value="starfmse">Star FM</option>
    </select>

    <button id="createPlaylistBtn" class="btn-accent">
      Spotlistr
    </button>

    <button id="theme-toggle" class="theme-btn">🌓</button>
  </div>

  <div id="spotlistrPopup" class="spotlistr-popup" style="display:none;"></div>
</nav>

<!-- MAIN CONTENT -->
<main class="content">

  <header class="header-area">
    <h1>Radiostationer</h1>
    <p class="timestamp">Senast uppdaterad: {timestamp}</p>
  </header>

  <section class="station-grid">
"""

    # Station cards
    for station_id, station_name in STATIONS.items():
        html += f"""
    <a class="station-card" href="{station_id}/{station_id}.html">
      <span class="dot green"></span>
      <span class="station-name">{station_name}</span>
    </a>
"""

    html += """
  </section>

  <div class="trigger-wrapper">
    <button class="trigger-btn" onclick="fetch('trigger.php').then(()=>alert('Uppdatering skickad!'))">
      ⟳ Hämta ny data
    </button>
  </div>

</main>

<!-- MINI PLAYER -->
<div id="miniPlayer" class="mini-player">

  <div class="mini-left">
    <div class="mini-main">

      <span id="miniLiveBadge" class="mini-live-badge">● LIVE</span>

      <div class="mini-station-row">
        <span id="miniIcon">📶</span>
        <span id="miniStation">Ingen station</span>
      </div>

      <div class="dropdown" id="liveDropdown">
        <button class="dropdown-btn">📶</button>
        <div class="dropdown-list">
          <div data-value="p2">🎼 P2</div>
          <div data-value="p3">🎧 P3</div>
          <div data-value="p4sth">📢 P4</div>
        </div>
      </div>

      <select id="liveStationSelect" style="display:none;">
        <option value="">⏹️</option>
        <option value="p2">P2</option>
        <option value="p3">P3</option>
        <option value="p4sth">P4</option>
      </select>

      <div id="miniEq" class="mini-eq">
        <div></div><div></div><div></div>
      </div>

    </div>
  </div>

  <div class="mini-controls">
    <button id="miniExpandToggle" class="mini-icon-btn">⌃</button>
    <button id="miniVolumeBtn" class="mini-icon-btn">🔊</button>
    <button id="miniPlayToggle" class="mini-btn">▶</button>

    <div id="miniVolumeSlider" class="mini-volume-slider hidden">
      <input type="range" id="miniVolumeRange" min="0" max="1" step="0.01" value="1">
    </div>
  </div>

  <audio id="liveAudio" preload="none" playsinline webkit-playsinline>
    <source id="liveSource" src="" type="audio/aac">
  </audio>

</div>

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

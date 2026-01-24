import requests
import os

STATIONS = {
    "mixmegapol": "Mix Megapol",
    "banditrock": "Bandit Rock",
    "nrjsweden": "NRJ Sweden",
    "lugnafavoriter": "Lugna Favoriter",
    "starfmse": "Star FM",
    "rixfm": "RIX FM"
}

BASE_URL = "https://prod.radio-api.net/stations/{}/songs"


def fetch_songs(station_id):
    url = BASE_URL.format(station_id)
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    return [item["rawInfo"] for item in data if item.get("rawInfo")]


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

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f"<h1>{station_name}</h1>\n")
        f.write("<ul>\n")
        for s in songs:
            f.write(f"<li>{s}</li>\n")
        f.write("</ul>\n")


for station_id, station_name in STATIONS.items():
    print(f"Uppdaterar {station_name}...")
    songs = fetch_songs(station_id)
    history = update_history(station_id, songs)
    generate_html(station_id, station_name, history)

print("Alla stationer uppdaterade.")

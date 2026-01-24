import requests
import os

URL = "https://prod.radio-api.net/stations/mixmegapol/songs"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    )
}

def fetch_songs():
    response = requests.get(URL, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()

    songs = []
    for item in data:
        raw = item.get("rawInfo", "").strip()
        if raw:
            songs.append(raw)

    return songs

# Hämta nya låtar från API
new_songs = fetch_songs()

# Rätt sökväg – filen ligger i samma mapp som update.py
path = "mixmeg.txt"

# Läs gamla låtar
if os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
        old_songs = [line.strip() for line in f if line.strip()]
else:
    old_songs = []

# Kombinera: gamla först, sedan nya
combined = list(dict.fromkeys(old_songs + new_songs))

# Spara tillbaka
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(combined))

print(f"Gamla låtar: {len(old_songs)}")
print(f"Nya låtar från API: {len(new_songs)}")
print(f"Totalt i mixmeg.txt: {len(combined)}")

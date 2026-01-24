import requests

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
        artist = item.get("artist", "").strip()
        title = item.get("title", "").strip()
        if artist and title:
            songs.append(f"{artist} - {title}")

    return songs

# Hämta nya låtar
new_songs = fetch_songs()

# Läs gamla låtar
try:
    with open("mixmeg.txt", "r", encoding="utf-8") as f:
        old_songs = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    old_songs = []

# Kombinera och ta bort dubbletter (behåll ordning)
combined = list(dict.fromkeys(new_songs + old_songs))

# Spara
with open("mixmeg.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(combined))

print(f"Uppdaterade mixmeg.txt med {len(new_songs)} nya låtar, totalt {len(combined)} i historiken.")

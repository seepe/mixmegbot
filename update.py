import requests

URL = "https://onlineradiobox.com/json/se.mixmegapol/playlist/"

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
    for item in data.get("data", []):
        artist = item.get("artist", "").strip()
        title = item.get("title", "").strip()
        if artist and title:
            songs.append(f"{artist} - {title}")

    # ta bort dubbletter men behåll ordning
    return list(dict.fromkeys(songs))

songs = fetch_songs()

with open("mixmeg.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(songs))

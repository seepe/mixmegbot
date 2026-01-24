import requests
import os

URL = "https://raw.githubusercontent.com/seepe/mixmegbot/main/mixmeg.txt"

def fetch_playlist():
    print("Hämtar mixmeg.txt från GitHub...")
    response = requests.get(URL, timeout=10)
    response.raise_for_status()
    github_songs = [line.strip() for line in response.text.split("\n") if line.strip()]
    print(f"Antal låtar från GitHub: {len(github_songs)}")

    if os.path.exists("playlist.txt"):
        with open("playlist.txt", "r", encoding="utf-8") as f:
            local_songs = [line.strip() for line in f if line.strip()]
    else:
        local_songs = []

    print(f"Antal lokala låtar innan merge: {len(local_songs)}")

    combined = list(dict.fromkeys(local_songs + github_songs))

    with open("playlist.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(combined))

    print(f"Uppdaterade playlist.txt med totalt {len(combined)} låtar.")

fetch_playlist()

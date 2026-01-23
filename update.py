import requests
from bs4 import BeautifulSoup

URL = "https://onlineradiobox.com/se/mixmegapol/playlist/"

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

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("table.table.table-hover tbody tr")

    songs = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 3:
            artist = cols[1].text.strip()
            title = cols[2].text.strip()
            songs.append(f"{artist} - {title}")

    return list(dict.fromkeys(songs))

songs = fetch_songs()

with open("mixmeg.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(songs))

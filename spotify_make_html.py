import urllib.parse
from datetime import datetime
import os

# Läs nuvarande låtlista
with open("playlist.txt", "r", encoding="utf-8") as f:
    songs = [line.strip() for line in f if line.strip()]

# Sortera: nyast först
songs = list(reversed(songs))

# Läs tidigare låtlista (om den finns)
if os.path.exists("playlist_previous.txt"):
    with open("playlist_previous.txt", "r", encoding="utf-8") as f:
        old_songs = [line.strip() for line in f if line.strip()]
else:
    old_songs = []

# Identifiera nya låtar
new_songs = set(songs) - set(old_songs)

# Skapa datumstämpel
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

html = f"""
<html>
<head>
<meta charset='UTF-8'>
<title>Mix Megapol – Spotifylista</title>
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

<div class="banner">Mix Megapol – Senast uppdaterad: {timestamp}</div>

<h1>Spotify-sökningar</h1>
<div class="timestamp">(Genererad automatiskt)</div>

<ul>
"""

# Lägg till låtarna
for song in songs:
    query = urllib.parse.quote(song)
    url = f"https://open.spotify.com/search/{query}"

    flag = "<span class='new-flag'>NY!</span>" if song in new_songs else ""

    html += f"<li><a href='{url}' target='_blank'>{song}</a>{flag}</li>\n"

html += """
</ul>
</body>
</html>
"""

# Skriv HTML-filen
with open("spotify_list.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Sparar playlist_previous.txt...")

# Spara nuvarande lista som "previous"
with open("playlist_previous.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(songs))

print("HTML genererad med NY!-markeringar.")

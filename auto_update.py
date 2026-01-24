import subprocess
import webbrowser
import time
import os
import paramiko
import datetime

# ==========================
#  Loggfunktion
# ==========================
def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("A_SpotRad.log", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


# ==========================
#  SFTP-inställningar
# ==========================
SFTP_HOST = "access-5019010393.webspace-host.com"                 # eller den SFTP-host du använder i FileZilla
SFTP_PORT = 22                          # standard för SFTP
SFTP_USER = "su573382"    # ändra
SFTP_PASS = "Moltas123!"        # ändra

REMOTE_PATH = "/spotify_list.html"   # ändra om din mapp heter något annat


# ==========================
#  Funktion: Ladda upp HTML via SFTP
# ==========================
def upload_file_sftp():
    log("Startar SFTP-uppladdning...")
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USER, password=SFTP_PASS)

    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put("spotify_list.html", REMOTE_PATH)

    sftp.close()
    transport.close()
    log("SFTP-uppladdning klar.")


# ==========================
#  Huvudflöde
# ==========================
log("=== Startar auto_update.py ===")

# Kör main.py (hämtar GitHub-listan)
try:
    log("Kör main.py...")
    subprocess.run(["python", "main.py"], check=True)
    log("main.py klar.")
except Exception as e:
    log(f"Fel i main.py: {e}")

# Kör spotify_make_html.py (genererar HTML)
try:
    log("Kör spotify_make_html.py...")
    subprocess.run(["python", "spotify_make_html.py"], check=True)
    log("HTML-generering klar.")
except Exception as e:
    log(f"Fel i spotify_make_html.py: {e}")

# Ladda upp HTML till webbhotellet via SFTP
try:
    upload_file_sftp()
except Exception as e:
    log(f"Fel vid SFTP-uppladdning: {e}")

log("=== auto_update.py avslutad ===\n")

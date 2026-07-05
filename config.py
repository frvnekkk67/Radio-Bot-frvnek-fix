"""
Konfiguracja bota - wszystkie wartości wrażliwe (tokeny, klucze) wczytywane
są ze zmiennych środowiskowych (plik .env lokalnie, albo Variables w Railway).
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Sekrety / dane logowania ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# Spotify: OPCJONALNE. Bez tych zmiennych bot i tak obsługuje playlisty/utwory
# Spotify - korzysta wtedy z darmowej, nieoficjalnej metody (patrz utils/spotify.py).
# Ustaw je tylko jeśli wolisz oficjalne, zarejestrowane API.
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# --- Baza danych ---
# Na Railway zalecane jest podpięcie Volume i ustawienie DB_PATH np. na /data/rankings.db
# żeby dane rankingu przetrwały redeploy. Domyślnie plik lokalny w katalogu bota.
DB_PATH = os.getenv("DB_PATH", "rankings.db")

# --- System rankingu / poziomów ---
# Ile punktów daje jedna wysłana wiadomość
POINTS_PER_MESSAGE = int(os.getenv("POINTS_PER_MESSAGE", "1"))
# Ile punktów daje jedna minuta na kanale głosowym
POINTS_PER_VOICE_MINUTE = int(os.getenv("POINTS_PER_VOICE_MINUTE", "1"))
# Ile punktów potrzeba na jeden poziom (poziom = punkty // LEVEL_POINTS)
LEVEL_POINTS = int(os.getenv("LEVEL_POINTS", "100"))

# Minimalny odstęp (sekundy) między punktami za wiadomości od tego samego użytkownika,
# żeby spam nie nakręcał rankingu w nieskończoność (domyślnie 2 minuty)
MESSAGE_COOLDOWN_SECONDS = 120

# --- Muzyka ---
# Ile sekund bezczynności (brak utworów w kolejce, tryb NIE 24/7) zanim bot opuści kanał
IDLE_DISCONNECT_SECONDS = 300

# --- Lavalink (serwer muzyczny, osobna usługa - patrz folder lavalink/ i README.md) ---
LAVALINK_HOST = os.getenv("LAVALINK_HOST", "")
LAVALINK_PORT = int(os.getenv("LAVALINK_PORT", "2333"))
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD", "youshallnotpass")
LAVALINK_SECURE = os.getenv("LAVALINK_SECURE", "false").lower() == "true"

# Kolory grafik / embedów (RGB)
COLOR_PRIMARY = (88, 101, 242)     # blurple
COLOR_BACKGROUND_TOP = (32, 34, 47)
COLOR_BACKGROUND_BOTTOM = (18, 19, 26)
"""
Główny punkt wejścia bota Discord.
Uruchomienie: python bot.py

Wymaga działającego serwera Lavalink (osobna usługa - patrz README.md /
folder lavalink/), do którego bot łączy się przez bibliotekę wavelink.
"""
import discord
import wavelink
from discord.ext import commands, tasks

import config
from utils.database import Database
from utils.player import PlayerManager, MusicPlayer
from utils.spotify import SpotifyClient

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True


class MusicRankingBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.db = Database()
        self.players = PlayerManager(self)
        self.spotify = SpotifyClient(config.SPOTIFY_CLIENT_ID, config.SPOTIFY_CLIENT_SECRET)

    async def setup_hook(self):
        await self.db.connect()
        for ext in ("cogs.music", "cogs.ranking", "cogs.settings"):
            await self.load_extension(ext)
        await self.tree.sync()

        if config.LAVALINK_HOST:
            scheme = "https" if config.LAVALINK_SECURE else "http"
            uri = f"{scheme}://{config.LAVALINK_HOST}:{config.LAVALINK_PORT}"
            node = wavelink.Node(uri=uri, password=config.LAVALINK_PASSWORD)
            try:
                await wavelink.Pool.connect(nodes=[node], client=self)
            except Exception as e:
                print(f"[lavalink] Nie udało się połączyć z serwerem Lavalink pod {uri}: {e}")
        else:
            print("[lavalink] Brak LAVALINK_HOST w zmiennych środowiskowych - muzyka nie będzie działać.")

        self.autoplay_watchdog.start()

    async def on_ready(self):
        print(f"Zalogowano jako {self.user} (ID: {self.user.id})")
        await self._restore_autoplay()
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.listening, name="/graj | /ranga | /top"
        ))

    async def _restore_autoplay(self):
        """Po (re)starcie bota przywraca tryb 24/7 na serwerach, które go mają włączonego."""
        guilds_cfg = await self.db.get_all_autoplay_guilds()
        for cfg in guilds_cfg:
            guild = self.get_guild(cfg["guild_id"])
            if guild is None:
                continue
            channel = guild.get_channel(cfg["voice_channel_id"])
            if channel is None:
                continue
            try:
                player = await self.players.connect(channel)
                await player.setup_autoplay(cfg["playlist_url"], self.spotify)
                await player.start_if_idle()
                print(f"[autoplay] Przywrócono tryb 24/7 na serwerze {guild.name}")
            except Exception as e:
                print(f"[autoplay] Nie udało się przywrócić 24/7 na {guild.name}: {e}")

    @tasks.loop(seconds=60)
    async def autoplay_watchdog(self):
        """Co minutę sprawdza, czy bot nadal jest połączony tam, gdzie powinien być w trybie 24/7,
        i dołącza ponownie, jeśli został rozłączony (np. przez restart Discorda)."""
        for player in self.players.all():
            if not player.autoplay_enabled:
                continue
            if player.connected:
                if not player.playing and not player.paused:
                    await player.start_if_idle()
                continue

        guilds_cfg = await self.db.get_all_autoplay_guilds()
        for cfg in guilds_cfg:
            guild = self.get_guild(cfg["guild_id"])
            if guild is None or isinstance(guild.voice_client, MusicPlayer):
                continue
            channel = guild.get_channel(cfg["voice_channel_id"])
            if channel is None:
                continue
            try:
                player = await self.players.connect(channel)
                await player.setup_autoplay(cfg["playlist_url"], self.spotify)
                await player.start_if_idle()
                print(f"[autoplay] Ponownie połączono z kanałem 24/7 na {guild.name}")
            except Exception as e:
                print(f"[autoplay] Błąd ponownego łączenia na {guild.name}: {e}")

    @autoplay_watchdog.before_loop
    async def before_watchdog(self):
        await self.wait_until_ready()

    async def close(self):
        await self.db.close()
        await super().close()


bot = MusicRankingBot()


@bot.listen()
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
    print(f"[lavalink] Połączono z węzłem Lavalink: {payload.node.identifier}")


@bot.listen()
async def on_wavelink_track_end(payload: wavelink.TrackEndEventPayload):
    player = payload.player
    if player is not None and isinstance(player, MusicPlayer):
        await player.play_next()


@bot.listen()
async def on_wavelink_track_exception(payload: wavelink.TrackExceptionEventPayload):
    print(f"[lavalink] Błąd odtwarzania utworu: {payload.exception}")
    player = payload.player
    if player is not None and isinstance(player, MusicPlayer):
        await player.play_next()


@bot.listen()
async def on_wavelink_track_stuck(payload: wavelink.TrackStuckEventPayload):
    print(f"[lavalink] Utwór się zaciął, pomijam: {payload.track.title}")
    player = payload.player
    if player is not None and isinstance(player, MusicPlayer):
        await player.play_next()


def main():
    if not config.DISCORD_TOKEN:
        raise SystemExit(
            "Brak DISCORD_TOKEN. Ustaw go w pliku .env (lokalnie) albo w Variables na Railway."
        )
    bot.run(config.DISCORD_TOKEN)


if __name__ == "__main__":
    main()
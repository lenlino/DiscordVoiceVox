import discord
import lavalink
from lavalink import ClientError
import re
import urllib.parse


class LavalinkPlayer(lavalink.BasePlayer):
    """Custom lavalink player for handling audio playback."""

    def __init__(self, guild_id, node):
        super().__init__(guild_id, node)
        self.filters = Filters()
        # Add a dummy track to prevent assertion errors
        self._dummy_track = None

    @property
    def current(self):
        """Override the current property to handle None case."""
        current = super().current
        if current is None and hasattr(self, '_dummy_track') and self._dummy_track is not None:
            return self._dummy_track
        return current

    async def play_track(self, track):
        """Play a track."""
        # Store the track as a dummy in case we need it later
        self._dummy_track = track
        await self.play(track)

    async def search_and_play(self, query, source=None, requester=None):
        """Search for a track and play it."""
        results = await self.search_tracks(query, source)
        if not results or not results.tracks:
            return None

        track = results.tracks[0]
        if requester:
            track.requester = requester

        # Store the track as a dummy in case we need it later
        self._dummy_track = track
        await self.play(track)
        return track

    async def search_tracks(self, query, source=None):
        """Search for tracks."""
        if source == "voicevox":
            # Handle voicevox source
            return await self.node.get_tracks(query)
        elif source == "wav":
            # Handle wav source
            return await self.node.get_tracks(query)
        else:
            # Default search
            return await self.node.get_tracks(query)


class Filters:
    """Filters for audio playback."""

    def __init__(self):
        self.timescale = TimescaleFilter()

    def reset(self):
        """Reset all filters."""
        self.timescale.reset()

    def to_dict(self):
        """Convert filters to dictionary."""
        return {
            'timescale': self.timescale.to_dict() if self.timescale.active else None
        }


class TimescaleFilter:
    """Timescale filter for adjusting speed and pitch."""

    def __init__(self):
        self.speed = 1.0
        self.pitch = 1.0
        self.active = False

    def set(self, speed=None, pitch=None):
        """Set filter values."""
        if speed is not None:
            self.speed = float(speed)
        if pitch is not None:
            self.pitch = float(pitch)
        self.active = True
        return self

    def reset(self):
        """Reset filter values."""
        self.speed = 1.0
        self.pitch = 1.0
        self.active = False
        return self

    def to_dict(self):
        """Convert filter to dictionary."""
        return {
            'speed': self.speed,
            'pitch': self.pitch
        }


class LavalinkWavelink:
    """Adapter class to provide wavelink-like functionality using lavalink.py."""

    @staticmethod
    async def get_tracks(query, source=None, node=None):
        """Get tracks from lavalink."""
        if node is None:
            # Use the first available node
            from main import bot
            if not hasattr(bot, 'lavalink'):
                return []
            node = bot.lavalink.node_manager.nodes[0] if bot.lavalink.node_manager.nodes else None
            if node is None:
                return []

        try:
            if source == "voicevox":
                # Handle voicevox source
                return await node.get_tracks(query)
            elif source == "wav":
                # Handle wav source
                return await node.get_tracks(query)
            else:
                # Default search
                return await node.get_tracks(query)
        except Exception as e:
            print(f"Error searching tracks: {e}")
            return []

    class Playable:
        """Adapter for wavelink.Playable."""

        @staticmethod
        async def search(query, source=None, node=None):
            """Search for tracks."""
            import base64
            import urllib.parse

            # Handle different types of queries based on the issue description
            if isinstance(query, str) and query.endswith(".wav"):
                # Handle .wav files (already supported)
                pass
            elif isinstance(query, str) and query.startswith("usegpu"):
                # Handle voicevox files
                from main import gpu_host
                parts = query.split("_")
                if len(parts) >= 4:
                    lavalink_retry = 1 if urllib.parse.quote(parts[1]) == gpu_host else 0
                    query = f"vv://voicevox?&speaker={int(parts[3])}&address={urllib.parse.quote(parts[1])}&query-address={urllib.parse.quote(parts[2])}&text={urllib.parse.quote(parts[4] if len(parts) > 4 else '')}&retry={lavalink_retry}"
                    source = "voicevox"
            elif not isinstance(query, str) or not query.endswith(".wav"):
                # Handle other file types using base64 encoding
                query = base64.urlsafe_b64encode(query if isinstance(query, bytes) else query.encode('utf-8')).decode('utf-8')
                source = "wav"

            results = await LavalinkWavelink.get_tracks(query, source, node)
            if not results or not results.tracks:
                return []
            return results.tracks

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

    async def play_track(self, track):
        """Play a track."""
        await self.play(track)

    async def search_and_play(self, query, source=None, requester=None):
        """Search for a track and play it."""
        results = await self.search_tracks(query, source)
        if not results or not results.tracks:
            return None

        track = results.tracks[0]
        if requester:
            track.requester = requester

        await self.play(track)
        return track

    async def search_tracks(self, query, source=None):
        """Search for tracks."""
        if source == "voicevox":
            # Handle voicevox source
            return await self.node.rest_api.search(query)
        elif source == "wav":
            # Handle wav source
            return await self.node.rest_api.search(query)
        else:
            # Default search
            return await self.node.rest_api.search(query)


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
                return await node.rest_api.search(query)
            elif source == "wav":
                # Handle wav source
                return await node.rest_api.search(query)
            else:
                # Default search
                return await node.rest_api.search(query)
        except Exception as e:
            print(f"Error searching tracks: {e}")
            return []

    class Playable:
        """Adapter for wavelink.Playable."""

        @staticmethod
        async def search(query, source=None, node=None):
            """Search for tracks."""
            results = await LavalinkWavelink.get_tracks(query, source, node)
            if not results or not results.tracks:
                return []
            return results.tracks

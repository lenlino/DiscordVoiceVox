import discord
import lavalink
from lavalink import ClientError
import re
import urllib.parse
from lavalink.filters import Timescale


class LavalinkPlayer(lavalink.BasePlayer):
    """Custom lavalink player for handling audio playback."""

    def __init__(self, guild_id, node):
        super().__init__(guild_id, node)
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
        """Search for tracks with node failover."""
        # Prefer the player's current node first, then fall back across others via LavalinkWavelink
        return await LavalinkWavelink.get_tracks(query, source, node=self.node)


class LavalinkWavelink:
    """Adapter class to provide wavelink-like functionality using lavalink.py."""

    @staticmethod
    async def get_tracks(query, source=None, node=None):
        """Get tracks from lavalink with failover across healthy nodes."""
        # If an explicit node is supplied, try it first; otherwise iterate healthy nodes.
        nodes_to_try = []
        if node is not None:
            nodes_to_try.append(node)
        else:
            try:
                from main import bot
                if hasattr(bot, 'lavalink') and getattr(bot.lavalink, 'nodes', None):
                    # Prefer available/ready nodes first, then any remaining nodes as fallback
                    all_nodes = list(bot.lavalink.nodes)
                    # Node.available is a method, call it.
                    healthy = [n for n in all_nodes if getattr(n, 'available', False)]
                    unhealthy = [n for n in all_nodes if n not in healthy]
                    nodes_to_try.extend(healthy + unhealthy)
            except Exception:
                pass

        if not nodes_to_try:
            return []

        last_err = None
        for n in nodes_to_try:
            try:
                if source == "voicevox":
                    return await n.get_tracks(query)
                elif source == "wav":
                    return await n.get_tracks(query)
                else:
                    return await n.get_tracks(query)
            except Exception as e:
                last_err = e
                continue

        # If all nodes failed, log the last error and return empty
        if last_err:
            print(f"Error searching tracks across nodes: {last_err}")
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
                if len(parts) >= 5:  # Ensure we have at least 5 parts (including the text)
                    lavalink_retry = 1 if urllib.parse.quote(parts[1]) == gpu_host else 0
                    text = parts[4]  # The text is now always the 5th part
                    query = f"vv://voicevox?&speaker={int(parts[3])}&address={urllib.parse.quote(parts[1])}&query-address={urllib.parse.quote(parts[2])}&text={urllib.parse.quote(text)}&retry={lavalink_retry}"
                    source = "voicevox"
            elif not isinstance(query, str) or not query.endswith(".wav"):
                # Handle other file types using base64 encoding
                query = base64.urlsafe_b64encode(query if isinstance(query, bytes) else query.encode('utf-8')).decode('utf-8')
                source = "wav"

            results = await LavalinkWavelink.get_tracks(query, source, node)
            if not results or not results.tracks:
                return []
            return results.tracks

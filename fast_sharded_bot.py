import asyncio
import discord
from discord.http import Route


class FastShardedBot(discord.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._identify_semaphore = None
        self._identify_lock = asyncio.Lock()

    async def _get_max_concurrency(self):
        if self._identify_semaphore is not None:
            return self._identify_semaphore
        async with self._identify_lock:
            if self._identify_semaphore is not None:
                return self._identify_semaphore
            data = await self.http.request(Route("GET", "/gateway/bot"))
            mc = data["session_start_limit"]["max_concurrency"]
            print(f"max_concurrency: {mc}")
            self._identify_semaphore = asyncio.Semaphore(mc)
            return self._identify_semaphore

    async def before_identify_hook(self, shard_id, *, initial=False):
        sem = await self._get_max_concurrency()
        async with sem:
            await asyncio.sleep(5.0)

    async def launch_shards(self):
        if self.shard_count is None:
            self.shard_count, gateway = await self.http.get_bot_gateway()
        else:
            gateway = await self.http.get_gateway()

        self._connection.shard_count = self.shard_count
        shard_ids = list(self.shard_ids or range(self.shard_count))
        self._connection.shard_ids = shard_ids

        sem = await self._get_max_concurrency()
        mc = sem._value

        for batch_start in range(0, len(shard_ids), mc):
            batch = shard_ids[batch_start:batch_start + mc]
            await asyncio.gather(*(
                self.launch_shard(gateway, sid, initial=(batch_start == 0 and i == 0))
                for i, sid in enumerate(batch)
            ))
            if batch_start + mc < len(shard_ids):
                await asyncio.sleep(5.0)

        self._connection.shards_launched.set()
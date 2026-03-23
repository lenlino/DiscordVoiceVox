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
        shard_ids = self.shard_ids or range(self.shard_count)

        async def _launch(sid, is_initial):
            await self.launch_shard(gateway, sid, initial=is_initial)

        tasks = []
        for i, shard_id in enumerate(shard_ids):
            tasks.append(_launch(shard_id, i == 0))
        await asyncio.gather(*tasks)
import asyncio
import async_timeout


class Fetcher(object):

    async def _fetch(self, session, url, attempts=5):
        attempt = 0
        while attempt < attempts:
            attempt += 1
            try:
                with async_timeout.timeout(10):
                    async with session.get(url) as response:
                        return await response.text()
            except:
                asyncio.sleep(1)

    async def _fetch_post(self, session, url, data, headers=None, attempts=5):
        attempt = 0
        while attempt < attempts:
            attempt += 1
            try:
                with async_timeout.timeout(10):
                    async with session.post(url, data=data, headers=headers) as response:
                        result = await response.text()
                        if result is None:
                            raise Exception()
                        return result
            except:
                asyncio.sleep(1)

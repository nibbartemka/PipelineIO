import asyncio
from typing import Any

import aiohttp


type PostResponse = dict[str, Any]


MAX_POST_ID: int  = 100
BASE_URL: str = "https://jsonplaceholder.typicode.com/posts"


async def fetch_post(
    session: aiohttp.ClientSession,
    post_id: int,
    semaphore: asyncio.Semaphore
) -> PostResponse | None:
    async with semaphore:
        url: str = f"{BASE_URL}/{post_id}"

        try:
            async with session.get(url, allow_redirects=True) as response:
                response.raise_for_status()
                return await response.json()
        except (
            asyncio.TimeoutError,
            aiohttp.ClientError,
            ValueError
        ) as exc:
            pass
        finally:
            pass


async def fetch_all_posts() -> list[PostResponse] | None:
    pass

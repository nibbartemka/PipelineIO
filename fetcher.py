import asyncio
from collections.abc import Coroutine
from contextlib import suppress
import logging
from typing import Any

import aiohttp

from models import PostData

logger: logging.Logger = logging.getLogger(__name__)


MAX_POST_ID: int = 100
BASE_URL: str = "https://jsonplaceholder.typicode.com/posts"
MAX_CONNECTIONS: int = 5
TIMEOUT: int = 5


async def fetch_post(
    session: aiohttp.ClientSession,
    post_id: int,
    semaphore: asyncio.Semaphore
) -> PostData | None:
    async with semaphore:
        logger.info("Начинаем загрузку поста %s", post_id)

        url: str = f"{BASE_URL}/{post_id}"

        try:
            async with session.get(url, allow_redirects=True) as response:
                response.raise_for_status()
                data = await response.json()
                return PostData(
                    user_id=data["userId"],
                    id=data["id"],
                    title=data["title"],
                    body=data["body"],
                )
        except (TimeoutError, aiohttp.ClientError, ValueError) as exc:
            logger.exception(
                "Ошибка при загрузке поста %s: %s",
                post_id, exc
            )

            return None


async def progress_monitor():
    while True:
        logger.info("Загрузка постов продолжается...")
        await asyncio.sleep(2)


async def fetch_all_posts() -> list[PostData] | None:
    semaphore: asyncio.Semaphore = asyncio.Semaphore(MAX_CONNECTIONS)
    timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(TIMEOUT)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        monitor_task = asyncio.create_task(
            progress_monitor(),
            name="fetch-progress-monitor",
        )

        tasks: list[Coroutine[Any, Any, PostData | None]] = [
            fetch_post(session, post_id, semaphore)
            for post_id in range(1, MAX_POST_ID + 1)
        ]

        try:
            return await asyncio.gather(*tasks)
        finally:
            monitor_task.cancel()
            with suppress(asyncio.CancelledError):
                await monitor_task

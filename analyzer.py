from concurrent.futures import Future, ProcessPoolExecutor, as_completed
import hashlib
import logging
import math
import os

from models import PostData, ProcessedPost

logger: logging.Logger = logging.getLogger(__name__)


def process_post(
    post: PostData,
) -> ProcessedPost | None:
    score: float = (sum(math.sin(i) for i in range(1_000_000))
                    * len(post.body))
    text_hash = hashlib.sha256(
        f"{post.title}{post.body}".encode()
    ).hexdigest()

    return ProcessedPost(
        user_id=post.user_id,
        id=post.id,
        title=post.title,
        body=post.body,
        complexity_score=score,
        text_hash=text_hash,
    )


def analyze_posts(
    posts: list[PostData],
) -> list[ProcessedPost]:
    def collect_results(futures: list[Future]) -> list[ProcessedPost]:
        results = []

        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception:
                logger.exception("Не удалось обработать пост")
                continue

        return results

    total_posts = len(posts)

    max_workers = min(
        os.cpu_count() or 1,
        total_posts,
    )

    with ProcessPoolExecutor(max_workers) as executor:
        futures = [
            executor.submit(process_post, post)
            for post in posts
        ]

        processed_posts = collect_results(futures)

        return processed_posts

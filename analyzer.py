from concurrent.futures import Future, ProcessPoolExecutor, as_completed
import hashlib
import logging
import math
import multiprocessing
import operator
import os
from typing import Any

from models import PostData, ProcessedPost

MONITOR_JOIN_TIMEOUT = 5

logger: logging.Logger = logging.getLogger(__name__)

_worker_counter: Any = None
_worker_lock: Any = None


def init_worker(counter: Any, lock: Any) -> None:
    global _worker_counter, _worker_lock
    _worker_counter = counter
    _worker_lock = lock


def monitor(status_queue: Any) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    monitor_logger = logging.getLogger("analyzer.monitor")

    while True:
        post_id = status_queue.get()

        if post_id is None:
            return

        monitor_logger.info("[Monitor] Пост %s обработан", post_id)


def process_post(
    post: PostData,
) -> ProcessedPost:
    text = post.title + post.body

    score = sum(math.sin(i) for i in range(1_000_000)) * len(text)

    text_hash = hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()

    processed_post = ProcessedPost(
        user_id=post.user_id,
        id=post.id,
        title=post.title,
        body=post.body,
        complexity_score=score,
        text_hash=text_hash,
    )

    with _worker_lock:
        _worker_counter.value += 1

    return processed_post


def collect_results(
    futures: list[Future[ProcessedPost]],
    status_queue: Any,
) -> list[ProcessedPost]:
    results = []

    for future in as_completed(futures):
        try:
            result = future.result()
        except Exception:
            logger.exception("Не удалось обработать пост")
            continue

        results.append(result)

        status_queue.put(result.id)

    return results


def analyze_posts(
    posts: list[PostData],
) -> list[ProcessedPost]:
    if not posts:
        return []

    max_workers = min(
        os.cpu_count() or 1,
        len(posts),
    )

    context = multiprocessing.get_context("spawn")
    status_queue = context.Queue()
    processed_count = context.Value("i", 0)
    count_lock = context.Lock()

    monitor_process = context.Process(
        target=monitor,
        args=(status_queue,),
        name="MonitorProcess",
    )

    monitor_process.start()

    try:
        with ProcessPoolExecutor(
            max_workers=max_workers,
            mp_context=context,
            initializer=init_worker,
            initargs=(processed_count, count_lock),
        ) as executor:
            futures = [
                executor.submit(process_post, post)
                for post in posts
            ]

            processed_posts = collect_results(futures, status_queue)
    finally:
        status_queue.put(None)
        monitor_process.join(timeout=MONITOR_JOIN_TIMEOUT)

        if monitor_process.is_alive():  # завис — не ждём вечно
            logger.warning("Монитор не завершился за %s с, останавливаем",
                           MONITOR_JOIN_TIMEOUT)
            monitor_process.terminate()
            monitor_process.join()

        status_queue.close()
        status_queue.join_thread()

    processed_posts.sort(key=operator.attrgetter("id"))

    logger.info(
        "Успешно обработано постов: %s",
        processed_count.value,
    )

    return processed_posts

from concurrent.futures import ThreadPoolExecutor
import json
import logging
from pathlib import Path
import queue
import threading
import time

from models import ProcessedPost

logger = logging.getLogger(__name__)

RESULTS_FILE = Path(__file__).with_name("results.log")
WORKER_COUNT = 4
SAVE_DELAY = 0.05
PROGRESS_INTERVAL = 2.0
QUEUE_POLL_TIMEOUT = 0.2

_file_lock = threading.Lock()


class SaveCounter:
    def __init__(self) -> None:
        self._value = 0
        self._lock = threading.Lock()

    def increment(self) -> None:
        with self._lock:
            self._value += 1

    @property
    def value(self) -> int:
        with self._lock:
            return self._value


def save_post(post_data: ProcessedPost) -> None:
    time.sleep(SAVE_DELAY)

    line = json.dumps(
        {
            "id": post_data.id,
            "title": post_data.title,
            "hash": post_data.text_hash,
            "score": post_data.complexity_score,
        },
        ensure_ascii=False,
    )

    with _file_lock, RESULTS_FILE.open("a", encoding="utf-8") as results_file:
        results_file.write(f"{line}\n")


def save_worker(
    tasks: queue.Queue[ProcessedPost],
    stop_event: threading.Event,
    counter: SaveCounter
) -> None:
    while True:
        try:
            post = tasks.get(timeout=QUEUE_POLL_TIMEOUT)
        except queue.Empty:
            if stop_event.is_set():
                return
            continue

        try:
            save_post(post)
            counter.increment()
        except Exception:
            logger.exception("Не удалось сохранить пост %s", post.id)
        finally:
            tasks.task_done()


def report_progress(
    stop_event: threading.Event,
    counter: SaveCounter,
    total_posts: int,
) -> None:
    while not stop_event.wait(PROGRESS_INTERVAL):
        logger.info(">>> Прогресс сохранения: %s / %s", counter.value, total_posts)


def save_posts(posts: list[ProcessedPost]) -> int:
    if not posts:
        return 0

    tasks: queue.Queue[ProcessedPost] = queue.Queue()

    for post in posts:
        tasks.put(post)

    stop_event = threading.Event()
    counter = SaveCounter()

    progress_thread = threading.Thread(
        target=report_progress,
        args=(stop_event, counter, len(posts)),
        name="SaveProgress",
    )

    with ThreadPoolExecutor(
        max_workers=WORKER_COUNT, thread_name_prefix="SaveWorker"
    ) as executor:
        futures = [
            executor.submit(
                save_worker,
                tasks,
                stop_event,
                counter,
            )
            for _ in range(WORKER_COUNT)
        ]

        try:
            progress_thread.start()
            tasks.join()
        finally:
            stop_event.set()
            progress_thread.join()

    for future in futures:
        future.result()

    return counter.value

import asyncio
import logging
import sys
from time import perf_counter

from analyzer import analyze_posts
from fetcher import MAX_POST_ID, fetch_all_posts
from saver import save_posts


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )


def run_pipeline() -> None:
    started_at = perf_counter()

    fetched_results = asyncio.run(fetch_all_posts())
    fetched_posts = [post for post in fetched_results if post is not None]

    processed_posts = analyze_posts(fetched_posts)
    saved_count = save_posts(processed_posts)

    elapsed = perf_counter() - started_at

    print("=== Отчёт о работе пайплайна ===")
    print(f"Запрошено постов: {MAX_POST_ID}")
    print(f"Успешно загружено: {len(fetched_posts)}")
    print(f"Успешно обработано (CPU): {len(processed_posts)}")
    print(f"Успешно сохранено (I/O): {saved_count}")
    print(f"Общее время: {elapsed:.2f} сек.")


def main() -> None:
    configure_logging()
    run_pipeline()


if __name__ == "__main__":
    main()

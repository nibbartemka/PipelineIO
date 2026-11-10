import logging
import sys


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)-8s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )


def main():
    configure_logging()

    logger = logging.getLogger(__name__)
    logger.info("Запуск пайплайна")
    logger.info("Выход из пайплайна")


if __name__ == "__main__":
    main()

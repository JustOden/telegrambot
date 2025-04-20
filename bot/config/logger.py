import logging


def start_logging():
    logging.basicConfig(
        # filename="log.txt",
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)

    return logging.getLogger()
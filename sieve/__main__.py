from sieve.logger import DATADOG_LOG_CLIENT, get_logger


logger = get_logger(__name__)


def main():
    try:
        logger.info("MESSAGE")

    finally:
        if DATADOG_LOG_CLIENT:
            DATADOG_LOG_CLIENT.close()


if __name__ == "__main__":
    main()

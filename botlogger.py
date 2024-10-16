import logging


# Custom filter to ignore 'getUpdates' log messages.
class HttpxFilter(logging.Filter):
    def filter(self, record):
        # Check if the log message contains 'getUpdates' and ignore it.
        return 'getUpdates' not in record.getMessage()


def get_logger():
    # Configure logging module.
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Get the httpx logger and add the filter to suppress getUpdates logs.
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.addFilter(HttpxFilter())

    logger = logging.getLogger(__name__)
    return logger

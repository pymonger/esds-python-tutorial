import os, logging


def ensure_dir(d):
    """Ensure directory exists."""

    if not os.path.isdir(d):
        os.makedirs(d, 0755)


def get_logger(name):
    """Return preconfigured logger."""

    log_fmt = "[%(asctime)s %(name)s %(levelname)s] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_fmt)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger

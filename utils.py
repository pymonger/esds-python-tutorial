import os


def ensure_dir(d):
    """Ensure directory exists."""

    if not os.path.isdir(d):
        os.makedirs(d, 0755)

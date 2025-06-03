import logging
import sys

from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Optional: You can replace these colors with others or use colorama for cross-platform support
LOG_COLORS = {
    logging.DEBUG: Fore.BLUE,
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
}


LEVEL_NAME_MAP = {
    logging.DEBUG: "DBG",
    logging.INFO: "INF",
    logging.WARNING: "WRN",
    logging.ERROR: "ERR",
    logging.CRITICAL: "CRT",
}


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        # Patch the levelname
        if record.levelno in LEVEL_NAME_MAP:
            record.levelname = LEVEL_NAME_MAP[record.levelno]

        color = LOG_COLORS.get(record.levelno, "")
        formatted = super().format(record)
        return f"{color}{formatted}{Style.RESET_ALL}"


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.ERROR

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = ColoredFormatter(
        fmt="%(levelname)s | %(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove default handlers if any (avoid duplicate logs)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(handler)

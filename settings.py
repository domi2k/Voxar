import logging
import logging.handlers
import os

import discord
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
GUILD_OBJECT = discord.Object(id=GUILD_ID) if GUILD_ID else None
WAVELINK_PASSWORD = os.getenv("WAVELINK_PASSWORD")


class CustomFormatter(logging.Formatter):
    black = "\x1b[30m"
    grey = "\x1b[90m"
    white = "\x1b[97m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    purple = "\x1b[35m"

    reset = "\x1b[0m"
    bold = "\x1b[1m"

    FORMATS = {
        logging.DEBUG:
            f"{black}%(asctime)s {bold}{white}%(levelname)-8s {grey}%(name)s{reset} {white}%(message)s{reset}",
        logging.INFO:
            f"{black}%(asctime)s {bold}{green}%(levelname)-8s {grey}%(name)s{reset} {green}%(message)s{reset}",
        logging.WARNING:
            f"{black}%(asctime)s {bold}{yellow}%(levelname)-8s {grey}%(name)s{reset} {yellow}%(message)s{reset}",
        logging.ERROR:
            f"{black}%(asctime)s {bold}{red}%(levelname)-8s {grey}%(name)s{reset} {red}%(message)s{reset}",
        logging.CRITICAL:
            f"{black}%(asctime)s {bold}{purple}%(levelname)-8s {grey}%(name)s{reset} {purple}%(message)s{reset}",
    }

    def format(self, record) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logger():
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        filename="discord.log",
        encoding="utf-8",
        maxBytes=32 * 1024 * 1024,
        backupCount=5,
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    file_formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger

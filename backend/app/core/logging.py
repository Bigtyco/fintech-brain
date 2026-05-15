import sys
from loguru import logger
from datetime import datetime, timezone, timedelta

_BJT = timezone(timedelta(hours=8))


def _beijing_time(record):
    record["time"] = record["time"].astimezone(_BJT)


logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    patcher=_beijing_time,
)
logger.add(
    "logs/app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="10 MB",
    retention="7 days",
    compression="gz",
    level="DEBUG",
    patcher=_beijing_time,
)

import logging
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


def _path(file_key: str) -> Path:
    return Path(settings.STORAGE_PATH) / file_key


def save(file_bytes: bytes, file_key: str) -> str:
    dest = _path(file_key)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(file_bytes)
    logger.info("Saved file: %s", dest)
    return file_key


def delete(file_key: str) -> None:
    path = _path(file_key)
    if path.exists():
        path.unlink()
        logger.info("Deleted file: %s", path)


def get_bytes(file_key: str) -> bytes:
    return _path(file_key).read_bytes()


def exists(file_key: str) -> bool:
    return _path(file_key).exists()

"""Tags use cases."""
from app.core.exceptions import AppError

from . import repository
from .dto import SaveTagDto, TagDto, TagSummaryDto


def list_with_usage() -> list[TagSummaryDto]:
    return repository.find_all_with_usage()


def list_all() -> list[TagDto]:
    return repository.find_all()


def get_or_fail(tag_id: int) -> TagDto:
    tag = repository.find_by_id(tag_id)
    if tag is None:
        raise AppError("La etiqueta no existe.")
    return tag


def create(payload: SaveTagDto) -> int:
    return repository.create(payload)


def update(tag_id: int, payload: SaveTagDto) -> None:
    repository.update(tag_id, payload)


def remove(tag_id: int) -> None:
    repository.remove(tag_id)

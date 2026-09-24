"""Categories use cases."""
from app.core.exceptions import AppError

from . import repository
from .dto import SaveCategoryDto, CategoryDto, CategorySummaryDto


def list_with_usage() -> list[CategorySummaryDto]:
    return repository.find_all_with_usage()


def list_all() -> list[CategoryDto]:
    return repository.find_all()


def get_or_fail(category_id: int) -> CategoryDto:
    category = repository.find_by_id(category_id)
    if category is None:
        raise AppError("La categoria no existe.")
    return category


def create(payload: SaveCategoryDto) -> int:
    return repository.create(payload)


def update(category_id: int, payload: SaveCategoryDto) -> None:
    repository.update(category_id, payload)


def remove(category_id: int) -> None:
    repository.remove(category_id)

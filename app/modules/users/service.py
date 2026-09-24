"""Users use cases.

Thin on purpose: the rules that matter (unique email, email format, cascade
on delete) are enforced by the database, so the service only turns a missing
record into a message and hands everything else to the repository.
"""
from app.core.exceptions import AppError

from . import repository
from .dto import SaveUserDto, UserDto, UserSummaryDto


def list_with_usage() -> list[UserSummaryDto]:
    return repository.find_all_with_usage()


def list_all() -> list[UserDto]:
    """Used by other modules to fill their author pickers."""
    return repository.find_all()


def get_or_fail(user_id: int) -> UserDto:
    user = repository.find_by_id(user_id)
    if user is None:
        raise AppError("El usuario no existe.")
    return user


def create(payload: SaveUserDto) -> int:
    return repository.create(payload)


def update(user_id: int, payload: SaveUserDto) -> None:
    repository.update(user_id, payload)


def remove(user_id: int) -> None:
    repository.remove(user_id)

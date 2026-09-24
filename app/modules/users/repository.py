"""Stored program calls backing the users module.

Every function here maps one to one onto a package member, so the PL/SQL
object behind each screen stays visible from the Python side.
"""
from app.core.oracle import call_function, call_procedure, fetch_all, fetch_one

from .dto import SaveUserDto, UserDto, UserSummaryDto


def create(payload: SaveUserDto) -> int:
    """blog_pkg.create_user -> the user_id drawn from seq_users."""
    return int(call_function(
        "blog_pkg.create_user", [payload.name, payload.email]))


def find_by_id(user_id: int) -> UserDto | None:
    """blog_pkg.get_user"""
    row = fetch_one("blog_pkg.get_user", [user_id])
    return UserDto.from_row(row) if row else None


def find_all() -> list[UserDto]:
    """blog_pkg.list_users"""
    return [UserDto.from_row(row) for row in fetch_all("blog_pkg.list_users")]


def find_all_with_usage() -> list[UserSummaryDto]:
    """blog_web_pkg.list_users_with_usage"""
    rows = fetch_all("blog_web_pkg.list_users_with_usage")
    return [UserSummaryDto.from_row(row) for row in rows]


def update(user_id: int, payload: SaveUserDto) -> None:
    """blog_pkg.update_user -> raises ORA-20003 when the user is gone."""
    call_procedure(
        "blog_pkg.update_user", [user_id, payload.name, payload.email])


def remove(user_id: int) -> None:
    """blog_pkg.delete_user

    Articles follow through ON DELETE CASCADE, comments stay but turn
    anonymous through ON DELETE SET NULL.
    """
    call_procedure("blog_pkg.delete_user", [user_id])

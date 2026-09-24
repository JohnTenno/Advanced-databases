"""Shapes travelling in and out of the users module."""
from dataclasses import dataclass
from datetime import datetime

from app.core.oracle import Row
from app.core.request_parser import text


@dataclass(frozen=True)
class UserDto:
    """A row of blog_users as the templates consume it."""

    user_id: int
    name: str
    email: str
    created_at: datetime

    @classmethod
    def from_row(cls, row: Row) -> "UserDto":
        return cls(
            user_id=int(row["user_id"]),
            name=row["name"],
            email=row["email"],
            created_at=row["created_at"],
        )


@dataclass(frozen=True)
class UserSummaryDto(UserDto):
    """A user plus how much content they have authored."""

    article_count: int = 0
    comment_count: int = 0

    @classmethod
    def from_row(cls, row: Row) -> "UserSummaryDto":
        return cls(
            user_id=int(row["user_id"]),
            name=row["name"],
            email=row["email"],
            created_at=row["created_at"],
            article_count=int(row["article_count"]),
            comment_count=int(row["comment_count"]),
        )


@dataclass(frozen=True)
class SaveUserDto:
    """Fields accepted when creating or updating a user."""

    name: str
    email: str

    @classmethod
    def from_form(cls) -> "SaveUserDto":
        return cls(
            name=text("name", required=True, label="nombre"),
            email=text("email", required=True, label="correo"),
        )

"""Shapes travelling in and out of the comments module."""
from dataclasses import dataclass
from datetime import datetime

from app.core.oracle import Row
from app.core.request_parser import integer, text


@dataclass(frozen=True)
class CommentDto:
    """A row of comments.

    user_id is nullable: a visitor without an account leaves a name and the
    comment stays anonymous. It also becomes null when the author's account
    is deleted, through ON DELETE SET NULL.
    """

    comment_id: int
    article_id: int
    user_id: int | None
    name: str
    url: str | None
    body_text: str
    created_at: datetime

    @classmethod
    def from_row(cls, row: Row) -> "CommentDto":
        return cls(
            comment_id=int(row["comment_id"]),
            article_id=int(row["article_id"]),
            user_id=int(row["user_id"]) if row["user_id"] is not None else None,
            name=row["name"],
            url=row["url"],
            body_text=row["body_text"],
            created_at=row["created_at"],
        )


@dataclass(frozen=True)
class SaveCommentDto:
    """Fields accepted when posting or editing a comment."""

    user_id: int | None
    name: str
    url: str | None
    body_text: str

    @classmethod
    def from_form(cls) -> "SaveCommentDto":
        return cls(
            user_id=integer("user_id"),
            name=text("name", required=True, label="nombre"),
            url=text("url"),
            body_text=text("body_text", required=True, label="comentario"),
        )

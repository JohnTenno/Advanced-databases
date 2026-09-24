"""Shapes travelling in and out of the articles module."""
from dataclasses import dataclass
from datetime import datetime

from app.core.oracle import Row
from app.core.request_parser import integer, text


@dataclass(frozen=True)
class ArticleDto:
    """A row of articles, straight from the table."""

    article_id: int
    user_id: int
    title: str
    body_text: str
    post_date: datetime
    status: str

    @classmethod
    def from_row(cls, row: Row) -> "ArticleDto":
        return cls(
            article_id=int(row["article_id"]),
            user_id=int(row["user_id"]),
            title=row["title"],
            body_text=row["body_text"] or "",
            post_date=row["post_date"],
            status=row["status"],
        )


@dataclass(frozen=True)
class ArticleListItemDto:
    """A listing row: article plus author name and comment total."""

    article_id: int
    user_id: int
    author_name: str
    title: str
    post_date: datetime
    status: str
    comment_count: int

    @classmethod
    def from_row(cls, row: Row) -> "ArticleListItemDto":
        return cls(
            article_id=int(row["article_id"]),
            user_id=int(row["user_id"]),
            author_name=row["author_name"],
            title=row["title"],
            post_date=row["post_date"],
            status=row["status"],
            comment_count=int(row["comment_count"]),
        )


@dataclass(frozen=True)
class ArticleDetailDto:
    """Everything the detail page shows above the comments."""

    article_id: int
    user_id: int
    author_name: str
    author_email: str
    title: str
    body_text: str
    post_date: datetime
    status: str
    comment_count: int

    @classmethod
    def from_row(cls, row: Row) -> "ArticleDetailDto":
        return cls(
            article_id=int(row["article_id"]),
            user_id=int(row["user_id"]),
            author_name=row["author_name"],
            author_email=row["author_email"],
            title=row["title"],
            body_text=row["body_text"] or "",
            post_date=row["post_date"],
            status=row["status"],
            comment_count=int(row["comment_count"]),
        )


@dataclass(frozen=True)
class SaveArticleDto:
    """Fields accepted when creating or updating an article.

    body_text goes to a CLOB column; python-oracledb binds a plain str to it
    without the 32767 character ceiling a VARCHAR2 bind would impose.
    """

    user_id: int
    title: str
    body_text: str
    status: str

    @classmethod
    def from_form(cls, default_status: str = "DRAFT") -> "SaveArticleDto":
        return cls(
            user_id=integer("user_id", required=True, label="autor"),
            title=text("title", required=True, label="titulo"),
            body_text=text("body_text", required=True, label="texto"),
            status=text("status") or default_status,
        )

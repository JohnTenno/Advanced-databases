"""Shapes travelling in and out of the tags module."""
from dataclasses import dataclass

from app.core.oracle import Row
from app.core.request_parser import text


@dataclass(frozen=True)
class TagDto:
    """A row of tags. Both name and url carry a UNIQUE constraint."""

    tag_id: int
    name: str
    url: str

    @classmethod
    def from_row(cls, row: Row) -> "TagDto":
        return cls(
            tag_id=int(row["tag_id"]),
            name=row["name"],
            url=row["url"],
        )


@dataclass(frozen=True)
class TagSummaryDto(TagDto):
    """A tag plus how many articles use it."""

    article_count: int = 0

    @classmethod
    def from_row(cls, row: Row) -> "TagSummaryDto":
        return cls(
            tag_id=int(row["tag_id"]),
            name=row["name"],
            url=row["url"],
            article_count=int(row["article_count"]),
        )


@dataclass(frozen=True)
class SaveTagDto:
    """Fields accepted when creating or updating a tag."""

    name: str
    url: str

    @classmethod
    def from_form(cls) -> "SaveTagDto":
        return cls(
            name=text("name", required=True, label="nombre"),
            url=text("url", required=True, label="URL"),
        )

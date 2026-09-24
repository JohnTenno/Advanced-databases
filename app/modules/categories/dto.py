"""Shapes travelling in and out of the categories module."""
from dataclasses import dataclass

from app.core.oracle import Row
from app.core.request_parser import text


@dataclass(frozen=True)
class CategoryDto:
    """A row of categories. Both name and url carry a UNIQUE constraint."""

    category_id: int
    name: str
    url: str

    @classmethod
    def from_row(cls, row: Row) -> "CategoryDto":
        return cls(
            category_id=int(row["category_id"]),
            name=row["name"],
            url=row["url"],
        )


@dataclass(frozen=True)
class CategorySummaryDto(CategoryDto):
    """A category plus how many articles use it."""

    article_count: int = 0

    @classmethod
    def from_row(cls, row: Row) -> "CategorySummaryDto":
        return cls(
            category_id=int(row["category_id"]),
            name=row["name"],
            url=row["url"],
            article_count=int(row["article_count"]),
        )


@dataclass(frozen=True)
class SaveCategoryDto:
    """Fields accepted when creating or updating a category."""

    name: str
    url: str

    @classmethod
    def from_form(cls) -> "SaveCategoryDto":
        return cls(
            name=text("name", required=True, label="nombre"),
            url=text("url", required=True, label="URL"),
        )

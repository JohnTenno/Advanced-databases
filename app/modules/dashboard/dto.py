"""The single row of totals shown on the landing page."""
from dataclasses import dataclass

from app.core.oracle import Row


@dataclass(frozen=True)
class DashboardDto:
    """One counter per table in the model."""

    total_users: int
    total_articles: int
    total_published: int
    total_drafts: int
    total_comments: int
    total_tags: int
    total_categories: int

    @classmethod
    def from_row(cls, row: Row) -> "DashboardDto":
        return cls(**{field: int(row[field]) for field in cls.__annotations__})

"""Stored program calls backing the categories module."""
from app.core.oracle import call_function, call_procedure, fetch_all, fetch_one

from .dto import SaveCategoryDto, CategoryDto, CategorySummaryDto


def create(payload: SaveCategoryDto) -> int:
    """blog_pkg.create_category -> the generated category_id."""
    return int(call_function("blog_pkg.create_category", [payload.name, payload.url]))


def find_by_id(category_id: int) -> CategoryDto | None:
    """blog_pkg.get_category"""
    row = fetch_one("blog_pkg.get_category", [category_id])
    return CategoryDto.from_row(row) if row else None


def find_all() -> list[CategoryDto]:
    """blog_pkg.list_categories"""
    return [CategoryDto.from_row(row) for row in fetch_all("blog_pkg.list_categories")]


def find_all_with_usage() -> list[CategorySummaryDto]:
    """blog_web_pkg.list_categories_with_usage"""
    rows = fetch_all("blog_web_pkg.list_categories_with_usage")
    return [CategorySummaryDto.from_row(row) for row in rows]


def update(category_id: int, payload: SaveCategoryDto) -> None:
    """blog_pkg.update_category -> raises ORA-20010 when it is gone."""
    call_procedure("blog_pkg.update_category", [category_id, payload.name, payload.url])


def remove(category_id: int) -> None:
    """blog_pkg.delete_category -> article links follow by ON DELETE CASCADE."""
    call_procedure("blog_pkg.delete_category", [category_id])

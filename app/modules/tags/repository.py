"""Stored program calls backing the tags module."""
from app.core.oracle import call_function, call_procedure, fetch_all, fetch_one

from .dto import SaveTagDto, TagDto, TagSummaryDto


def create(payload: SaveTagDto) -> int:
    """blog_pkg.create_tag -> the generated tag_id."""
    return int(call_function("blog_pkg.create_tag", [payload.name, payload.url]))


def find_by_id(tag_id: int) -> TagDto | None:
    """blog_pkg.get_tag"""
    row = fetch_one("blog_pkg.get_tag", [tag_id])
    return TagDto.from_row(row) if row else None


def find_all() -> list[TagDto]:
    """blog_pkg.list_tags"""
    return [TagDto.from_row(row) for row in fetch_all("blog_pkg.list_tags")]


def find_all_with_usage() -> list[TagSummaryDto]:
    """blog_web_pkg.list_tags_with_usage"""
    rows = fetch_all("blog_web_pkg.list_tags_with_usage")
    return [TagSummaryDto.from_row(row) for row in rows]


def update(tag_id: int, payload: SaveTagDto) -> None:
    """blog_pkg.update_tag -> raises ORA-20008 when the tag is gone."""
    call_procedure("blog_pkg.update_tag", [tag_id, payload.name, payload.url])


def remove(tag_id: int) -> None:
    """blog_pkg.delete_tag -> article links follow by ON DELETE CASCADE."""
    call_procedure("blog_pkg.delete_tag", [tag_id])

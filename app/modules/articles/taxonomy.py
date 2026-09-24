"""The two many-to-many links an article has: tags and categories.

Both relations behave identically, so the pair of tables is driven through
one small set of functions instead of duplicating a module.

Note the asymmetry coming from the package: assign_* is idempotent (it traps
DUP_VAL_ON_INDEX), while remove_* raises ORA-20012 / ORA-20013 when the link
was not there, so removing twice is reported as an error on purpose.
"""
from app.core.oracle import call_procedure, fetch_all

from app.modules.categories.dto import CategoryDto
from app.modules.tags.dto import TagDto


def list_tags(article_id: int) -> list[TagDto]:
    """blog_web_pkg.list_article_tags -> tags already on the article."""
    rows = fetch_all("blog_web_pkg.list_article_tags", [article_id])
    return [TagDto.from_row(row) for row in rows]


def list_unassigned_tags(article_id: int) -> list[TagDto]:
    """blog_web_pkg.list_available_tags -> what the picker should offer."""
    rows = fetch_all("blog_web_pkg.list_available_tags", [article_id])
    return [TagDto.from_row(row) for row in rows]


def assign_tag(article_id: int, tag_id: int) -> None:
    """blog_pkg.assign_tag"""
    call_procedure("blog_pkg.assign_tag", [article_id, tag_id])


def remove_tag(article_id: int, tag_id: int) -> None:
    """blog_pkg.remove_tag -> raises ORA-20012 when it was not assigned."""
    call_procedure("blog_pkg.remove_tag", [article_id, tag_id])


def list_categories(article_id: int) -> list[CategoryDto]:
    """blog_web_pkg.list_article_categories"""
    rows = fetch_all("blog_web_pkg.list_article_categories", [article_id])
    return [CategoryDto.from_row(row) for row in rows]


def list_unassigned_categories(article_id: int) -> list[CategoryDto]:
    """blog_web_pkg.list_available_categories"""
    rows = fetch_all("blog_web_pkg.list_available_categories", [article_id])
    return [CategoryDto.from_row(row) for row in rows]


def assign_category(article_id: int, category_id: int) -> None:
    """blog_pkg.assign_category"""
    call_procedure("blog_pkg.assign_category", [article_id, category_id])


def remove_category(article_id: int, category_id: int) -> None:
    """blog_pkg.remove_category -> raises ORA-20013 when it was not assigned."""
    call_procedure("blog_pkg.remove_category", [article_id, category_id])

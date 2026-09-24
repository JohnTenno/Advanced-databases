"""Stored program calls backing the articles module."""
from app.core.oracle import call_function, call_procedure, fetch_all, fetch_one

from .dto import ArticleDetailDto, ArticleDto, ArticleListItemDto, SaveArticleDto


def create(payload: SaveArticleDto) -> int:
    """blog_pkg.create_article -> the generated article_id."""
    return int(call_function("blog_pkg.create_article", [
        payload.user_id, payload.title, payload.body_text, payload.status]))


def find_by_id(article_id: int) -> ArticleDto | None:
    """blog_pkg.get_article"""
    row = fetch_one("blog_pkg.get_article", [article_id])
    return ArticleDto.from_row(row) if row else None


def find_detail(article_id: int) -> ArticleDetailDto | None:
    """blog_web_pkg.get_article_full"""
    row = fetch_one("blog_web_pkg.get_article_full", [article_id])
    return ArticleDetailDto.from_row(row) if row else None


def find_all() -> list[ArticleListItemDto]:
    """blog_web_pkg.list_articles_full

    Reuses blog_pkg.count_article_comments for the comment column instead of
    issuing one extra call per row.
    """
    rows = fetch_all("blog_web_pkg.list_articles_full")
    return [ArticleListItemDto.from_row(row) for row in rows]


def update(article_id: int, payload: SaveArticleDto) -> None:
    """blog_pkg.update_article -> raises ORA-20005 when the article is gone."""
    call_procedure("blog_pkg.update_article", [
        article_id, payload.user_id, payload.title,
        payload.body_text, payload.status])


def publish(article_id: int) -> None:
    """blog_pkg.publish_article -> sets PUBLISHED and post_date = SYSDATE."""
    call_procedure("blog_pkg.publish_article", [article_id])


def remove(article_id: int) -> None:
    """blog_pkg.delete_article -> comments and links follow by cascade."""
    call_procedure("blog_pkg.delete_article", [article_id])


def count_comments(article_id: int) -> int:
    """blog_pkg.count_article_comments -> read only, so no commit."""
    return int(call_function(
        "blog_pkg.count_article_comments", [article_id], commit=False))

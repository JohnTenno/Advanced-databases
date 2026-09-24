"""Stored program calls backing the comments module."""
from app.core.oracle import call_function, call_procedure, fetch_all, fetch_one

from .dto import CommentDto, SaveCommentDto


def create(article_id: int, payload: SaveCommentDto) -> int:
    """blog_pkg.create_comment -> the generated comment_id."""
    return int(call_function("blog_pkg.create_comment", [
        article_id, payload.user_id, payload.name,
        payload.url, payload.body_text]))


def find_by_id(comment_id: int) -> CommentDto | None:
    """blog_pkg.get_comment"""
    row = fetch_one("blog_pkg.get_comment", [comment_id])
    return CommentDto.from_row(row) if row else None


def find_by_article(article_id: int) -> list[CommentDto]:
    """blog_pkg.list_comments_by_article -> newest first."""
    rows = fetch_all("blog_pkg.list_comments_by_article", [article_id])
    return [CommentDto.from_row(row) for row in rows]


def update(comment_id: int, payload: SaveCommentDto) -> None:
    """blog_pkg.update_comment -> raises ORA-20006 when the comment is gone."""
    call_procedure("blog_pkg.update_comment", [
        comment_id, payload.user_id, payload.name,
        payload.url, payload.body_text])


def remove(comment_id: int) -> None:
    """blog_pkg.delete_comment -> raises ORA-20007 when the comment is gone."""
    call_procedure("blog_pkg.delete_comment", [comment_id])

"""Comments use cases."""
from app.core.exceptions import AppError

from . import repository
from .dto import CommentDto, SaveCommentDto


def list_for_article(article_id: int) -> list[CommentDto]:
    return repository.find_by_article(article_id)


def get_or_fail(comment_id: int) -> CommentDto:
    comment = repository.find_by_id(comment_id)
    if comment is None:
        raise AppError("El comentario no existe.")
    return comment


def create(article_id: int, payload: SaveCommentDto) -> int:
    return repository.create(article_id, payload)


def update(comment_id: int, payload: SaveCommentDto) -> None:
    repository.update(comment_id, payload)


def remove(comment_id: int) -> int:
    """Delete the comment and report which article to navigate back to.

    The lookup happens first because once the row is gone there is no way to
    know where it belonged.
    """
    comment = get_or_fail(comment_id)
    repository.remove(comment_id)
    return comment.article_id

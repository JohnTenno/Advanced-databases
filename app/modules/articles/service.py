"""Articles use cases.

The detail page needs six queries that belong together, so the service
assembles them once and hands the controller a single view model.
"""
from dataclasses import dataclass

from app.core.exceptions import AppError
from app.modules.categories.dto import CategoryDto
from app.modules.comments import service as comments_service
from app.modules.comments.dto import CommentDto
from app.modules.tags.dto import TagDto
from app.modules.users import service as users_service
from app.modules.users.dto import UserDto

from . import repository, taxonomy
from .dto import ArticleDetailDto, ArticleDto, ArticleListItemDto, SaveArticleDto


@dataclass(frozen=True)
class ArticleDetailView:
    """Everything the detail template renders, gathered in one place."""

    article: ArticleDetailDto
    comments: list[CommentDto]
    tags: list[TagDto]
    categories: list[CategoryDto]
    available_tags: list[TagDto]
    available_categories: list[CategoryDto]
    users: list[UserDto]


def list_all() -> list[ArticleListItemDto]:
    return repository.find_all()


def get_or_fail(article_id: int) -> ArticleDto:
    article = repository.find_by_id(article_id)
    if article is None:
        raise AppError("El articulo no existe.")
    return article


def get_detail(article_id: int) -> ArticleDetailView:
    article = repository.find_detail(article_id)
    if article is None:
        raise AppError("El articulo no existe.")

    return ArticleDetailView(
        article=article,
        comments=comments_service.list_for_article(article_id),
        tags=taxonomy.list_tags(article_id),
        categories=taxonomy.list_categories(article_id),
        available_tags=taxonomy.list_unassigned_tags(article_id),
        available_categories=taxonomy.list_unassigned_categories(article_id),
        users=users_service.list_all(),
    )


def list_authors() -> list[UserDto]:
    """An article needs an author, so the form needs the user list."""
    return users_service.list_all()


def create(payload: SaveArticleDto) -> int:
    return repository.create(payload)


def update(article_id: int, payload: SaveArticleDto) -> None:
    repository.update(article_id, payload)


def publish(article_id: int) -> None:
    repository.publish(article_id)


def remove(article_id: int) -> None:
    repository.remove(article_id)

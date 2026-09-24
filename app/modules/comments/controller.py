"""HTTP routes for comments.

Posting hangs off the article URL, while editing and deleting address the
comment on its own.
"""
from flask import Blueprint, flash, redirect, render_template, url_for

from app.modules.users import service as users_service

from . import service
from .dto import SaveCommentDto

blueprint = Blueprint("comments", __name__)


@blueprint.post("/articles/<int:article_id>/comments")
def create(article_id: int):
    service.create(article_id, SaveCommentDto.from_form())
    flash("Comentario publicado.", "success")
    return redirect(url_for("articles.detail", article_id=article_id))


@blueprint.get("/comments/<int:comment_id>/edit")
def edit_form(comment_id: int):
    return render_template(
        "comments/edit.html",
        comment=service.get_or_fail(comment_id),
        users=users_service.list_all())


@blueprint.post("/comments/<int:comment_id>/edit")
def edit(comment_id: int):
    comment = service.get_or_fail(comment_id)
    service.update(comment_id, SaveCommentDto.from_form())
    flash("Comentario actualizado.", "success")
    return redirect(url_for("articles.detail", article_id=comment.article_id))


@blueprint.post("/comments/<int:comment_id>/delete")
def remove(comment_id: int):
    article_id = service.remove(comment_id)
    flash("Comentario eliminado.", "success")
    return redirect(url_for("articles.detail", article_id=article_id))

"""HTTP routes for /articles, including its tag and category links."""
from flask import Blueprint, flash, redirect, render_template, url_for

from app.core.request_parser import integer

from . import service, taxonomy
from .dto import SaveArticleDto

blueprint = Blueprint("articles", __name__, url_prefix="/articles")


@blueprint.get("/")
def index():
    return render_template("articles/index.html", articles=service.list_all())


@blueprint.get("/new")
def create_form():
    authors = service.list_authors()
    if not authors:
        flash("Primero hay que registrar al menos un usuario.", "warning")
        return redirect(url_for("users.index"))
    return render_template("articles/form.html", article=None, authors=authors)


@blueprint.post("/new")
def create():
    article_id = service.create(SaveArticleDto.from_form())
    flash(f"Articulo creado con id {article_id}.", "success")
    return redirect(url_for("articles.detail", article_id=article_id))


@blueprint.get("/<int:article_id>")
def detail(article_id: int):
    return render_template(
        "articles/detail.html", view=service.get_detail(article_id))


@blueprint.get("/<int:article_id>/edit")
def edit_form(article_id: int):
    return render_template(
        "articles/form.html",
        article=service.get_or_fail(article_id),
        authors=service.list_authors())


@blueprint.post("/<int:article_id>/edit")
def edit(article_id: int):
    service.update(article_id, SaveArticleDto.from_form())
    flash("Articulo actualizado.", "success")
    return redirect(url_for("articles.detail", article_id=article_id))


@blueprint.post("/<int:article_id>/publish")
def publish(article_id: int):
    service.publish(article_id)
    flash("Articulo publicado.", "success")
    return redirect(url_for("articles.detail", article_id=article_id))


@blueprint.post("/<int:article_id>/delete")
def remove(article_id: int):
    service.remove(article_id)
    flash("Articulo eliminado con sus comentarios y relaciones.", "success")
    return redirect(url_for("articles.index"))


@blueprint.post("/<int:article_id>/tags/assign")
def assign_tag(article_id: int):
    taxonomy.assign_tag(
        article_id, integer("tag_id", required=True, label="etiqueta"))
    flash("Etiqueta asignada.", "success")
    return redirect(url_for("articles.detail", article_id=article_id))


@blueprint.post("/<int:article_id>/tags/<int:tag_id>/remove")
def remove_tag(article_id: int, tag_id: int):
    taxonomy.remove_tag(article_id, tag_id)
    flash("Etiqueta retirada.", "success")
    return redirect(url_for("articles.detail", article_id=article_id))


@blueprint.post("/<int:article_id>/categories/assign")
def assign_category(article_id: int):
    taxonomy.assign_category(
        article_id, integer("category_id", required=True, label="categoria"))
    flash("Categoria asignada.", "success")
    return redirect(url_for("articles.detail", article_id=article_id))


@blueprint.post("/<int:article_id>/categories/<int:category_id>/remove")
def remove_category(article_id: int, category_id: int):
    taxonomy.remove_category(article_id, category_id)
    flash("Categoria retirada.", "success")
    return redirect(url_for("articles.detail", article_id=article_id))

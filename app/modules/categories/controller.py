"""HTTP routes for /categories.

Categories and tags have the same columns and the same CRUD, so both render
the shared catalog templates and only pass their own labels and endpoints.
"""
from flask import Blueprint, flash, redirect, render_template, url_for

from . import service
from .dto import SaveCategoryDto

blueprint = Blueprint("categories", __name__, url_prefix="/categories")

CATALOG = {
    "title": "Categorias",
    "singular": "categoria",
    "id_field": "category_id",
    "endpoints": {
        "index": "categories.index",
        "create": "categories.create",
        "edit": "categories.edit_form",
        "save": "categories.edit",
        "remove": "categories.remove",
    },
}


@blueprint.get("/")
def index():
    return render_template(
        "catalog/index.html", catalog=CATALOG, records=service.list_with_usage())


@blueprint.post("/")
def create():
    category_id = service.create(SaveCategoryDto.from_form())
    flash(f"Categoria creada con id {category_id}.", "success")
    return redirect(url_for("categories.index"))


@blueprint.get("/<int:category_id>/edit")
def edit_form(category_id: int):
    return render_template(
        "catalog/edit.html", catalog=CATALOG, record=service.get_or_fail(category_id))


@blueprint.post("/<int:category_id>/edit")
def edit(category_id: int):
    service.update(category_id, SaveCategoryDto.from_form())
    flash("Categoria actualizada.", "success")
    return redirect(url_for("categories.index"))


@blueprint.post("/<int:category_id>/delete")
def remove(category_id: int):
    service.remove(category_id)
    flash("Categoria eliminada.", "success")
    return redirect(url_for("categories.index"))

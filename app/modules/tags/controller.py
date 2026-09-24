"""HTTP routes for /tags.

Tags and categories have the same columns and the same CRUD, so both render
the shared catalog templates and only pass their own labels and endpoints.
"""
from flask import Blueprint, flash, redirect, render_template, url_for

from . import service
from .dto import SaveTagDto

blueprint = Blueprint("tags", __name__, url_prefix="/tags")

CATALOG = {
    "title": "Etiquetas",
    "singular": "etiqueta",
    "id_field": "tag_id",
    "endpoints": {
        "index": "tags.index",
        "create": "tags.create",
        "edit": "tags.edit_form",
        "save": "tags.edit",
        "remove": "tags.remove",
    },
}


@blueprint.get("/")
def index():
    return render_template(
        "catalog/index.html", catalog=CATALOG, records=service.list_with_usage())


@blueprint.post("/")
def create():
    tag_id = service.create(SaveTagDto.from_form())
    flash(f"Etiqueta creada con id {tag_id}.", "success")
    return redirect(url_for("tags.index"))


@blueprint.get("/<int:tag_id>/edit")
def edit_form(tag_id: int):
    return render_template(
        "catalog/edit.html", catalog=CATALOG, record=service.get_or_fail(tag_id))


@blueprint.post("/<int:tag_id>/edit")
def edit(tag_id: int):
    service.update(tag_id, SaveTagDto.from_form())
    flash("Etiqueta actualizada.", "success")
    return redirect(url_for("tags.index"))


@blueprint.post("/<int:tag_id>/delete")
def remove(tag_id: int):
    service.remove(tag_id)
    flash("Etiqueta eliminada.", "success")
    return redirect(url_for("tags.index"))

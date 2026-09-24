"""HTTP routes for /users."""
from flask import Blueprint, flash, redirect, render_template, url_for

from . import service
from .dto import SaveUserDto

blueprint = Blueprint("users", __name__, url_prefix="/users")


@blueprint.get("/")
def index():
    return render_template("users/index.html", users=service.list_with_usage())


@blueprint.post("/")
def create():
    user_id = service.create(SaveUserDto.from_form())
    flash(f"Usuario creado con id {user_id}.", "success")
    return redirect(url_for("users.index"))


@blueprint.get("/<int:user_id>/edit")
def edit_form(user_id: int):
    return render_template("users/edit.html", user=service.get_or_fail(user_id))


@blueprint.post("/<int:user_id>/edit")
def edit(user_id: int):
    service.update(user_id, SaveUserDto.from_form())
    flash("Usuario actualizado.", "success")
    return redirect(url_for("users.index"))


@blueprint.post("/<int:user_id>/delete")
def remove(user_id: int):
    service.remove(user_id)
    flash("Usuario eliminado junto con sus articulos.", "success")
    return redirect(url_for("users.index"))

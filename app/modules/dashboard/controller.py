"""HTTP route for the landing page."""
from flask import Blueprint, render_template

from app.core.oracle import fetch_one
from app.modules.articles import service as articles_service

from .dto import DashboardDto

blueprint = Blueprint("dashboard", __name__)

# How many of the newest articles the landing page previews.
RECENT_ARTICLE_LIMIT = 5


@blueprint.get("/")
def index():
    """blog_web_pkg.dashboard plus the newest articles."""
    totals = DashboardDto.from_row(fetch_one("blog_web_pkg.dashboard"))
    return render_template(
        "dashboard/index.html",
        totals=totals,
        articles=articles_service.list_all()[:RECENT_ARTICLE_LIMIT])

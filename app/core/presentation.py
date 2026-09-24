"""Template filters and globals shared by every page."""
from datetime import datetime

from flask import Flask

ARTICLE_STATUSES = ("DRAFT", "PUBLISHED", "ARCHIVED")

STATUS_LABELS = {
    "DRAFT": "Borrador",
    "PUBLISHED": "Publicado",
    "ARCHIVED": "Archivado",
}

STATUS_STYLES = {
    "DRAFT": "warning",
    "PUBLISHED": "success",
    "ARCHIVED": "secondary",
}


def format_date(value: datetime | None) -> str:
    """Oracle DATE as dd/mm/yyyy."""
    return value.strftime("%d/%m/%Y") if value else "-"


def format_datetime(value: datetime | None) -> str:
    """Oracle DATE including the time, used for comments."""
    return value.strftime("%d/%m/%Y %H:%M") if value else "-"


def register(app: Flask) -> None:
    """Attach the filters and globals to the application."""
    app.add_template_filter(format_date, "date")
    app.add_template_filter(format_datetime, "datetime")

    @app.context_processor
    def inject_globals() -> dict:
        return {
            "article_statuses": ARTICLE_STATUSES,
            "status_labels": STATUS_LABELS,
            "status_styles": STATUS_STYLES,
            "db_target": app.config["APP_CONFIG"].db_target,
        }

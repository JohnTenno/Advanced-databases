"""Feature modules, each one owning its routes, DTOs and data access.

Every module exposes a Flask blueprint named ``blueprint``; adding a feature
means creating a folder here and listing it below.
"""
from flask import Flask

from app.modules.articles.controller import blueprint as articles
from app.modules.categories.controller import blueprint as categories
from app.modules.comments.controller import blueprint as comments
from app.modules.dashboard.controller import blueprint as dashboard
from app.modules.tags.controller import blueprint as tags
from app.modules.users.controller import blueprint as users

BLUEPRINTS = (dashboard, articles, comments, users, tags, categories)


def register_modules(app: Flask) -> None:
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)

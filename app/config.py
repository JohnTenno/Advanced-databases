"""Application settings, read once from the environment."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    """Everything the app needs to boot.

    Defaults match the gvenzl/oracle-xe:21-slim container used in class, so
    the app runs out of the box when .env is missing.
    """

    db_user: str
    db_password: str
    db_dsn: str
    secret_key: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            db_user=os.getenv("DB_USER", "hr"),
            db_password=os.getenv("DB_PASSWORD", "hr"),
            db_dsn=os.getenv("DB_DSN", "localhost:1521/xepdb1"),
            secret_key=os.getenv("SECRET_KEY", "blog-bda-development-key"),
        )

    @property
    def db_target(self) -> str:
        """Human readable connection target, shown in the page footer."""
        return f"{self.db_user}@{self.db_dsn}"

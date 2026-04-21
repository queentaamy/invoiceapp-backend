"""
Create the base application schema.
"""

from app.database.connection import Base
from app.models import models  # noqa: F401 - Registers metadata tables.


MIGRATION_ID = "000_initial_schema"


def upgrade(connection) -> None:
    Base.metadata.create_all(bind=connection)
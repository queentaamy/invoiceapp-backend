"""
Repair drift where the users.name column is missing even though earlier
migrations were marked as applied.
"""

from sqlalchemy import text


MIGRATION_ID = "002_repair_users_name_column"


def upgrade(connection) -> None:
    connection.execute(text("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS name VARCHAR
    """))

    connection.execute(text("""
        UPDATE users
        SET name = split_part(email, '@', 1)
        WHERE name IS NULL OR btrim(name) = ''
    """))
#!/usr/bin/env python3
"""
Apply pending database migrations against PostgreSQL.

Usage:
    python3 scripts/migrate.py
    python3 scripts/migrate.py --list
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> None:
        return None

ROOT_DIR = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT_DIR / "migrations"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import text

load_dotenv()

from app.database.connection import engine


def migration_files() -> list[Path]:
    return sorted(
        path for path in MIGRATIONS_DIR.glob("*.py")
        if path.name != "__init__.py"
    )


def load_migration(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load migration from {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "MIGRATION_ID"):
        raise RuntimeError(f"{path.name} is missing MIGRATION_ID")
    if not hasattr(module, "upgrade"):
        raise RuntimeError(f"{path.name} is missing upgrade(connection)")

    return module


def ensure_migrations_table() -> None:
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """))


def applied_migrations() -> set[str]:
    ensure_migrations_table()
    with engine.connect() as connection:
        rows = connection.execute(
            text("SELECT version FROM schema_migrations ORDER BY version")
        )
        return {row.version for row in rows}


def list_migrations() -> int:
    applied = applied_migrations()

    for path in migration_files():
        module = load_migration(path)
        status = "applied" if module.MIGRATION_ID in applied else "pending"
        print(f"{module.MIGRATION_ID} {status}")

    return 0


def apply_migrations() -> int:
    applied = applied_migrations()
    pending_paths = [
        path for path in migration_files()
        if load_migration(path).MIGRATION_ID not in applied
    ]

    if not pending_paths:
        print("No pending migrations.")
        return 0

    for path in pending_paths:
        module = load_migration(path)
        print(f"Applying {module.MIGRATION_ID}...")
        with engine.begin() as connection:
            module.upgrade(connection)
            connection.execute(
                text("""
                    INSERT INTO schema_migrations (version)
                    VALUES (:version)
                """),
                {"version": module.MIGRATION_ID},
            )
        print(f"Applied {module.MIGRATION_ID}.")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run PostgreSQL migrations.")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List known migrations and whether they are applied.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.list:
        return list_migrations()

    return apply_migrations()


if __name__ == "__main__":
    raise SystemExit(main())
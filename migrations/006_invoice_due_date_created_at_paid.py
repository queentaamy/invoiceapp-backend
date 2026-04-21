"""
Add invoice due dates, creation timestamps, and paid status flags.
"""

from sqlalchemy import text


MIGRATION_ID = "006_invoice_due_date_created_at_paid"


def upgrade(connection) -> None:
    connection.execute(text("""
        ALTER TABLE invoices
        ADD COLUMN IF NOT EXISTS due_date DATE
    """))

    connection.execute(text("""
        ALTER TABLE invoices
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ
    """))

    connection.execute(text("""
        UPDATE invoices
        SET created_at = NOW()
        WHERE created_at IS NULL
    """))

    connection.execute(text("""
        ALTER TABLE invoices
        ALTER COLUMN created_at SET DEFAULT NOW()
    """))

    connection.execute(text("""
        ALTER TABLE invoices
        ALTER COLUMN created_at SET NOT NULL
    """))

    connection.execute(text("""
        ALTER TABLE invoices
        ADD COLUMN IF NOT EXISTS is_paid BOOLEAN
    """))

    connection.execute(text("""
        UPDATE invoices
        SET is_paid = FALSE
        WHERE is_paid IS NULL
    """))

    connection.execute(text("""
        ALTER TABLE invoices
        ALTER COLUMN is_paid SET DEFAULT FALSE
    """))

    connection.execute(text("""
        ALTER TABLE invoices
        ALTER COLUMN is_paid SET NOT NULL
    """))

    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_invoices_created_at
        ON invoices (created_at)
    """))

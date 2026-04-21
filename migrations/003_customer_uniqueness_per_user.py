"""
Scope customer email uniqueness per user instead of globally.
"""

from sqlalchemy import text


MIGRATION_ID = "003_customer_uniqueness_per_user"


def upgrade(connection) -> None:
    # Drop historical global unique constraints/indexes on customer email if present.
    connection.execute(text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.table_constraints
                WHERE table_name = 'customers'
                  AND constraint_type = 'UNIQUE'
                  AND constraint_name = 'customers_email_key'
            ) THEN
                ALTER TABLE customers DROP CONSTRAINT customers_email_key;
            END IF;
        END
        $$;
    """))

    connection.execute(text("""
        DROP INDEX IF EXISTS ux_customers_email;
    """))

    # Enforce uniqueness only inside each user account.
    connection.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS ux_customers_user_email
        ON customers (user_id, email);
    """))

    # Note: do not force name uniqueness here; some existing user data has
    # duplicate names and this migration should remain non-breaking.

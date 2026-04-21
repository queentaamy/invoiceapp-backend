"""
Remove the legacy global unique index on customer email.
"""

from sqlalchemy import text


MIGRATION_ID = "005_drop_global_customer_email_index"


def upgrade(connection) -> None:
    connection.execute(text("""
        DROP INDEX IF EXISTS ix_customers_email;
    """))

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

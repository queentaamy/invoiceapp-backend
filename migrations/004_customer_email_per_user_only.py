from sqlalchemy import text


MIGRATION_ID = "004_customer_email_per_user_only"


def upgrade(connection) -> None:
    connection.execute(text("""
        UPDATE customers
        SET email = lower(btrim(email))
        WHERE email IS NOT NULL
    """))

    # Drop older per-user unique indexes/constraints before recreating the rule.
    connection.execute(text("""
        DROP INDEX IF EXISTS ux_customers_user_email;
    """))

    connection.execute(text("""
        ALTER TABLE customers
        DROP CONSTRAINT IF EXISTS uq_customers_user_email;
    """))

    connection.execute(text("""
        ALTER TABLE customers
        ADD CONSTRAINT uq_customers_user_email
        UNIQUE (user_id, email);
    """))

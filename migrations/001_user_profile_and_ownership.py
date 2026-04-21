from sqlalchemy import text


MIGRATION_ID = "001_user_profile_and_ownership"


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

    connection.execute(text("""
        ALTER TABLE customers
        ADD COLUMN IF NOT EXISTS user_id INTEGER
    """))

    connection.execute(text("""
        ALTER TABLE customers
        ADD COLUMN IF NOT EXISTS customer_number INTEGER
    """))

    connection.execute(text("""
        WITH ranked_customers AS (
            SELECT
                id,
                ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY id) AS seq
            FROM customers
            WHERE user_id IS NOT NULL
        )
        UPDATE customers AS c
        SET customer_number = ranked_customers.seq
        FROM ranked_customers
        WHERE c.id = ranked_customers.id
          AND (c.customer_number IS NULL OR c.customer_number = 0)
    """))

    connection.execute(text("""
        ALTER TABLE invoices
        ADD COLUMN IF NOT EXISTS user_id INTEGER
    """))

    connection.execute(text("""
        UPDATE invoices AS i
        SET user_id = c.user_id
        FROM customers AS c
        WHERE i.customer_id = c.id
          AND i.user_id IS NULL
          AND c.user_id IS NOT NULL
    """))

    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_customers_user_id
        ON customers (user_id)
    """))

    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_customers_customer_number
        ON customers (customer_number)
    """))

    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_invoices_user_id
        ON invoices (user_id)
    """))
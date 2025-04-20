import sqlite3


def create_spending_events_table(connection: sqlite3.Connection) -> None:
    """Create the spending_events table if it doesn't exist."""
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS spending_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        plan_name TEXT NOT NULL,
        billing_start DATE NOT NULL,
        billing_end DATE NOT NULL,
        amount_due REAL
    )
    """)

    conn.commit()


def create_electricity_plans_table(connection: sqlite3.Connection) -> None:
    """Create the electricity_plans table if it doesn't exist."""
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS electricity_plans (
        plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_name TEXT NOT NULL,
        plan_description TEXT NOT NULL,
        selling_points TEXT NOT NULL
    )
    """)

    conn.commit()


def create_all_tables(conn: sqlite3.Connection) -> None:
    """Create all tables for the application."""
    create_spending_events_table(connection=conn)
    create_electricity_plans_table(connection=conn)
    # Add calls to create other tables here


def init_database(db_path: str) -> sqlite3.Connection:
    """Initialize the database with all required tables."""
    try:
        conn = sqlite3.connect(db_path)
        create_all_tables(conn=conn)
        return conn
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        raise


if __name__ == "__main__":
    # This allows running this module directly to just create the schema
    conn = init_database(db_path="demo.db")
    if conn:
        print("Database schema created successfully!")
        conn.close()

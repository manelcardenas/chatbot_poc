import logging
import sqlite3

from src.db.data_generators import populate_all_tables
from src.db.db_schema import init_database

# Database configurations
DB_NAME = "data.db"


def populate_database() -> None:
    """Main function to populate the demo database."""
    try:
        # Initialize database with schema
        conn = init_database(db_path=DB_NAME)
        if not conn:
            logging.error("Failed to initialize database")
            return

        # Populate with sample data
        populate_all_tables(connection=conn)

        logging.info("Database successfully populated!")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    populate_database()

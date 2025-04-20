import sqlite3

from db_schema import init_database
from data_generators import populate_all_tables

# Database configurations
DB_NAME = "demo.db"


def populate_database():
    """Main function to populate the demo database."""
    try:
        # Initialize database with schema
        conn = init_database(db_path=DB_NAME)
        if not conn:
            print("Failed to initialize database")
            return
            
        # Populate with sample data
        populate_all_tables(conn=conn)
        
        print("Database successfully populated!")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    populate_database()

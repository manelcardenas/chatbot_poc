import logging
import sqlite3


def get_customers_data() -> list[tuple]:
    """Generate sample customer data."""
    return [
        (1, "Alice Johnson", "alice.johnson@example.com"),
        (2, "Bob Smith", "bob.smith@example.com"),
    ]


def get_spending_events_data() -> list[tuple]:
    """Generate sample spending events data."""
    # Customer 1 data
    customer1_data = [
        (1, "Standard Plan", "2024-01-01", "2024-01-31", 50.00),
        (1, "Night Plan", "2024-02-01", "2024-02-29", 30.00),
        (1, "Night Plan", "2024-03-01", "2024-03-31", 35.00),
        (1, "Night Plan", "2024-04-01", "2024-04-30", 32.00),
        (1, "Standard Plan", "2024-05-01", "2024-05-31", 54.00),
        (1, "Standard Plan", "2024-06-01", "2024-06-30", 56.00),
        (1, "Standard Plan", "2024-07-01", "2024-07-31", 57.00),
        (1, "Standard Plan", "2024-08-01", "2024-08-31", 58.00),
        (1, "Standard Plan", "2024-09-01", "2024-09-30", 70.00),
        (1, "Standard Plan", "2024-10-01", "2024-10-31", 65.00),
        (1, "Standard Plan", "2024-11-01", "2024-11-30", 68.00),
        (1, "Standard Plan", "2024-12-01", "2024-12-31", 69.00),
    ]

    # Customer 2 data
    customer2_data = [
        (2, "Eco Plan", "2024-01-01", "2024-01-31", 69.00),
        (2, "Eco Plan", "2024-02-01", "2024-02-29", 67.00),
        (2, "Eco Plan", "2024-03-01", "2024-03-31", 70.00),
        (2, "Standard Plan", "2024-04-01", "2024-04-30", 50.00),
        (2, "Standard Plan", "2024-05-01", "2024-05-31", 53.00),
        (2, "Eco Plan", "2024-06-01", "2024-06-30", 63.00),
        (2, "Eco Plan", "2024-07-01", "2024-07-31", 64.00),
        (2, "Eco Plan", "2024-08-01", "2024-08-31", 65.00),
        (2, "Eco Plan", "2024-09-01", "2024-09-30", 66.00),
        (2, "Eco Plan", "2024-10-01", "2024-10-31", 67.00),
        (2, "Eco Plan", "2024-11-01", "2024-11-30", 68.00),
        (2, "Eco Plan", "2024-12-01", "2024-12-31", 69.00),
    ]

    return customer1_data + customer2_data


def get_electricity_plans_data() -> list[tuple]:
    """Generate sample electricity plans data."""
    return [
        (
            1,
            "Standard Plan",
            "A well-rounded electricity plan designed for typical households, offering stable pricing and reliable service without any peak-hour surcharges.",
            "Affordable rates, predictable billing, ideal for families",
        ),
        (
            2,
            "Eco Plan",
            "A renewable energy plan that prioritizes sustainability by sourcing electricity from solar, wind, and hydroelectric power. Perfect for environmentally conscious consumers.",
            "100% green energy, reduces carbon footprint, government incentives may apply",
        ),
        (
            3,
            "Night Plan",
            "An electricity plan that provides significant cost savings for customers who consume most of their energy during off-peak nighttime hours. Ideal for night-shift workers and EV owners.",
            "Lower rates at night, great for electric vehicle charging, smart meter integration",
        ),
    ]


def populate_customers(conn: sqlite3.Connection) -> None:
    """Populate the customers table with sample data."""
    cursor = conn.cursor()

    customers = get_customers_data()

    try:
        cursor.executemany(
            """
        INSERT INTO customers (
            customer_id,
            name,
            email)
        VALUES (?, ?, ?)
        """,
            customers,
        )

        conn.commit()
        logging.info(f"Added {len(customers)} customers")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error populating customers: {e}")


def populate_spending_events(conn: sqlite3.Connection) -> None:
    """Populate the spending_events table with sample data."""
    cursor = conn.cursor()

    spending_events = get_spending_events_data()

    try:
        cursor.executemany(
            """
        INSERT INTO spending_events (
            customer_id,
            plan_name,
            billing_start,
            billing_end,
            amount_due)
        VALUES (?, ?, ?, ?, ?)
        """,
            spending_events,
        )

        conn.commit()
        logging.info(f"Added {len(spending_events)} spending events")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error populating spending events: {e}")


def populate_electricity_plans(conn: sqlite3.Connection) -> None:
    """Populate the electricity_plans table with sample data."""
    cursor = conn.cursor()

    electricity_plans = get_electricity_plans_data()

    try:
        cursor.executemany(
            """
        INSERT INTO electricity_plans (
            plan_id,
            plan_name,
            plan_description,
            selling_points)
        VALUES (?, ?, ?, ?)
        """,
            electricity_plans,
        )

        conn.commit()
        logging.info(f"Added {len(electricity_plans)} electricity plans")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error populating electricity plans: {e}")


def populate_all_tables(connection: sqlite3.Connection) -> None:
    """Populate all tables with sample data."""
    populate_customers(conn=connection)
    populate_spending_events(conn=connection)
    populate_electricity_plans(conn=connection)

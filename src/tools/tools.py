import sqlite3

from langchain_core.tools import tool

DB_PATH = "data.db"


def get_db_connection() -> None:
    """Creates and returns a database connection."""
    # TODO: This does not go here. Move it in the future
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        raise Exception(f"Database connection error: {e}")


@tool
def fetch_spending_events(customer_id: int = 1, months: int = None, plan_name: str = None) -> str:
    """
    Fetches spending events for a customer with optional filtering by months or plan.
    Args:
        customer_id: The ID of the customer (defaults to 1)
        months: Optional number of most recent months to retrieve
        plan_name: Optional plan name to filter by
    Returns:
        A formatted string with the spending events information
    """
    # TODO: Add restriction so the user can only see their own data (customer_id).
    # TODO: this customer_id can be tracked using cache instead of making the llm obtain it every time.
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM spending_events WHERE customer_id = ?"
        params = [customer_id]

        if plan_name:
            query += " AND plan_name = ?"
            params.append(plan_name)

        if months:
            query += " ORDER BY billing_end DESC LIMIT ?"
            params.append(months)
        else:
            query += " ORDER BY billing_end DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()

        if not results:
            return "No spending events found with the given criteria."

        # Get column names for better formatting
        column_names = [description[0] for description in cursor.description]

        # Format the results
        output = "Spending events:\n"
        for row in results:
            output += "\n"
            for i, value in enumerate(row):
                output += f"{column_names[i]}: {value}\n"
            output += "----------"

        return output

    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        if conn:
            conn.close()


@tool
def list_supported_plans() -> list[str]:
    """
    Returns a list of electricity plans supported by the system.
    Returns:
        A list of plan names
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT plan_name FROM electricity_plans")
        results = cursor.fetchall()

        if not results:
            return ["Standard Plan", "Eco Plan", "Night Plan"]  # Fallback if no DB data

        return [row[0] for row in results]

    except sqlite3.Error:
        # Fallback if database error
        return ["Standard Plan", "Eco Plan", "Night Plan"]
    finally:
        if conn:
            conn.close()


@tool
def fetch_plan_information(plan_name: str) -> str:
    """
    Fetches detailed information about a specific electricity plan.
    Args:
        plan_name: The name of the plan to look up
    Returns:
        A formatted string with plan details
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM electricity_plans WHERE plan_name = ?", (plan_name,))
        result = cursor.fetchone()

        if not result:
            return f"No information found for plan: {plan_name}"

        # Get column names for better formatting
        column_names = [description[0] for description in cursor.description]

        # Format the result
        output = f"Information for {plan_name}:\n\n"
        for i, value in enumerate(result):
            if column_names[i] != "plan_id":  # Skip ID for user-facing output
                output += f"{column_names[i]}: {value}\n"

        return output

    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        if conn:
            conn.close()

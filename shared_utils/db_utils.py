import os
import psycopg
from psycopg.rows import dict_row # To fetch results as dictionaries

def connect_to_db(db_prefix="RELATIONAL_"):
    """
    Connects to a PostgreSQL database using environment variables.
    db_prefix should be 'RELATIONAL_' or 'AGE_'.
    """
    host = os.getenv(f"{db_prefix}DB_HOST")
    port = os.getenv(f"{db_prefix}DB_PORT")
    dbname = os.getenv(f"{db_prefix}DB_NAME")
    user = os.getenv(f"{db_prefix}DB_USER")
    password = os.getenv(f"{db_prefix}DB_PASSWORD")

    if not all([host, port, dbname, user, password]):
        raise ValueError(f"Missing one or more database environment variables for {db_prefix}DB.")

    conn_str = f"host={host} port={port} dbname={dbname} user={user} password={password}"
    print(f"Attempting to connect to {dbname} at {host}:{port}")
    return psycopg.connect(conn_str)

def run_sql_command(conn, sql_command, fetch_results=False):
    """
    Executes a SQL command and optionally fetches results.
    """
    try:
        with conn.cursor(row_factory=dict_row) as cur: # Use dict_row for easy access
            cur.execute(sql_command)
            if fetch_results:
                results = cur.fetchall()
                return results
            else:
                conn.commit() # Commit changes for non-SELECT commands
                return None
    except psycopg.Error as e:
        print(f"Database error occurred: {e}")
        conn.rollback() # Rollback in case of error
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise
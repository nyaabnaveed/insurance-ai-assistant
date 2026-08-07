from db_connection import get_connection


def run_query(query):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(query)

        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        return columns, rows

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()
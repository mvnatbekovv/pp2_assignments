import psycopg2
from config8 import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD


def connect():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=5432
        )
        print("Connected to PostgreSQL successfully!")
        conn.close()

    except Exception as e:
        print("Connection error:", e)


if __name__ == "__main__":
    connect()
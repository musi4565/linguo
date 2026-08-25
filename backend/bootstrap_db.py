import sys

import psycopg
from psycopg import sql

ADMIN = {"host": "localhost", "port": "5433", "user": "postgres", "password": "1202"}
APP_USER = "linguo"
APP_PASSWORD = "linguo_dev_2026"
DB_NAME = "linguo"


def run():
    with psycopg.connect(dbname="postgres", **ADMIN) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (APP_USER,))
            if cur.fetchone():
                print(f"Role '{APP_USER}' already exists")
            else:
                cur.execute(
                    sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                        sql.Identifier(APP_USER), sql.Literal(APP_PASSWORD)
                    )
                )
                print(f"Role '{APP_USER}' created")

            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
            if cur.fetchone():
                print(f"Database '{DB_NAME}' already exists")
            else:
                cur.execute(
                    sql.SQL(
                        "CREATE DATABASE {} OWNER {} ENCODING 'UTF8'"
                    ).format(
                        sql.Identifier(DB_NAME), sql.Identifier(APP_USER)
                    )
                )
                print(f"Database '{DB_NAME}' created")

    with psycopg.connect(
        dbname=DB_NAME,
        host=ADMIN["host"],
        port=ADMIN["port"],
        user=APP_USER,
        password=APP_PASSWORD,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            print("App user connection OK:", cur.fetchone()[0][:60])


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        print(f"FAILED: {exc}")
        sys.exit(1)

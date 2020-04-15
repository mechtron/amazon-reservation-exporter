import os

import psycopg2


DATABASE_HOSTNAME = os.environ.get("DATABASE_HOSTNAME")
DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
DATABASE_NAME = os.environ.get("DATABASE_NAME")


def setup_database():
    try:
        connection = psycopg2.connect(
            host=DATABASE_HOSTNAME.split(":")[0],
            port=DATABASE_HOSTNAME.split(":")[1],
            user=DATABASE_USERNAME,
            password=DATABASE_PASSWORD,
            database=DATABASE_NAME,
            connect_timeout=10,
        )
        cursor = connection.cursor()
        print(connection.get_dsn_parameters(), "\n")
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

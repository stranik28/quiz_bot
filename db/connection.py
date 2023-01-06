import psycopg2
from psycopg2 import Error
import os


async def connect():
    """ Connect to the PostgreSQL database server """
    try:
        # Connect to an existing database read from .env file
        connection = psycopg2.connect(user = os.environ.get("POSTGRES_USER"),
                                        password = os.environ.get("POSTGRES_PASSWORD"),
                                        host = os.environ.get("POSTGRES_HOST"),
                                        port = os.environ.get("POSTGRES_PORT"),
                                        database = os.environ.get("POSTGRES_DB"))
        
        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print ( connection.get_dsn_parameters(),"\n")

        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")
        return connection, cursor

    except (Exception, Error) as error :
        print ("Error while connecting to PostgreSQL", error)
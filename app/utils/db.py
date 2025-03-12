import os
import sqlite3

def create_connection():
    db_path = os.getenv("SQLITE_DB")

    if not db_path:
        raise ValueError("SQLITE_DB environment variable is not set!")
    
    pgdata_path = os.path.abspath(db_path)

    if not os.path.exists(pgdata_path):
        try:
            os.makedirs(pgdata_path)
        except OSError as e:
            raise RuntimeError(f"Failed to create directory {pgdata_path}: {e}")
    
    # Try to open the database file
    try:
        # If the database does not exist, create it and initialize it
        if not os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Define the path to the schema.sql file
            sql_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
             "..", "..", 'migrations', 'schema.sql') )
            
            # Check if the schema file exists before trying to open it
            if not os.path.exists(sql_file_path):
                raise FileNotFoundError(f"Schema file not found at {sql_file_path}")

            # Read and execute the SQL script to create the schema
            with open(sql_file_path, 'r') as file:
                sql_script = file.read()
                cursor.executescript(sql_script)
            
            # Commit the changes to the database
            conn.commit()
        else:
            # If the database exists, just return a connection
            conn = sqlite3.connect(db_path)
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Failed to open or create database file at {db_path}: {e}")
    
    return conn
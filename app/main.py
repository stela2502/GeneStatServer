from GeneStatServer import app 
import os


def get_database_file():
    # Ask the user for the database file path
    db_file = input("Please enter the path to your database file: ")
    
    # Check if the file exists
    if not os.path.isfile(db_file):
        print(f"Error: {db_file} does not exist.")
        exit(1)  # Exit if the file does not exist
    
    return db_file


if __name__ == "__main__":
	db_file = get_database_file()  # Get the database file from the user
	print(f"Using database: {db_file}")
    
    os.environ['SQLITE_DB'] = db_file

    app.run(debug=True)
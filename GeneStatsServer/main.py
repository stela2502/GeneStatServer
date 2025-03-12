from GeneStatsServer import app
import argparse
import os


def main():
    # Parse the command-line argument
    parser = argparse.ArgumentParser(description="Run the GeneStatsServer app.")
    parser.add_argument(
        '--db-file',
        type=str,
        required=True,
        help="Path to the database file"
    )

    # Parse the arguments and store them in `args`
    args = parser.parse_args()

    # Now you can access the database file path from the parsed arguments
    print(f"Using database: {args.db_file}")

    # Set the environment variable for the database file
    os.environ['SQLITE_DB'] = args.db_file

    # Start the Flask app
    app.run(debug=True)

if __name__ == "__main__":
    main()
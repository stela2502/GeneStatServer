from GeneStatsServer import app
import argparse
import os


def main():
    # Parse the command-line argument
    parser = argparse.ArgumentParser(description="Run the GeneStatsServer app.")
    parser.add_argument(
        '--db-file',
        type=str,
        required=False,
        help="Path to the database file"
    )

    # Parse the arguments and store them in `args`
    args = parser.parse_args()

    db_file = args.db_file or os.getenv('SQLITE_DB')

    os.environ['SQLITE_DB'] = db_file

    if not db_file:
        raise ValueError("usage: GeneStatsServer --db-file /path/to/your/database or set the SQLITE_DB environment variable")

    # Now you can access the database file path from the parsed arguments
    print(f"Using database: {db_file}")

    # Start the Flask app
    app.run(host='0.0.0.0', debug=False)

if __name__ == "__main__":
    main()
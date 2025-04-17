import argparse
import os
import sys
from GeneStatsServer import app  # Assuming your Flask app is defined in __init__.py or app.py

def main():
    parser = argparse.ArgumentParser(description="Run the GeneStatsServer Flask app.")
    parser.add_argument(
        "--db-file", 
        required=True, 
        help="Path to the SQLite database file"
    )

    args = parser.parse_args()
    db_path = os.path.abspath(args.db_file)

    if not os.path.exists(db_path):
        print(f"⚠️  Warning: The database file '{db_path}' does not exist yet. It will be created.")
        # Optionally create parent dir
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    os.environ['SQLITE_DB'] = db_path
    app.config['DEBUG'] = True
    print(f"✅ Running app with SQLITE_DB={db_path}")
    
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
import argparse
import os
import sys
from app import app  # Assuming your Flask app is in 'app.py'


def set_pgdata_for_testing():
    """Set SQLITE_DB for testing to use a local directory for testing."""
    pgdata = os.path.join(os.getcwd(), 'tests', 'data', 'output')  # Customize this path
    if not os.path.exists(pgdata):
        print(f"Creating SQLITE_DB directory at: {pgdata}")
        os.makedirs(pgdata)
    os.environ['SQLITE_DB'] = pgdata
    print(f"SQLITE_DB set to: {pgdata}")

def set_pgdata_for_deployment():
    """Set SQLITE_DB for deployment mode."""
    pgdata = os.getenv('SQLITE_DB')  # Should be set as an environment variable in production
    if not pgdata:
        print("Error: SQLITE_DB environment variable is not set!")
        sys.exit(1)
    print(f"SQLITE_DB set to: {pgdata}")

def run_debug_mode():
    """Run the Flask app in debug mode."""
    app.config['DEBUG'] = True
    set_pgdata_for_testing()  # Set SQLITE_DB to the testing folder
    app.run(debug=True, host='0.0.0.0', port=5000)

def run_deploy_mode():
    """Run the Flask app in deployment mode."""
    app.config['DEBUG'] = False
    set_pgdata_for_deployment()  # Set SQLITE_DB to the deployment folder
    app.run(debug=False, host='0.0.0.0', port=5000)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Run the Flask application in different modes.")
    
    parser.add_argument(
        'mode', choices=['debug', 'deploy'], 
        help="Mode to run the application in (either 'debug' or 'deploy')"
    )

    args = parser.parse_args()

    if args.mode == 'debug':
        run_debug_mode()
    elif args.mode == 'deploy':
        run_deploy_mode()
    else:
        print("Invalid mode. Choose 'debug' or 'deploy'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
        
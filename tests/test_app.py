from flask import Flask
import sqlite3
import pytest
import os
from app import create_app
from app.utils.db import create_connection  # Your db creation function
from io import BytesIO;
from urllib.parse import urlparse, parse_qs

# Define the test database path
TEST_DATABASE_PATH = './tests/data/'
os.environ['PGDATA'] = TEST_DATABASE_PATH

@pytest.fixture(scope='module')
def app():
    """Create and configure the Flask app for testing"""
    db_path = os.path.join(TEST_DATABASE_PATH,"genome.db")
    # Check if the database already exists; if it does, remove it before testing
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Removed existing test database at {db_path}")
        except OSError as e:
            raise RuntimeError(f"Failed to remove existing database at {db_path}: {e}")


    # Set the database file for testing (PGDATA logic is handled in your function)
    

    # Create the app instance
    app = create_app()

    # Initialize the database if needed
    create_connection()  # Call your function to initialize DB (create tables)

    yield app  # This is the Flask app instance for testing

    # Clean up after tests are done
    #os.remove(db_path)  # Remove the test database file

def test_database_tables_exist():
    """Test if the necessary database tables exist"""

    # Connect to the SQLite database (or use another method depending on your DB)
    conn = create_connection()
    cursor = conn.cursor()

    # Query to check if a specific table exists (adjust table names to your model)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # List of tables that should exist in the database
    expected_tables = ['experiments', 'info', 'genes', 'transcripts', 'bed']  # Replace with your actual table names

    # Extract table names from the query result
    table_names = [table[0] for table in tables]

    # Assert that all expected tables exist in the database
    for table in expected_tables:
        if table not in table_names:
            raise AssertionError(f"Table '{table}' is missing from the database! Tables found: {table_names}")

    # Clean up and close the connection
    conn.close()


@pytest.fixture(scope='module')
def client(app):
    """Returns a test client for making requests"""

    # Set the PGDATA variable if it's not already set
    os.environ['PGDATA'] = os.getenv('PGDATA', TEST_DATABASE_PATH)

    # Ensure the database directory is valid
    if not os.path.isdir(os.environ['PGDATA']):
        raise TestSetupError(f"Invalid PGDATA directory: {os.environ['PGDATA']}. Please check the path to the test database.")

    # Ensure the app is passed properly
    if not app:
        raise TestSetupError("Flask app is not properly initialized!")

    app.config['TESTING'] = True

    # Return the test client for making requests
    return app.test_client()



def test_file_upload_bed(client):
    """Test uploading a file through the web interface and checking the database and UI"""

    # Prepare the file to upload (a small test file)
    file_content = b"""chr6\t70703200\t70703250\t0\t275
chr6\t70703250\t70703300\t0\t609
"""
    data = {
        'file': (BytesIO(file_content), 'test_file.bed'),  # Simulate file upload
        'new_experiment_name': "Test case",
        'new_experiment_description': ""
    }

    # Upload the file via the web interface (POST request)
    response = client.post('/upload_bed', data=data)

    # Assert the upload was successful (check for HTTP 200 or other success status)
    assert response.status_code == 302
    if not response.headers["Location"] == "/":
        raise ValueError( f"Some error occured: {response.headers["Location"]}" )
    

    parsed_url = urlparse(response.headers["Location"])
    query_params = parse_qs(parsed_url.query)

    error_message = query_params.get('error_message', [''])[0]  # Default to empty string if not found
    if error_message:
        raise ValueError(f"File upload failed with error: {error_message}")

    # Verify the file was uploaded by checking the database
    conn = create_connection()
    cursor = conn.cursor()

    # Query to check if the file has been added to the 'files' table
    cursor.execute("SELECT * FROM bed;")
    results = cursor.fetchall()

    # Expected data to be inserted into the bed table
    expected_data = [
        (1,1,"chr6", 70703200, 70703250, 275, "0"),
        (2,1,"chr6", 70703250, 70703300, 609, "0"),
    ]

    assert len(results) ==  len(expected_data), "expected more data from the bed table!"
    # Assert that the results match the expected data
    for expected_row, actual_row in zip(expected_data, results):
        assert expected_row == actual_row, f"Mismatch: Expected {expected_row} but got {actual_row}"

    # Clean up the database connection
    conn.close()

    # Now let's test if the uploaded file appears in the web interface
    response = client.get('/')  # Assuming your app has a /files endpoint showing uploaded files

    # Check if the response includes the uploaded file's name (i.e., it should appear in the list)
    assert response.status_code == 200
    # Decode the response body as a string (HTML content)
    page_content = response.data.decode('utf-8')

    # Check if "Test case" is in the table of experiments
    assert "Test case" in page_content, f"'Test case' was not found in the experiment table.\n{page_content}"

    # Optionally, you could check the contents of the page more thoroughly
    # e.g., assert 'File uploaded successfully' not in response.data
    # or ensure other UI elements are displayed correctly.


def test_file_upload_gtf(client):
    """ upload a test gft file stream and check that everything panns out as expected"""

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("Delete from info;")
    cursor.execute("Delete from genes;") 
    cursor.execute("Delete from transcripts;")
    conn.close()

    # Prepare the file to upload (a small test file)
    file_content = b"""chr6\tHAVANA\tgene\t70703419\t70703950\t.\t+\t.\tgene_id "ENSMUSG00000076609.3"; gene_type "IG_C_gene"; gene_name "Igkc"; level 2; mgi_id "MGI:96495"; tag "overlapping_locus"; havana_gene "OTTMUSG00000053470.1";
"""
    data = {
        'gtffile': (BytesIO(file_content), 'test.gtf'),  # Simulate file upload
    }

    # Upload the file via the web interface (POST request)
    response = client.post('/upload_gtf', data=data)

    # Assert the upload was successful (check for HTTP 200 or other success status)
    if response.status_code == 200:
        page_content = response.data.decode('utf-8')
        assert "test.gtf" in page_content, f"'test.gtf' was not found in the experiment table.\n{page_content}"

    assert response.status_code == 302
    
    if not response.headers["Location"] == "/":
        raise ValueError( f"Some error occured: {response.headers["Location"]}" )

    parsed_url = urlparse(response.headers["Location"])
    query_params = parse_qs(parsed_url.query)

    error_message = query_params.get('error_message', [''])[0]  # Default to empty string if not found
    if error_message:
        raise ValueError(f"GTF File upload failed with error: {error_message}")

    # Verify the file was uploaded by checking the database
    conn = create_connection()
    cursor = conn.cursor()

    # Query to check if the file has been added to the 'files' table
    cursor.execute("SELECT * FROM info;")
    results = cursor.fetchall()

    # Expected data to be inserted into the bed table
    expected_data = [
        (1, 'gene info from test.gtf')
    ]

    assert len(results) ==  len(expected_data), "expected more data from the bed table!"
    # Assert that the results match the expected data
    for expected_row, actual_row in zip(expected_data, results):
        assert expected_row == actual_row, f"Mismatch: Expected {expected_row} but got {actual_row}"

    # Clean up the database connection
    conn.close()

    # Now let's test if the uploaded file appears in the web interface
    response = client.get('/')  # Assuming your app has a /files endpoint showing uploaded files

    # Check if the response includes the uploaded file's name (i.e., it should appear in the list)
    assert response.status_code == 200
    # Decode the response body as a string (HTML content)
    page_content = response.data.decode('utf-8')

    # Check if "Test case" is in the table of experiments
    assert "test.gtf" in page_content, f"'test.gtf' was not found in the experiment table.\n{page_content}"

    # Optionally, you could check the contents of the page more thoroughly
    # e.g., assert 'File uploaded successfully' not in response.data
    # or ensure other UI elements are displayed correctly.


def test_file_download_genes(client):
    data = {
        "distance": 100000
    }
    response = client.post('/get_genes', data=data)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    if b"No results found for the given distance." in response.data:
        raise ValueError("Crap this search did not return any entries?!")

    # Check if the Content-Type header is 'text/csv' for CSV files
    if not response.headers['Content-Type'] == 'text/csv; charset=utf-8':
        raise ValueError(f"the content type is wrong ({response.headers['Content-Type']}) - we got {response.data}")

    # Check if the Content-Disposition header includes 'attachment' and the filename
    assert 'attachment' in response.headers['Content-Disposition']
    assert 'filename=genes_near_peaks.csv' in response.headers['Content-Disposition']

    tsv_file = response.data.decode('utf-8')
    assert tsv_file == "Gene ID\tGene Name\tChromosome\tGene Start\tGene Stop\tBED ID\tExperiment ID\tBED Chromosome\tBED Start\tBED Stop\tPeak Score\tFeature Name\tDistance (bp)\r\n1\tIgkc\tchr6\t70703419\t70703950\t1\tTest case\tchr6\t70703200\t70703250\t275.0\t0\t169\r\n1\tIgkc\tchr6\t70703419\t70703950\t2\tTest case\tchr6\t70703250\t70703300\t609.0\t0\t119\r\n"

from flask import Blueprint, request, redirect, url_for, jsonify, Flask
from werkzeug.utils import secure_filename
from .utils.file_processing import load_gtf_to_postgres
from .utils.db import create_connection


upload_gtf_bp = Blueprint('upload_gtf', __name__)

# Route to handle the download of the CSV file
@upload_gtf_bp.route("/upload_gtf", methods=["POST"])
def upload_gtf():
    try:
        # Get the distance parameter from the query string
        gtf_file = request.files.get("gtffile")

        if not gtf_file:
            return f"Please provide a valid file - not '{gtf_file}'"

        if not allowed_file(gtf_file.filename):
            return jsonify({"error": "Invalid file type. Please upload a .gtf file."}), 400

        #raise RuntimeError( f"What have I gotten here: '{gtf_file.filename}'??")
        # Call the function to get genes near peaks
        load_gtf_to_postgres(gtf_file)

        return redirect(url_for('index.index'))
    except Exception as e:
        return f"An error occurred: {e}"


# Helper function to validate file extensions (optional)
def allowed_file(filename):
    return filename.endswith('.gtf')
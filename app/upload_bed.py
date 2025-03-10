from flask import Blueprint, request, redirect, url_for, jsonify, Flask
from werkzeug.utils import secure_filename
from .utils.file_processing import process_bed_file_in_memory
from .utils.db import create_connection

# Define the blueprint
upload_bed_bp = Blueprint('upload_bed', __name__)

@upload_bed_bp.route('/upload_bed', methods=['POST'])
def upload_bed():
    experiment_id = request.form.get("experiment_id")
    new_experiment_name = request.form.get("new_experiment_name")
    new_experiment_description = request.form.get("new_experiment_description")

    if new_experiment_name:  # Insert new experiment into DB
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO experiments (experiment_name, description) VALUES (?, ?);", 
                    (new_experiment_name, new_experiment_description))
        experiment_id = cur.lastrowid
        conn.commit()
        cur.close()

    if not experiment_id:
        return redirect(url_for('index.index', error_message="No experiment ID selected"))

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        try:
            result = process_bed_file_in_memory(file, experiment_id)
        except Exception as e:
            return redirect(url_for('index.index', error_message=f"Failed to process the BED file: {e}"))
        
        if result:
            return redirect(url_for('index.index'))
        else:
            error_message = "Failed to process the BED file"
            return redirect(url_for('index.index', error_message=error_message))
    else:
        return jsonify({"error": "Invalid file format"}), 400


# Helper function to validate file extensions (optional)
def allowed_file(filename):
    return filename.endswith('.bed')
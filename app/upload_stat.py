from .utils.file_processing import process_stat_file_in_memory
from flask import Blueprint, render_template, request, Flask, Response, render_template, redirect, url_for, jsonify
from .utils.db import create_connection
from .utils.searches import get_stats_table
import io
import csv
from werkzeug.utils import secure_filename

upload_stat_bp = Blueprint('/stats', __name__)

@upload_stat_bp.route('/stats/', methods=['GET'])
def index():
    # Fetch annotation names from the database
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, annotation_name FROM annotation")
    annotations = cur.fetchall()
    conn.close()

    # On GET, render the form with annotation options
    return render_template('upload_stat.html', annotations=annotations)


@upload_stat_bp.route('/stats/upload', methods=['POST'])
def upload_stat():
    # Get all form data
    new_annotation_name = request.form.get("new_annotation_name")
    new_annotation_description = request.form.get("new_annotation_description")
    
    # Columns and separator values
    separator = request.form.get("separator")
    gene_column = request.form.get("gene_column")
    stats_column = request.form.get("stats_column")
    corrected_stats_col = request.form.get("corected_stats_col")
    fold_change_col = request.form.get("fold_change_col")
    
    # Check if we have a new annotation to insert into the database
    if new_annotation_name:  # Insert new annotation into DB
        conn = create_connection()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO annotation (annotation_name, description) VALUES (?, ?);", 
                        (new_annotation_name, new_annotation_description))
            annotation_id = cur.lastrowid
            conn.commit()
            cur.close()
        except Exception as e:
            if str(e).startswith("UNIQUE"):
                return render_template('upload_stat.html', 
                    form_error="This annotation name has already been used!",
                    new_annotation_description=new_annotation_description,  # Populate description
                    separator=separator,  # Populate separator
                    gene_column=gene_column,  # Populate gene column
                    stats_column=stats_column,  # Populate stats column
                    corrected_stats_col=corrected_stats_col,  # Populate corrected stats column
                    fold_change_col=fold_change_col  # Populate fold change column
                )
            raise ValueError(f"Error: {e}")
        finally:
            conn.close()
    
    if not annotation_id:
        return render_template('upload_stat.html', error_message="No annotation ID selected")
    
    if 'file' not in request.files:
        return render_template('upload_stat.html', error_message="No file part")
    
    file = request.files['file']
    if file.filename == '':
        return render_template('upload_stat.html', error_message="No selected file")
    
    if file:
        filename = secure_filename(file.filename)
        try:
            result = process_stat_file_in_memory(
                file, 
                annotation_id, 
                separator,
                gene_column,
                stats_column,
                corrected_stats_col,
                fold_change_col
            )
        except Exception as e:
            return render_template(
                'upload_stat.html', 
                form_error=f"Failed to process the Stats file: {e}",
                new_annotation_description=new_annotation_description,  # Populate description
                separator=separator,  # Populate separator
                gene_column=gene_column,  # Populate gene column
                stats_column=stats_column,  # Populate stats column
                corrected_stats_col=corrected_stats_col,  # Populate corrected stats column
                fold_change_col=fold_change_col  # Populate fold change column
            )
        
        if result:
            return redirect(url_for('/stats.index'))  # Redirect to avoid resubmission
        else:
            return render_template('upload_stat.html', error_message="Failed to process the stats table")
    else:
        return render_template('upload_stat.html', error_message="Invalid file format")


@upload_stat_bp.route('/stats/get', methods=['POST'])
def get_stats():
    # Extract query parameters from the URL
    distance = request.form.get('distance', type=int)  # Assuming max distance is passed as a query parameter
    annotation_id = request.form.get('annotation_id', type=int)  # Selected annotation ID
    p_val_threshold = request.form.get('p_val_threshold', type=float)  # p-value threshold
    
    if distance is None or annotation_id is None or p_val_threshold is None:
        return jsonify({"error": f"Missing required parameters: annotation_id {annotation_id} distance {distance} p_val_threshold {p_val_threshold}"}), 400
    
    # Call the function to get the data
    results = get_stats_table(distance, annotation_id, p_val_threshold)
    
    # Prepare the CSV output
    output = io.StringIO()
    writer = csv.writer(output, delimiter="\t" )
    #    gene_id INT,    gene_name TEXT,    chromosome TEXT,    gene_start INT,    gene_stop INT,    bed_id INT,    experiment_id INT,    bed_chromosome TEXT,    bed_start INT,    bed_stop INT,    peak_score FLOAT,    feature_name TEXT,    distance INT            writer.writerow(["Gene ID", "Gene Name", "Peak ID", "Distance (bp)"])  
    # Header row based on the table structure
    writer.writerow([      
        "Gene ID", "Gene Name", "Chromosome", "Gene Start", "Gene Stop", "BED ID", 
        "Experiment Name", "BED Chromosome", "BED Start", "BED Stop", "Peak Score", 
        "Feature Name", "Distance (bp) ", "Stats Name", "P Value", "Corrected P Vaule",
        "Stats Fold Change"
    ])  # header row
    # Write the data rows
    writer.writerows(results)

    output.seek(0)

    # Create a response to trigger a download
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=genes_near_peaks_with_stats.csv"},
    )

    if stats_data is None:
        return jsonify({"error": "Failed to retrieve data"}), 500
    
    # Optionally, render a template or return JSON
    return render_template('stats_results.html', stats_data=stats_data)
    # Or return as JSON
    # return jsonify(stats_data)


ALLOWED_EXTENSIONS = ('.txt', '.csv', '.tsv')

# Helper function to validate file extensions (optional)
def allowed_file(filename):
    return filename.lower().endswith(ALLOWED_EXTENSIONS)
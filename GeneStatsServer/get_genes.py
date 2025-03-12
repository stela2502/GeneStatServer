from flask import Blueprint, render_template, request, Flask, Response
from .utils.db import create_connection
from .utils.searches import get_genes_near_peaks
import io
import csv

# Define the blueprint
get_genes_bp = Blueprint('get_genes', __name__)
# Define the route inside the blueprint

# Route to handle the download of the CSV file
@get_genes_bp.route("/get_genes", methods=["POST"])
def get_genes():
    try:
        # Get the distance parameter from the query string
        distance = request.form.get("distance", type=int)

        if not distance:
            return f"Please provide a valid distance parameter - not '{distance}'"

        # Call the function to get genes near peaks
        results = get_genes_near_peaks(distance)

        if results:
            # Prepare the CSV output
            output = io.StringIO()
            writer = csv.writer(output, delimiter="\t" )
            #    gene_id INT,    gene_name TEXT,    chromosome TEXT,    gene_start INT,    gene_stop INT,    bed_id INT,    experiment_id INT,    bed_chromosome TEXT,    bed_start INT,    bed_stop INT,    peak_score FLOAT,    feature_name TEXT,    distance INT            writer.writerow(["Gene ID", "Gene Name", "Peak ID", "Distance (bp)"])  
            # Header row based on the table structure
            writer.writerow([
                "Gene ID", "Gene Name", "Chromosome", "Gene Start", "Gene Stop", "BED ID", 
                "Experiment ID", "BED Chromosome", "BED Start", "BED Stop", "Peak Score", 
                "Feature Name", "Distance (bp)"
            ])  # header row
            # Write the data rows
            writer.writerows(results)

            output.seek(0)

            # Create a response to trigger a download
            return Response(
                output,
                mimetype="text/csv",
                headers={"Content-Disposition": "attachment;filename=genes_near_peaks.csv"},
            )
        else:
            return "No results found for the given distance."

    except Exception as e:
        return f"An error occurred: {e}"
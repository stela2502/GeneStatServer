from flask import Blueprint, render_template, request, Flask
from .utils.db import create_connection

# Define the blueprint
index_bp = Blueprint('index', __name__)
# Define the route inside the blueprint
@index_bp.route('/')

def index():
    conn = create_connection()
    if conn:
        cur = conn.cursor()
        # Fetch data from database
        cur.execute("SELECT info FROM info LIMIT 1;")
        genome_version_row = cur.fetchone()
        genome_version = genome_version_row[0] if genome_version_row else "Nothing"

        cur.execute("SELECT count(*) FROM genes;")
        gene_counts = cur.fetchone()[0]
        
        cur.execute("SELECT count(*) FROM transcripts;")
        transcript_counts = cur.fetchone()[0]

        error_message = ""
        if genome_version == "Nothing":
            error_message ="Please upload your GTF file."

        # Fetch number of experiments
        cur.execute("SELECT COUNT(*) FROM experiments;")
        num_experiments = cur.fetchone()[0]

        # Fetch peaks per experiment
        cur.execute("SELECT experiment_id, COUNT(experiment_id) FROM bed GROUP BY experiment_id;")
        peaks_per_experiment = cur.fetchall()

        # Fetch experiments
        cur.execute("SELECT id, experiment_name FROM experiments;")
        experiments = cur.fetchall()
        experiment_dict = {exp_id: exp_name for exp_id, exp_name in experiments}

        cur.close()
        conn.close()

        peaks_info = {}
        if not peaks_per_experiment:
            error_message += "Please upload your BED data"

        for exp_id, peak_count in peaks_per_experiment:
            exp_name = experiment_dict.get(exp_id, "Unknown Experiment")
            peaks_info[exp_name] = peak_count 

        error_message += request.args.get('error_message', "")

        return render_template('index.html', genome_version=genome_version, 
                               num_experiments=num_experiments, gene_counts=gene_counts, 
                               transcript_counts=transcript_counts, peaks_info=peaks_info, 
                               experiments=experiments, error_message=error_message)
    else:
        return "Database connection error!", 500
        
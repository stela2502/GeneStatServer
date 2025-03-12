from .db import create_connection  # Your db creation function
import os

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'bed'}

def find_column( column_name, columns):
    if column_name and isinstance(column_name, str):
        try:
            # Check if column_name can be converted to an integer (which would mean it's not a real column name)
            return int(column_name)
        except ValueError:
            # Only proceed if it's truly a string (not an integer-like string)
            try:
                index = columns.index(column_name)  # Find the index
                return index
            except ValueError:
                raise ValueError(f"Column '{column_name}' not found in header: {columns}")

def process_stat_file_in_memory(file, annotation_id, sep, gene_column, stats_column, corected_stats_col, fold_change_col ):
    conn = create_connection()
    if conn:
        cur = conn.cursor()
        lines = file.stream
        stats_data = []
        first = True
        for raw_line in lines:
            line = raw_line.decode("utf-8")
            parts = line.strip().split(sep)

            if first:
                first = False
                stats_column = find_column(stats_column, parts)
                gene_column = find_column(gene_column, parts)
                corected_stats_col = find_column(corected_stats_col, parts)
                fold_change_col = find_column(fold_change_col, parts)

            if len(parts) >= 3:
                gene  = parts[gene_column]
                p_val = parts[stats_column]
                p_cor = parts[corected_stats_col] if parts[corected_stats_col] else None
                foldc = parts[fold_change_col] if parts[fold_change_col] else None
                stats_data.append([annotation_id, p_val, p_cor, foldc, gene ])
        if len(stats_data) == 0:
            raise ValueError( f"I got no data from the table - are these settings correct: sep {sep}, "
                f"stats_column {stats_column}, gene_column {gene_column}, corected_stats_col {corected_stats_col},"
                f" fold_change_col {fold_change_col}"
            )
        try:
            cur.executemany(
                """
                INSERT INTO stats (gene_id, annotation_id, p_val, p_corr, foldc)
                SELECT id, ?, ?, ?, ?
                FROM genes WHERE gene_name = ?
                """,
                stats_data
            )
            conn.commit()
            conn.close()
        except Exception as e:
            raise ValueError( f"I got a database error: {e}")
        return True
    return False


def process_bed_file_in_memory(file, experiment_id):
    conn = create_connection()
    if conn:
        cur = conn.cursor()
        lines = file.stream
        bed_data = []

        for raw_line in lines:
            line = raw_line.decode("utf-8")
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                chromosome = parts[0]
                start = int(parts[1])
                stop = int(parts[2])
                peak_score = float(parts[4]) if len(parts) > 4 else 0.0
                feature_name = parts[3] if len(parts) > 3 else "-"
                bed_data.append([experiment_id, chromosome, start, stop, peak_score, feature_name])
        
        try:
            cur.executemany(
                "INSERT INTO bed (experiment_id, chromosome, start, stop, peak_score, feature_name) VALUES (?, ?, ?, ?, ?, ?)", 
                bed_data
            )
            conn.commit()
            conn.close()
        except Exception as e:
            raise ValueError( f"I got a database error: {e}")
        return True
    return False


def load_gtf_to_postgres(gtf_file):
    """Loads a GTF file into a PostgreSQL database using a temporary SQL dump for efficiency."""

    conn = create_connection()
    cur = conn.cursor()

    # Check if GTF has already been uploaded
    cur.execute("SELECT info FROM info LIMIT 1;")
    genome_version = cur.fetchone()[0] if cur.rowcount > 0 else "Nothing"

    if genome_version != "Nothing":
        return "Error: GTF has already been uploaded"

    cur.execute(f"INSERT INTO info (info) VALUES ('gene info from {gtf_file.filename}');")
    conn.commit()

    pgdata_path = os.getenv("SQLITE_DB")
    if pgdata_path:
        print(f"SQLITE_DB is set to: {pgdata_path}")
    else:
        print("SQLITE_DB is not set.")

    temp_sql_path = os.path.join(pgdata_path, "temp_import.sql")
    gene_id_counter = 1  # Start counting genes from 1


    # Buffers for bulk insertion
    gene_entries = []
    transcript_entries = []

    for raw_line in gtf_file.stream:
        line = raw_line.decode("utf-8").strip()
        if line.startswith("#"):
            continue
        
        parts = line.split("\t")
        if len(parts) < 9:
            continue
        
        feature_type = parts[2]
        chromosome = parts[0]
        start = int(parts[3])
        stop = int(parts[4])
        strand = parts[6]
        attributes = parts[8]

        if feature_type == "gene":
            gene_name = extract_attribute(attributes, "gene_name")
            if gene_name:
                if strand == "-":
                    start, stop = stop, start  # Adjust for reverse strand
                gene_entries.append( (gene_name,chromosome,start,stop ))
                gene_id_counter += 1  # Increment for the next gene

        elif feature_type == "transcript":
            transcript_name = extract_attribute(attributes, "transcript_id")
            if transcript_name:
                if strand == "-":
                    start, stop = stop, start  # Adjust for reverse strand
                transcript_entries.append((gene_id_counter-1 ,transcript_name , start, stop ) )
    # just for debug!           
    f_name = os.path.join(pgdata_path, "db_gtf_contents_file.sql" )


    # Write COPY commands to the SQL file
    if gene_entries:
        cur.executemany(
            "INSERT INTO genes (gene_name, chromosome, start, stop) VALUES (?, ?, ?, ?)", 
            gene_entries)

    if transcript_entries:
        cur.executemany(
            "INSERT INTO transcripts (gene_id, transcript_name, start, stop)  VALUES (?, ?, ?, ?)", 
            transcript_entries)

    cur.execute ( "CREATE INDEX IF NOT EXISTS idx_genes_chromosome_start ON genes(chromosome, start)")
    cur.execute ( "CREATE INDEX IF NOT EXISTS idx_transcripts_gene_id ON transcripts(gene_id)")

    conn.commit()
    conn.close()
        
    return "Data successfully loaded and indexes created"


def extract_attribute(attributes, key):
    """Extracts values from a GTF attributes column (e.g., gene_name or transcript_id)."""
    for attr in attributes.split(";"):
        attr = attr.strip()
        if attr.startswith(key):
            parts = attr.split('"')
            if len(parts) > 1:
                return parts[1]
    return None
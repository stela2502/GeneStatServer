from .db import create_connection

def get_genes_near_peaks(distance):
    conn = create_connection()
    if conn:
        cur = conn.cursor()
        try:
            query = """
                SELECT g.id AS gene_id, g.gene_name, g.chromosome, g.start AS gene_start, 
                    g.stop AS gene_stop, b.id AS bed_id, e.experiment_name, 
                    b.chromosome AS bed_chromosome, b.start AS bed_start, b.stop AS bed_stop, 
                    b.peak_score, b.feature_name, 
                    CASE 
                        WHEN g.start > b.stop THEN g.start - b.stop 
                        WHEN g.stop < b.start THEN b.start - g.stop 
                        ELSE 0 
                    END AS distance
                FROM genes g
                JOIN bed b ON g.chromosome = b.chromosome
                JOIN experiments e ON b.experiment_id = e.id
                WHERE (g.start - ? <= b.stop AND g.stop + ? >= b.start)
                ORDER BY g.chromosome, g.start;
            """
            cur.execute(query, (distance, distance))
            results = cur.fetchall()
            cur.close()
            conn.close()
            return results
        except Exception as e:
            return None
    return None


def get_stats_table(distance, annotation_id, p_val_threshold):
    # Perform the query using the selected annotation and filter values
    conn = create_connection()
    if conn:
        cur = conn.cursor()
        try:
            query = """
            SELECT 
                g.id AS gene_id, 
                g.gene_name, 
                g.chromosome, 
                g.start AS gene_start, 
                g.stop AS gene_stop, 
                b.id AS bed_id, 
                e.experiment_name, 
                b.chromosome AS bed_chromosome, 
                b.start AS bed_start, 
                b.stop AS bed_stop, 
                b.peak_score, 
                b.feature_name, 
                CASE 
                    WHEN g.start > b.stop THEN g.start - b.stop 
                    WHEN g.stop < b.start THEN b.start - g.stop 
                    ELSE 0 
                END AS distance,
                a.annotation_name,  -- Add annotation_name here
                s.p_val, 
                s.p_corr, 
                s.foldc
            FROM genes g
            JOIN bed b ON g.chromosome = b.chromosome
            JOIN experiments e ON b.experiment_id = e.id
            JOIN stats s ON s.gene_id = g.id
            JOIN annotation a ON a.id = s.annotation_id  -- Join with annotations table
            WHERE (g.start - ? <= b.stop AND g.stop + ? >= b.start) 
                AND s.p_val < ?
                AND s.annotation_id = ?
            ORDER BY g.chromosome, g.start;
            """

            # Execute the query with the provided parameters
            cur.execute(query, (distance, distance, p_val_threshold, annotation_id))
            results = cur.fetchall()
            # Close connection
            conn.close()
            # Return the results
            return results
        except Exception as e:
            # Handle any errors and return None
            raise ValueError(f"Error: {e}")
    raise ValueError("I could not connect to the database!")
    # Return None if connection was not successful
    return None
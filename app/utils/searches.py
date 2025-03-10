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
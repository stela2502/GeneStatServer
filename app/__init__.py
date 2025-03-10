from flask import Flask
from .routes import index_bp
from .upload_gtf import upload_gtf_bp
from .upload_bed import upload_bed_bp
from .get_genes import get_genes_bp

def create_app():
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(index_bp)
    app.register_blueprint(upload_bed_bp)
    app.register_blueprint(upload_gtf_bp)
    app.register_blueprint(get_genes_bp)

    return app
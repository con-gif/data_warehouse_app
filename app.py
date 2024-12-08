# app.py
from flask import Flask, render_template
from blueprints.import_bp import import_bp
from blueprints.compare_bp import compare_bp
from blueprints.export_bp import export_bp
from blueprints.tag_bp import tag_bp
from blueprints.format_bp import format_bp
from blueprints.screening_bp import screening_bp
from blueprints.clean_validate_bp import clean_validate_bp
from blueprints.deduplicate_bp import deduplicate_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(import_bp)
app.register_blueprint(compare_bp, url_prefix='/comparison')
app.register_blueprint(export_bp)
app.register_blueprint(tag_bp)
app.register_blueprint(format_bp)
app.register_blueprint(screening_bp, url_prefix='/screening')
app.register_blueprint(clean_validate_bp, url_prefix='/clean-validate')  # Use '/clean-validate'
app.register_blueprint(deduplicate_bp)

# Home page route to render index.html
@app.route('/')
def home():
    return render_template('index.html')

# Health check endpoint to ensure server is running
@app.route('/health')
def health():
    return {"status": "running"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import tempfile
from werkzeug.utils import secure_filename

from modules import (
    read_fasta,
    extract_species,
    align_file,
    build_neighbor_joining_tree,
)

app = Flask(__name__)
CORS(app)

# Max upload size
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

ALLOWED_EXTENSIONS = {'fasta', 'fa', 'fna', 'ffn', 'faa', 'txt'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle FASTA upload and return a phylogenetic tree as Newick."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload a FASTA file'}), 400

    original_name = secure_filename(file.filename)

    with tempfile.TemporaryDirectory(prefix='treealign_') as tmpdir:
        upload_path = os.path.join(tmpdir, original_name)
        file.save(upload_path)

        try:
            # 1. Parse
            records = read_fasta(upload_path)
            if len(records) < 3:
                return jsonify({
                    'error': f'FASTA file has only {len(records)} sequence(s). '
                             'At least 3 sequences are required to build a tree.'
                }), 400

            # 2. Align (writes aligned FASTA into tmpdir)
            aligned_path = align_file(upload_path, output_dir=tmpdir)
            if aligned_path is None:
                return jsonify({
                    'error': 'Alignment failed. Is MUSCLE installed and on PATH?'
                }), 500

            # 3. Build NJ tree (writes Newick into tmpdir)
            tree, tree_file = build_neighbor_joining_tree(
                aligned_path, output_dir=tmpdir
            )

            # 4. Read Newick back while tmpdir still exists
            with open(tree_file, 'r') as f:
                newick = f.read()

            # 5. FASTA ID 
            id_to_species = {rec.id: extract_species(rec) for rec in records}

            return jsonify({
                'filename': original_name,
                'num_sequences': len(records),
                'newick': newick,
                'id_to_species': id_to_species,
            })

        except Exception as e:
            return jsonify({'error': f'Pipeline failed: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
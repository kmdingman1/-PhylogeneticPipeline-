from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import io
import tempfile
from werkzeug.utils import secure_filename
from Bio import Phylo

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


def tree_to_ascii(tree):
    """Capture Bio.Phylo.draw_ascii output as a string."""
    buf = io.StringIO()
    Phylo.draw_ascii(tree, file=buf)
    return buf.getvalue()


def rename_terminals_to_species(tree, records):
    """Replace cryptic leaf IDs with readable species names."""
    id_to_species = {rec.id: extract_species(rec) for rec in records}
    for leaf in tree.get_terminals():
        if leaf.name in id_to_species:
            leaf.name = id_to_species[leaf.name]
    return tree


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle FASTA upload and return an ASCII phylogenetic tree."""
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

            # 2. Align
            aligned_path = align_file(upload_path, output_dir=tmpdir)
            if aligned_path is None:
                return jsonify({
                    'error': 'Alignment failed. Is MUSCLE installed and on PATH?'
                }), 500

            # 3. Build NJ tree
            tree, tree_file = build_neighbor_joining_tree(
                aligned_path, output_dir=tmpdir
            )

            # 4. Prettier leaf labels
            rename_terminals_to_species(tree, records)

            # 5. ASCII for now
            ascii_tree = tree_to_ascii(tree)
            with open(tree_file, 'r') as f:
                newick = f.read()

            species_list = [extract_species(r) for r in records]

            return jsonify({
                'filename': original_name,
                'num_sequences': len(records),
                'species': species_list,
                'ascii_tree': ascii_tree,
                'newick': newick,
            })

        except Exception as e:
            return jsonify({'error': f'Pipeline failed: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
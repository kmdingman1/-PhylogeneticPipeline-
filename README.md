# TreeAlign

**An integrated phylogenetic analysis pipeline in your browser.**

Upload a FASTA file, and TreeAlign will align the sequences with MUSCLE, compute a pairwise distance matrix, build a Neighbor-Joining tree, and render it as an interactive visualization — all in a single click.

---

## Table of Contents

- [What It Does](#what-it-does)
- [Screenshots](#screenshots)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Supported File Formats](#supported-file-formats)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Dependencies](#dependencies)

---

## What It Does

TreeAlign collapses a typical phylogenetics workflow into a single web interaction:

1. You upload a FASTA file (works best with protein sequences or mitochondrial DNA sequences).
2. TreeAlign aligns the sequences using **MUSCLE v5**.
3. It computes a pairwise identity distance matrix with Biopython.
4. It constructs an unrooted **Neighbor-Joining** tree.
5. Your browser renders the tree using D3.js — zoom, pan, and hover over leaves to see species names.

No command line, no intermediate files to manage, no desktop viewer — just upload and generate.

---

## Screenshots

*<img width="1047" height="551" alt="image" src="https://github.com/user-attachments/assets/5e49765e-1811-42ff-a7fd-3b797b9d79c0" />*
*<img width="1158" height="775" alt="image" src="https://github.com/user-attachments/assets/5d8ca6a3-0c5d-442b-8277-d0261e2eef33" />*



---

## Quick Start

If you already have Python 3.9+ and MUSCLE installed:

```bash
git clone https://github.com/kmdingman1/-PhylogeneticPipeline-.git
cd -PhylogeneticPipeline-
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:5000** in your browser.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/kmdingman1/-PhylogeneticPipeline-.git
cd -PhylogeneticPipeline-
```

### 2. Install Python dependencies

TreeAlign requires **Python 3.9 or higher**.

```bash
pip install -r requirements.txt
```

Installs Flask, Flask-CORS, and Biopython.

### 3. Install MUSCLE

TreeAlign uses **MUSCLE v5** for multiple sequence alignment.

**Windows**
1. Download `muscle-win64.v5.3` from the [MUSCLE releases page](https://github.com/rcedgar/muscle/releases/tag/v5.3).
2. Rename it to `muscle.exe`.
3. Place it either in the project root or somewhere on your `PATH`.

**macOS**
```bash
brew install muscle
```

**Linux**
```bash
sudo apt-get install muscle
```

### 4. Verify MUSCLE is available

```bash
muscle -version
```

### 5. Run TreeAlign

```bash
python app.py
```

You should see:

```
 * Running on http://127.0.0.1:5000
```

Open URL in your browser.

---

## Usage

### From the browser

1. Click **Upload FASTA File**.
2. Choose a `.fasta` (or `.fa`, `.fna`, `.ffn`, `.faa`, `.txt`) file containing **at least 3 sequences**.
3. Wait a few seconds while the pipeline runs.
4. Interact with the resulting tree:
   - **Scroll** to zoom
   - **Click and drag** to pan
   - **Hover over a leaf** to see its full species name


### Sample data

The `data/test_FASTA/` folder includes a few example files you can try:

- `HBBprotein.fasta` — mammalian hemoglobin beta-chain proteins
- `CYCSproteins.fasta` — vertebrate cytochrome-c proteins
- `CYTBmitochondrial.fasta` — primate Cytochrome b mitochondrial gene
- `COX1mitochondrial.fasta` — mammalian Cytochrome c oxidase mitochondrial gene
---

## Supported File Formats

| Extension | Type                       |
| --------- | -------------------------- |
| `.fasta`  | Standard FASTA             |
| `.fa`     | Standard FASTA (short)     |
| `.fna`    | Nucleotide FASTA           |
| `.ffn`    | Coding-region FASTA        |
| `.faa`    | Amino-acid (protein) FASTA |
| `.txt`    | Plain text (FASTA-formatted) |

**Limits**
- Minimum: **3 sequences**
- Maximum file size: **50 MB**

Species names are automatically extracted from several common header styles:

- NCBI bracket format: `>seq_001 description [Homo sapiens]`
- UniProt format: `>sp|P68871|HBB_HUMAN ... OS=Homo sapiens GN=HBB ...`
- RefSeq-style: `>NC_018753.1 Nomascus gabriellae mitochondrion ...`

If no species name can be extracted, the sequence ID is used as a fallback.

---

## Project Structure

```
PhylogeneticPipeline/
├── app.py                     # Flask application entry point
├── requirements.txt           # Python dependencies
├── muscle.exe                 # MUSCLE for MSA
│
├── modules/                   # Core pipeline
│   ├── __init__.py
│   ├── parser.py              # FASTA parsing & species extraction
│   ├── aligner.py             # MUSCLE wrapper
│   └── tree_builder.py        # Distance matrix + Neighbor-Joining
│
├── templates/
│   └── index.html             # Main UI
│
├── static/
│   ├── css/style.css
│   └── js/treeVisualization.js  # D3.js tree renderer
│
└── data/
    ├── test_FASTA/            # Example input files
    ├── aligned_FASTA/         # (dev-time output; runtime uses tempdir)
    └── phylotree/             # (dev-time output; runtime uses tempdir)
```

---

## Troubleshooting

**"MUSCLE not found" / "Alignment failed"**
MUSCLE isn't on your `PATH`. Either install it properly, or place `muscle.exe` (Windows) in the project root.

**"FASTA file has only N sequence(s). At least 3 sequences are required."**
Neighbor-Joining needs a minimum of three taxa to produce a tree. Add more sequences to your file.

**"Invalid file type. Please upload a FASTA file"**
The file extension isn't in the allowed list. Rename to `.fasta` or convert your file.

**Upload stalls or returns a 413 error**
Your file is larger than 50 MB. Split it into smaller files or increase `MAX_CONTENT_LENGTH` in `app.py`.

**"Pipeline failed" with no clear error**
Check the Flask terminal output. The full Python traceback is printed there, which will tell you which stage failed.

---


## Dependencies

**Python packages** (see `requirements.txt`):
- [Flask](https://flask.palletsprojects.com/) 2.3.3 — web framework
- [Flask-CORS](https://flask-cors.readthedocs.io/) 4.0.0 — CORS support
- [Biopython](https://biopython.org/) 1.83 — sequence I/O, distance calculation, tree construction

**External tools**:
- [MUSCLE](https://github.com/rcedgar/muscle) v5.x — multiple sequence alignment

**Browser-side**:
- [D3.js](https://d3js.org/) v7 — interactive tree visualization

---

Built for COSC 880, Spring 2026.

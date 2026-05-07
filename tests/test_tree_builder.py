# Tests for the tree builder module.
#
# aligned_3seq.fasta has 3 hand-crafted sequences:
#   seq_A:  A C G T A C G T
#   seq_B:  A C G T A C G T   (identical to A)
#   seq_C:  A C G A A C G A   (matches A and B at 6 of 8 positions)
#
# So d(A,B) = 0.00 and d(A,C) = d(B,C) = 0.25.

from pathlib import Path

import pytest
from Bio import Phylo

from modules.tree_builder import (
    build_neighbor_joining_tree,
    calculate_distance_matrix,
)


def test_distance_matrix_known_values(fixtures_dir):
    m = calculate_distance_matrix(str(fixtures_dir / "aligned_3seq.fasta"))
    assert m["seq_A", "seq_B"] == pytest.approx(0.00, abs=1e-9)
    assert m["seq_A", "seq_C"] == pytest.approx(0.25, abs=1e-9)
    assert m["seq_B", "seq_C"] == pytest.approx(0.25, abs=1e-9)


def test_tree_has_correct_number_of_leaves(fixtures_dir, workdir):
    tree, _ = build_neighbor_joining_tree(
        str(fixtures_dir / "aligned_3seq.fasta"),
        output_dir=str(workdir),
    )
    assert tree.count_terminals() == 3


def test_tree_writes_newick_file(fixtures_dir, workdir):
    _, tree_file = build_neighbor_joining_tree(
        str(fixtures_dir / "aligned_3seq.fasta"),
        output_dir=str(workdir),
    )
    assert Path(tree_file).exists()
    assert Path(tree_file).suffix == ".nwk"


def test_newick_file_can_be_read_back(fixtures_dir, workdir):
    _, tree_file = build_neighbor_joining_tree(
        str(fixtures_dir / "aligned_3seq.fasta"),
        output_dir=str(workdir),
    )
    parsed = Phylo.read(tree_file, "newick")
    assert parsed.count_terminals() == 3

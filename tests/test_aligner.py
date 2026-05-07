from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from modules.aligner import align_file


# Tests that don't actually need MUSCLE installed
# (mock subprocess.run so the wrapper logic runs without it)

def test_returns_none_when_muscle_missing(fixtures_dir, workdir):
    # subprocess.run raises FileNotFoundError if the binary isn't there
    with patch("modules.aligner.subprocess.run", side_effect=FileNotFoundError):
        result = align_file(
            str(fixtures_dir / "valid_5seq.fasta"),
            output_dir=str(workdir),
        )
    assert result is None


def test_returns_none_when_muscle_fails(fixtures_dir, workdir):
    # MUSCLE exits with status 1 -> wrapper should return None, not crash
    with patch("modules.aligner.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stderr="boom")
        result = align_file(
            str(fixtures_dir / "valid_5seq.fasta"),
            output_dir=str(workdir),
        )
    assert result is None


# Tests that need a real MUSCLE binary
# These get skipped automatically on machines that don't have MUSCLE.

@pytest.mark.requires_muscle
def test_real_muscle_produces_alignment(fixtures_dir, workdir, muscle_available):
    if not muscle_available:
        pytest.skip("MUSCLE not installed")

    result = align_file(
        str(fixtures_dir / "valid_5seq.fasta"),
        output_dir=str(workdir),
    )
    assert result is not None
    assert Path(result).exists()

    # all aligned sequences should be the same length
    from Bio import AlignIO
    alignment = AlignIO.read(result, "fasta")
    lengths = {len(rec.seq) for rec in alignment}
    assert len(lengths) == 1


@pytest.mark.requires_muscle
def test_real_muscle_keeps_sequence_ids(fixtures_dir, workdir, muscle_available):
    if not muscle_available:
        pytest.skip("MUSCLE not installed")

    result = align_file(
        str(fixtures_dir / "valid_5seq.fasta"),
        output_dir=str(workdir),
    )
    from Bio import AlignIO
    alignment = AlignIO.read(result, "fasta")
    ids = {rec.id for rec in alignment}
    assert ids == {"seq_001", "seq_002", "seq_003", "seq_004", "seq_005"}

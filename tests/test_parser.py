import pytest
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from modules.parser import read_fasta, extract_species


def test_read_fasta_returns_5_records(fixtures_dir):
    records = read_fasta(str(fixtures_dir / "valid_5seq.fasta"))
    assert len(records) == 5


def test_read_fasta_missing_file():
    with pytest.raises(FileNotFoundError):
        read_fasta("/not/a/real/file.fasta")


def test_read_fasta_empty_file(fixtures_dir):
    records = read_fasta(str(fixtures_dir / "empty.fasta"))
    assert records == []


# helper for the species-extraction tests
def make_record(description, rec_id="x"):
    return SeqRecord(Seq("AAA"), id=rec_id, description=description)


def test_extract_species_ncbi_brackets():
    rec = make_record(
        "seq_001 hemoglobin subunit beta [Homo sapiens]",
        rec_id="seq_001",
    )
    assert extract_species(rec) == "Homo sapiens"


def test_extract_species_uniprot():
    rec = make_record(
        "sp|P68871|HBB_HUMAN Hemoglobin subunit beta OS=Homo sapiens "
        "GN=HBB PE=1 SV=2",
        rec_id="sp|P68871|HBB_HUMAN",
    )
    assert extract_species(rec) == "Homo sapiens"


def test_extract_species_refseq():
    rec = make_record(
        "NC_018753.1 Nomascus gabriellae mitochondrion, complete genome",
        rec_id="NC_018753.1",
    )
    assert extract_species(rec) == "Nomascus gabriellae"


def test_extract_species_no_species_info():
    rec = make_record("seq_001", rec_id="seq_001")
    assert extract_species(rec) == "seq_001"

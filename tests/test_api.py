# Integration tests for app.py — drives the Flask test client end to end.

import io
import json
import pytest


def test_index_returns_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"TreeAlign" in response.data


def test_upload_with_no_file_returns_400(client):
    response = client.post("/upload")
    assert response.status_code == 400


def test_upload_with_empty_filename_returns_400(client):
    response = client.post(
        "/upload",
        data={"file": (io.BytesIO(b""), "")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400


def test_upload_with_bad_extension_returns_400(client):
    response = client.post(
        "/upload",
        data={"file": (io.BytesIO(b"content"), "not_fasta.docx")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400


def test_upload_with_too_few_sequences_returns_400(client, fixtures_dir):
    with open(fixtures_dir / "too_few_2seq.fasta", "rb") as f:
        response = client.post(
            "/upload",
            data={"file": (f, "too_few_2seq.fasta")},
            content_type="multipart/form-data",
        )
    assert response.status_code == 400


@pytest.mark.requires_muscle
def test_valid_upload_returns_tree(client, fixtures_dir, muscle_available):
    if not muscle_available:
        pytest.skip("MUSCLE not installed")
    with open(fixtures_dir / "valid_5seq.fasta", "rb") as f:
        response = client.post(
            "/upload",
            data={"file": (f, "valid_5seq.fasta")},
            content_type="multipart/form-data",
        )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["num_sequences"] == 5
    assert "newick" in data
    assert "id_to_species" in data

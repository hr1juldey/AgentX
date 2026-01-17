"""
Tests for PDF Summarizer API.
"""

import pytest
from fastapi.testclient import TestClient
from io import BytesIO

from main import app

client = TestClient(app)


@pytest.fixture
def sample_pdf_content():
    """Create a sample PDF content for testing."""
    # This is a minimal PDF file
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(This is a test PDF document.) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000264 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
347
%%EOF
"""
    return pdf_content


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["application"] == "PDF Summarizer"
    assert "endpoints" in data


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_upload_document(sample_pdf_content):
    """Test document upload."""
    files = {"file": ("test.pdf", BytesIO(sample_pdf_content), "application/pdf")}
    response = client.post("/api/v1/documents", files=files)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["filename"] == "test.pdf"
    assert "status" in data
    assert data["status"] in ["processing", "ready", "error"]


def test_upload_non_pdf():
    """Test uploading non-PDF file."""
    files = {"file": ("test.txt", BytesIO(b"not a pdf"), "text/plain")}
    response = client.post("/api/v1/documents", files=files)

    assert response.status_code == 400


def test_list_documents():
    """Test listing documents."""
    response = client.get("/api/v1/documents")

    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total" in data
    assert isinstance(data["documents"], list)


def test_get_nonexistent_document():
    """Test getting a document that doesn't exist."""
    response = client.get("/api/v1/documents/99999")

    assert response.status_code == 404


def test_generate_summary_for_nonexistent_document():
    """Test generating summary for nonexistent document."""
    response = client.post("/api/v1/documents/99999/summarize")

    assert response.status_code == 404


def test_get_summary_for_nonexistent_document():
    """Test getting summary for nonexistent document."""
    response = client.get("/api/v1/documents/99999/summary")

    assert response.status_code == 404


def test_delete_nonexistent_document():
    """Test deleting a document that doesn't exist."""
    response = client.delete("/api/v1/documents/99999")

    assert response.status_code == 404

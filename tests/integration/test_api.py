"""Integration tests for API endpoints"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
import tempfile
from pathlib import Path

# Create a test PDF file
def create_test_pdf():
    """Create a simple test PDF for testing"""
    import pikepdf
    temp_dir = Path(tempfile.gettempdir()) / "pdf_test"
    temp_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_dir / "test.pdf"
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page(page_size=(612, 792))
    pdf.save(str(pdf_path))
    return str(pdf_path)


@pytest.fixture
def client():
    return TestClient(app)


class TestAPI:
    """Test API endpoints"""

    def test_health_check(self, client: TestClient):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data

    def test_upload_pdf(self, client: TestClient):
        """Test PDF upload endpoint"""
        test_pdf_path = create_test_pdf()

        try:
            with open(test_pdf_path, 'rb') as f:
                response = client.post(
                    "/api/v1/pdf/upload",
                    files={"file": ("test.pdf", f, "application/pdf")}
                )

            assert response.status_code == 201
            data = response.json()

            assert "id" in data
            assert "test.pdf" in data["filename"]
            assert data["is_protected"] is False  # Test PDF is not protected
            assert data["message"] == "File uploaded successfully"

        finally:
            # Clean up test file
            if os.path.exists(test_pdf_path):
                os.unlink(test_pdf_path)

    def test_get_pdf_info(self, client: TestClient):
        """Test PDF info endpoint"""
        # First upload a PDF
        test_pdf_path = create_test_pdf()

        try:
            with open(test_pdf_path, 'rb') as f:
                upload_response = client.post(
                    "/api/v1/pdf/upload",
                    files={"file": ("test.pdf", f, "application/pdf")}
                )

            pdf_id = upload_response.json()["id"]

            # Now get info
            response = client.get(f"/api/v1/pdf/{pdf_id}/info")
            assert response.status_code == 200

            data = response.json()
            assert data["id"] == pdf_id
            assert "test.pdf" in data["filename"]
            assert data["is_protected"] is False

        finally:
            if os.path.exists(test_pdf_path):
                os.unlink(test_pdf_path)

    def test_crack_password_endpoint(self, client: TestClient):
        """Test password cracking endpoint"""
        # First upload a PDF
        test_pdf_path = create_test_pdf()

        try:
            with open(test_pdf_path, 'rb') as f:
                upload_response = client.post(
                    "/api/v1/pdf/upload",
                    files={"file": ("test.pdf", f, "application/pdf")}
                )

            pdf_id = upload_response.json()["id"]

            # Try to crack (should fail since it's not protected)
            response = client.post(
                f"/api/v1/crack/{pdf_id}",
                json={
                    "mode": "dictionary",
                    "max_length": 4
                }
            )

            # Should return error since PDF is not protected
            assert response.status_code == 400
            data = response.json()
            assert "not password protected" in data.get("detail", "").lower()

        finally:
            if os.path.exists(test_pdf_path):
                os.unlink(test_pdf_path)

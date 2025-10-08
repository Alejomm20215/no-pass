"""Integration tests for API endpoints"""

import pytest
from fastapi.testclient import TestClient
import os
import tempfile
from pathlib import Path

# Import the FastAPI app
from app.main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

# Create a test PDF file
def create_test_pdf():
    """Create a simple test PDF for testing"""
    import pikepdf

    # Use a specific temp directory to avoid Windows permission issues
    temp_dir = Path(tempfile.gettempdir()) / "pdf_test"
    temp_dir.mkdir(exist_ok=True)

    pdf_path = temp_dir / "test.pdf"

    try:
        pdf = pikepdf.Pdf.new()
        pdf.add_blank_page(page_size=(612, 792))
        pdf.save(str(pdf_path))
        return str(pdf_path)
    except Exception as e:
        # If pikepdf fails, try a different approach or skip test
        print(f"Warning: Could not create test PDF: {e}")
        # Return a path that doesn't exist to make tests fail gracefully
        return str(pdf_path)


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
            assert data["filename"] == "test.pdf"
            assert data["is_protected"] is False  # Test PDF is not protected
            assert data["message"] == "File uploaded successfully"

        finally:
            # Clean up test file and directory
            if os.path.exists(test_pdf_path):
                try:
                    os.unlink(test_pdf_path)
                    # Also try to remove the temp directory if it's empty
                    temp_dir = Path(test_pdf_path).parent
                    if temp_dir.exists() and not list(temp_dir.iterdir()):
                        temp_dir.rmdir()
                except Exception as e:
                    print(f"Warning: Could not clean up test file: {e}")

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
            # The filename will have a UUID prefix for security
            assert "test.pdf" in data["filename"]
            assert data["is_protected"] is False

        finally:
            if os.path.exists(test_pdf_path):
                try:
                    os.unlink(test_pdf_path)
                    # Also try to remove the temp directory if it's empty
                    temp_dir = Path(test_pdf_path).parent
                    if temp_dir.exists() and not list(temp_dir.iterdir()):
                        temp_dir.rmdir()
                except Exception as e:
                    print(f"Warning: Could not clean up test file: {e}")

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
                assert "not password protected" in data["detail"].lower()

        finally:
            if os.path.exists(test_pdf_path):
                try:
                    os.unlink(test_pdf_path)
                    temp_dir = Path(test_pdf_path).parent
                    if temp_dir.exists() and not list(temp_dir.iterdir()):
                        temp_dir.rmdir()
                except Exception as e:
                    print(f"Warning: Could not clean up test file: {e}")

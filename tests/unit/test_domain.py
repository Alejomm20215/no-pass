"""Unit tests for domain models"""

import pytest
from datetime import datetime
from pathlib import Path

from app.core.domain.entities import (
    PDFDocument,
    CrackJob,
    AttackOptions,
    CrackResult,
    AttackMode,
    CharsetType,
    JobStatus
)


class TestPDFDocument:
    """Test PDFDocument entity"""

    def test_creation(self):
        """Test PDF document creation"""
        pdf = PDFDocument(
            filename="test.pdf",
            size=1024,
            is_protected=True
        )

        assert pdf.filename == "test.pdf"
        assert pdf.size == 1024
        assert pdf.is_protected is True
        assert isinstance(pdf.created_at, datetime)
        assert pdf.id is not None

    def test_path_conversion(self):
        """Test path conversion"""
        pdf = PDFDocument(filename="test.pdf", file_path="/some/path.pdf")
        assert isinstance(pdf.file_path, Path)
        assert pdf.file_path.name == "path.pdf"
        assert "some" in str(pdf.file_path)


class TestAttackOptions:
    """Test AttackOptions entity"""

    def test_defaults(self):
        """Test default values"""
        options = AttackOptions()

        assert options.mode == AttackMode.DICTIONARY
        assert options.charset == CharsetType.NUMERIC
        assert options.min_length == 1
        assert options.max_length == 4
        assert options.max_attempts == 10000
        assert options.timeout == 3600
        assert options.verbose is False

    def test_custom_values(self):
        """Test custom values"""
        options = AttackOptions(
            mode=AttackMode.BRUTEFORCE,
            charset=CharsetType.ALPHANUMERIC,
            min_length=2,
            max_length=8,
            max_attempts=50000,
            timeout=1800,
            verbose=True,
            wordlist=["custom", "passwords"]
        )

        assert options.mode == AttackMode.BRUTEFORCE
        assert options.charset == CharsetType.ALPHANUMERIC
        assert options.min_length == 2
        assert options.max_length == 8
        assert options.max_attempts == 50000
        assert options.timeout == 1800
        assert options.verbose is True
        assert options.wordlist == ["custom", "passwords"]


class TestCrackJob:
    """Test CrackJob entity"""

    def test_creation(self):
        """Test job creation"""
        job = CrackJob(pdf_id="test-pdf-123")

        assert job.pdf_id == "test-pdf-123"
        assert job.status == JobStatus.QUEUED
        assert job.progress == 0.0
        assert job.options is not None
        assert isinstance(job.created_at, datetime)

    def test_job_lifecycle(self):
        """Test job state transitions"""
        job = CrackJob(pdf_id="test-pdf-123")

        # Start job
        job.start()
        assert job.status == JobStatus.PROCESSING
        assert job.started_at is not None

        # Complete job successfully
        result = CrackResult(success=True, password="123456", attempts=10)
        job.complete(result)
        assert job.status == JobStatus.COMPLETED
        assert job.result == result
        assert job.progress == 100.0
        assert job.completed_at is not None

    def test_job_failure(self):
        """Test job failure"""
        job = CrackJob(pdf_id="test-pdf-123")

        job.fail("Password not found")
        assert job.status == JobStatus.FAILED
        assert job.error == "Password not found"
        assert job.completed_at is not None

    def test_job_cancellation(self):
        """Test job cancellation"""
        job = CrackJob(pdf_id="test-pdf-123")

        job.cancel()
        assert job.status == JobStatus.CANCELLED
        assert job.completed_at is not None

    def test_progress_update(self):
        """Test progress updates"""
        job = CrackJob(pdf_id="test-pdf-123")

        job.update_progress(50.0)
        assert job.progress == 50.0

        # Test boundaries
        job.update_progress(-10.0)  # Should stay 0
        assert job.progress == 0.0

        job.update_progress(150.0)  # Should stay 100
        assert job.progress == 100.0


class TestCrackResult:
    """Test CrackResult entity"""

    def test_success_result(self):
        """Test successful result"""
        result = CrackResult(
            success=True,
            password="123456",
            method="dictionary",
            attempts=234,
            duration=12.5
        )

        assert result.success is True
        assert result.password == "123456"
        assert result.method == "dictionary"
        assert result.attempts == 234
        assert result.duration == 12.5
        assert result.error is None

    def test_failure_result(self):
        """Test failure result"""
        result = CrackResult(
            success=False,
            attempts=1000,
            duration=30.0,
            error="Password not found"
        )

        assert result.success is False
        assert result.password is None
        assert result.method is None
        assert result.attempts == 1000
        assert result.duration == 30.0
        assert result.error == "Password not found"

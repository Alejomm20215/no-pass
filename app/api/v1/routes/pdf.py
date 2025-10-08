"""PDF routes"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import FileResponse

from app.api.v1.schemas.pdf import UploadResponse, PDFInfo
from app.api.v1.schemas.response import ErrorResponse
from app.config.settings import Settings
from app.config.dependencies import get_settings, get_pdf_handler
from app.core.interfaces.pdf_handler import IPDFHandler
from app.core.domain.entities import PDFDocument

router = APIRouter(prefix="/pdf", tags=["PDF"])


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}},
)
async def upload_pdf(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    pdf_handler: IPDFHandler = Depends(get_pdf_handler),
):
    """Upload a PDF file"""

    # Validate file extension
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Check file size
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB

    # Save file
    file_id = PDFDocument().id  # Generate new ID
    file_path = settings.UPLOAD_DIR / f"{file_id}_{file.filename}"

    try:
        with open(file_path, "wb") as f:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                file_size += len(chunk)

                # Check size limit
                if file_size > settings.MAX_FILE_SIZE:
                    file_path.unlink()  # Delete partial file
                    raise HTTPException(
                        status_code=413,
                        detail=f"File size exceeds maximum {settings.MAX_FILE_SIZE} bytes",
                    )

                f.write(chunk)
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

    # Get PDF info
    try:
        pdf_doc = pdf_handler.get_pdf_info(file_path)
    except Exception as e:
        file_path.unlink()
        raise HTTPException(status_code=400, detail=f"Invalid PDF: {str(e)}")

    return UploadResponse(
        id=file_id,
        filename=file.filename or "uploaded.pdf",
        size=file_size,
        is_protected=pdf_doc.is_protected,
        message="File uploaded successfully",
    )


@router.get(
    "/{pdf_id}/info", response_model=PDFInfo, responses={404: {"model": ErrorResponse}}
)
async def get_pdf_info(
    pdf_id: str,
    settings: Settings = Depends(get_settings),
    pdf_handler: IPDFHandler = Depends(get_pdf_handler),
):
    """Get PDF information"""

    # Find file
    pdf_files = list(settings.UPLOAD_DIR.glob(f"{pdf_id}_*"))
    if not pdf_files:
        raise HTTPException(status_code=404, detail="PDF not found")

    pdf_path = pdf_files[0]
    pdf_doc = pdf_handler.get_pdf_info(pdf_path)

    return PDFInfo(
        id=pdf_id,
        filename=pdf_doc.filename,
        size=pdf_doc.size,
        is_protected=pdf_doc.is_protected,
        created_at=pdf_doc.created_at,
    )


@router.get(
    "/{pdf_id}/download",
    response_class=FileResponse,
    responses={404: {"model": ErrorResponse}},
)
async def download_pdf(pdf_id: str, settings: Settings = Depends(get_settings)):
    """Download PDF file"""

    # Find file in upload or output directory
    pdf_files = list(settings.UPLOAD_DIR.glob(f"{pdf_id}_*")) + list(
        settings.OUTPUT_DIR.glob(f"{pdf_id}_*")
    )

    if not pdf_files:
        raise HTTPException(status_code=404, detail="PDF not found")

    pdf_path = pdf_files[0]

    return FileResponse(
        path=pdf_path,
        filename=pdf_path.name.split("_", 1)[1],  # Remove ID prefix
        media_type="application/pdf",
    )


@router.delete(
    "/{pdf_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
async def delete_pdf(pdf_id: str, settings: Settings = Depends(get_settings)):
    """Delete PDF file"""

    # Find and delete file from both directories
    deleted = False
    for directory in [settings.UPLOAD_DIR, settings.OUTPUT_DIR]:
        pdf_files = list(directory.glob(f"{pdf_id}_*"))
        for pdf_file in pdf_files:
            pdf_file.unlink()
            deleted = True

    if not deleted:
        raise HTTPException(status_code=404, detail="PDF not found")

    return None

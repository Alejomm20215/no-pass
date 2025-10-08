"""Password cracking routes"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from pathlib import Path

from app.api.v1.schemas.crack import CrackRequest, CrackResponse, UnlockRequest, UnlockResponse
from app.api.v1.schemas.response import ErrorResponse
from app.config.settings import Settings
from app.config.dependencies import (
    get_settings,
    get_crack_password_use_case,
    get_unlock_pdf_use_case
)
from app.core.use_cases.crack_password import CrackPasswordUseCase
from app.core.use_cases.unlock_pdf import UnlockPDFUseCase
from app.core.domain.entities import AttackOptions

router = APIRouter(prefix="/crack", tags=["Password Cracking"])


@router.post(
    "/{pdf_id}",
    response_model=CrackResponse,
    responses={
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse}
    }
)
async def crack_pdf_password(
    pdf_id: str,
    request: CrackRequest,
    settings: Settings = Depends(get_settings),
    crack_use_case: CrackPasswordUseCase = Depends(get_crack_password_use_case)
):
    """Crack PDF password"""
    
    # Find PDF file
    pdf_files = list(settings.UPLOAD_DIR.glob(f"{pdf_id}_*"))
    if not pdf_files:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    pdf_path = pdf_files[0]
    
    # Prepare attack options
    options = AttackOptions(
        mode=request.mode,
        charset=request.charset,
        min_length=request.min_length,
        max_length=request.max_length,
        max_attempts=request.max_attempts,
        wordlist=request.custom_wordlist,
        wordlist_file=Path(request.wordlist_file) if request.wordlist_file else None,
        john_binary=request.john_binary or "john",
        pdf2john_binary=request.pdf2john_binary or "pdf2john.pl",
        pdfcrack_binary=request.pdfcrack_binary or "pdfcrack",
        timeout=request.timeout
    )
    
    # Execute crack
    try:
        result = crack_use_case.execute(pdf_path, options)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error or "Cracking failed")

    return CrackResponse(
        success=True,
        password=result.password,
        method=result.method,
        attempts=result.attempts,
        duration=result.duration
    )


@router.post(
    "/{pdf_id}/unlock",
    response_model=UnlockResponse,
    responses={
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse}
    }
)
async def unlock_pdf(
    pdf_id: str,
    request: UnlockRequest,
    settings: Settings = Depends(get_settings),
    unlock_use_case: UnlockPDFUseCase = Depends(get_unlock_pdf_use_case)
):
    """Unlock PDF by removing password"""
    
    # Find PDF file
    pdf_files = list(settings.UPLOAD_DIR.glob(f"{pdf_id}_*"))
    if not pdf_files:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    pdf_path = pdf_files[0]
    
    # Prepare output path
    output_path = settings.OUTPUT_DIR / f"{pdf_id}_{pdf_path.name.split('_', 1)[1]}"
    output_path = output_path.with_name(f"{output_path.stem}_unlocked.pdf")
    
    # Execute unlock
    try:
        result = unlock_use_case.execute(pdf_path, request.password, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    
    return UnlockResponse(
        success=True,
        output_filename=output_path.name
    )


@router.post(
    "/{pdf_id}/crack-and-unlock",
    response_model=dict,
    responses={
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse}
    }
)
async def crack_and_unlock(
    pdf_id: str,
    request: CrackRequest,
    settings: Settings = Depends(get_settings),
    crack_use_case: CrackPasswordUseCase = Depends(get_crack_password_use_case),
    unlock_use_case: UnlockPDFUseCase = Depends(get_unlock_pdf_use_case)
):
    """Crack password and automatically unlock PDF"""
    
    # Find PDF file
    pdf_files = list(settings.UPLOAD_DIR.glob(f"{pdf_id}_*"))
    if not pdf_files:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    pdf_path = pdf_files[0]
    
    # Prepare attack options
    options = AttackOptions(
        mode=request.mode,
        charset=request.charset,
        min_length=request.min_length,
        max_length=request.max_length,
        max_attempts=request.max_attempts,
        wordlist=request.custom_wordlist,
        timeout=request.timeout
    )
    
    # Execute crack
    try:
        crack_result = crack_use_case.execute(pdf_path, options)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    if not crack_result.success:
        return {
            "crack_success": False,
            "crack_result": CrackResponse(
                success=False,
                attempts=crack_result.attempts,
                duration=crack_result.duration,
                error=crack_result.error
            )
        }
    
    # Unlock with found password
    output_path = settings.OUTPUT_DIR / f"{pdf_id}_{pdf_path.name.split('_', 1)[1]}"
    output_path = output_path.with_name(f"{output_path.stem}_unlocked.pdf")
    
    try:
        unlock_result = unlock_use_case.execute(pdf_path, crack_result.password, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "crack_success": True,
        "crack_result": CrackResponse(
            success=True,
            password=crack_result.password,
            method=crack_result.method,
            attempts=crack_result.attempts,
            duration=crack_result.duration
        ),
        "unlock_success": unlock_result.success,
        "unlock_result": UnlockResponse(
            success=unlock_result.success,
            output_filename=output_path.name if unlock_result.success else None,
            error=unlock_result.error
        )
    }


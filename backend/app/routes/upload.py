import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.ingest import ingest_pdf
from app.models.schemas import UploadResponse
from app.core.auth import get_current_user

router = APIRouter()

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    document_id = str(uuid.uuid4())
    saved_filename = f"{document_id}.pdf"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)

    try:
        contents = await file.read()
        with open(saved_path, "wb") as f:
            f.write(contents)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")

    try:
        chunks_created = ingest_pdf(saved_path, document_id)
    except Exception as e:
        if os.path.exists(saved_path):
            os.remove(saved_path)
        raise HTTPException(
            status_code=503,
            detail=f"Failed to process PDF: {str(e)}"
        )

    if chunks_created == 0:
        raise HTTPException(
            status_code=400,
            detail="No extractable text found in this PDF. It may be a scanned/image-based document."
        )

    return UploadResponse(
        document_id=document_id,
        original_filename=file.filename,
        chunks_created=chunks_created,
        message="File uploaded and processed successfully",
    )

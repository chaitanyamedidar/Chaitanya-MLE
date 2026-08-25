from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.deps import get_current_user
from app.ml.gemini import extract_invoice, gemini_enabled
from app.models.user import User

router = APIRouter(tags=["extract"])

_ALLOWED = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
    "application/pdf",
}


@router.post("/extract/invoice")
async def extract_invoice_endpoint(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
) -> dict:
    _ = user
    if not gemini_enabled():
        raise HTTPException(status_code=503, detail="Gemini is not configured")
    mime = file.content_type or "application/octet-stream"
    if mime not in _ALLOWED:
        raise HTTPException(status_code=400, detail="Upload a PNG, JPEG, WebP, GIF, or PDF")
    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Empty file")
    try:
        draft = extract_invoice(payload, mime)
    except Exception as exc:  # noqa: BLE001 — surface model errors to the client
        raise HTTPException(status_code=502, detail=f"Could not read invoice: {exc}") from exc
    return {"draft": draft, "saved": False}

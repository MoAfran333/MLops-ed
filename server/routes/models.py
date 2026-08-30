from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from server.services.model_service import get_best_model_path

router = APIRouter(
    prefix="/api/models",
    tags=["Models"],
)


@router.get("/best/download")
def download_best_model():

    try:
        model_path = get_best_model_path()

        return FileResponse(
            model_path,
            media_type="application/octet-stream",
            filename="best_model.pkl",
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

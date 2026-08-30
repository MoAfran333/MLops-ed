from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from server.schemas.profiling import ProfileRequest, ProfileResponse
from server.services.profiling_services import get_profile_path, profile_dataset

router = APIRouter(
    prefix="/api/profile",
    tags=["profiling"],
)


@router.post("/", response_model=ProfileResponse)
def profile(
    request: ProfileRequest,
):

    try:
        return profile_dataset(request.dataset_id)

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Profile generation failed: {exc}",
        ) from exc


@router.get("/{filename}")
def get_profile(filename: str):

    try:
        profile_path = get_profile_path(filename)

        return FileResponse(
            profile_path,
            media_type="text/html",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

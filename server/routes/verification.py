from fastapi import APIRouter, HTTPException

from server.schemas.verification import (
    VerifyRequest,
    VerifyResponse,
)
from server.services.verification_services import verify_model

router = APIRouter(
    prefix="/api/verify",
    tags=["Verification"],
)


@router.post("/", response_model=VerifyResponse)
def verify(request: VerifyRequest):

    try:
        return verify_model(
            request.dataset_id,
            request.target_column,
            request.model,
        )

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
            detail=f"Verification failed: {exc}",
        ) from exc

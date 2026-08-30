from fastapi import APIRouter, HTTPException

from server.schemas.optimization import (
    OptimizeRequest,
    OptimizeResponse,
)
from server.services.optimization_services import optimize_model

router = APIRouter(
    prefix="/api/optimize",
    tags=["Optimization"],
)


@router.post("/", response_model=OptimizeResponse)
def optimize(request: OptimizeRequest):

    try:
        result = optimize_model(
            request.dataset_id,
            request.target_column,
            request.model,
        )

        result["download_url"] = "/api/models/best/download"

        return result

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
            detail=f"Optimization failed: {exc}",
        ) from exc

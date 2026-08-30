from fastapi import APIRouter, HTTPException

from server.schemas.recommendation import (
    RecommendRequest,
    RecommendResponse,
)
from server.services.recommendation_services import (
    recommend_model,
)

router = APIRouter(
    prefix="/api/recommendation",
    tags=["Recommendation"],
)


@router.post("/", response_model=RecommendResponse)
def recommend(
    request: RecommendRequest,
):

    try:
        return recommend_model(
            request.dataset_id,
            request.target_column,
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Model recommendation failed: {exc}",
        ) from exc

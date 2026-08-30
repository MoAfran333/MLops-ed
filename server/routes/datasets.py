from fastapi import APIRouter, File, HTTPException, UploadFile

from server.schemas.datasets import DatasetInfoResponse
from server.services.dataset_services import (
    DATA_DIR,
    get_dataset_info,
)

router = APIRouter(
    prefix="/api/datasets",
    tags=["Datasets"],
)


@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported.",
        )

    filename = file.filename

    destination = DATA_DIR / filename

    try:
        contents = await file.read()
        destination.write_bytes(contents)

        return get_dataset_info(filename)

    except Exception as exc:
        if destination.exists():
            destination.unlink()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/{dataset_id}",
    response_model=DatasetInfoResponse,
)
def dataset_info(dataset_id: str):

    try:
        return get_dataset_info(dataset_id)

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
            detail=f"Failed to read dataset: {exc}",
        ) from exc

from pathlib import Path

import pandas as pd

from server.config import DATA_DIR


def get_dataset_path(dataset_id: str) -> Path:
    path = Path(dataset_id)

    if path.name != dataset_id:
        raise ValueError("Invalid dataset identifier.")

    if path.suffix.lower() != ".csv":
        raise ValueError("Only CSV datasets are supported.")

    dataset_path = DATA_DIR / dataset_id

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset '{dataset_id}' not found.")

    return dataset_path


def load_dataset(dataset_id: str) -> pd.DataFrame:
    return pd.read_csv(get_dataset_path(dataset_id))


def get_dataset_info(dataset_id: str) -> dict:
    df = load_dataset(dataset_id)
    path = get_dataset_path(dataset_id)

    preview = (
        df.head(10)
        .astype(object)
        .where(pd.notna(df.head(10)), None)
        .to_dict(orient="records")
    )

    return {
        "dataset_id": dataset_id,
        "filename": path.name,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "preview": preview,
    }

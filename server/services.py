from pathlib import Path
from typing import Any

import pandas as pd

from compare_train_size import run_comparison
from src.meta_features import compute_meta_features, detect_problem_type
from src.meta_learner import MetaLearner
from src.model_tuner import ModelTuner
from src.profiling import generate_profile

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data" / "raw"
RESULTS_DIR = PROJECT_ROOT / "results"
MODELS_DIR = PROJECT_ROOT / "models"
PROFILES_DIR = RESULTS_DIR / "profiles"


DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
PROFILES_DIR.mkdir(parents=True, exist_ok=True)


META_LEARNER_PATH = MODELS_DIR / "meta_learner.pkl"
BEST_MODEL_PATH = MODELS_DIR / "best_model.pkl"


# ---------------------------------------------------------------------------
# Dataset helpers
# ---------------------------------------------------------------------------


def validate_dataset_id(dataset_id: str) -> str:
    """
    Prevent path traversal.

    The frontend should send a filename such as:
        WineQT.csv

    It should never be allowed to send:
        ../../something
    """
    path = Path(dataset_id)

    if path.name != dataset_id:
        raise ValueError("Invalid dataset identifier.")

    if path.suffix.lower() != ".csv":
        raise ValueError("Only CSV datasets are supported.")

    return dataset_id


def get_dataset_path(dataset_id: str) -> Path:
    dataset_id = validate_dataset_id(dataset_id)

    path = DATA_DIR / dataset_id

    if not path.exists():
        raise FileNotFoundError(f"Dataset '{dataset_id}' was not found.")

    return path


def load_dataset(dataset_id: str) -> pd.DataFrame:
    path = get_dataset_path(dataset_id)
    return pd.read_csv(path)


def get_dataset_info(dataset_id: str) -> dict[str, Any]:
    path = get_dataset_path(dataset_id)
    df = pd.read_csv(path)

    preview_df = df.head(10).copy()

    # Convert values into JSON-safe Python values.
    preview_df = preview_df.astype(object).where(
        pd.notna(preview_df),
        None,
    )

    return {
        "dataset_id": dataset_id,
        "filename": path.name,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "preview": preview_df.to_dict(orient="records"),
    }


# ---------------------------------------------------------------------------
# Recommendation
# ---------------------------------------------------------------------------


def recommend_model(
    dataset_id: str,
    target_column: str,
) -> dict[str, Any]:

    df = load_dataset(dataset_id)

    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' does not exist.")

    if not META_LEARNER_PATH.exists():
        raise FileNotFoundError(
            "Meta-learner model not found. Please train the meta-learner first."
        )

    # 1. Detect problem type
    problem_type = detect_problem_type(
        df,
        target_column,
    )

    # 2. Compute meta-features
    meta_features = compute_meta_features(
        df,
        target_column,
    )

    meta_features["problem_type"] = problem_type

    # 3. Load meta learner
    learner = MetaLearner.load(META_LEARNER_PATH)

    # 4. Predict recommended model
    recommended_model = learner.predict(meta_features)

    return {
        "dataset_id": dataset_id,
        "target_column": target_column,
        "problem_type": problem_type,
        "meta_features": meta_features,
        "recommended_model": recommended_model,
    }


# ---------------------------------------------------------------------------
# Profiling
# ---------------------------------------------------------------------------


def generate_dataset_profile(
    dataset_id: str,
) -> dict[str, str]:

    df = load_dataset(dataset_id)

    dataset_path = get_dataset_path(dataset_id)

    profile_path = generate_profile(
        df,
        dataset_path.stem,
        PROFILES_DIR,
    )

    profile_path = Path(profile_path)

    return {
        "dataset_id": dataset_id,
        "profile_path": str(profile_path),
    }


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


def verify_model(
    dataset_id: str,
    target_column: str,
    model: str,
) -> dict[str, Any]:

    df = load_dataset(dataset_id)

    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' does not exist.")

    problem_type = detect_problem_type(
        df,
        target_column,
    )

    results = run_comparison(
        df,
        dataset_id,
        target_column,
        problem_type,
        specific_model=model,
    )

    if not results:
        raise RuntimeError("Verification produced no results.")

    result = results[0]

    drop_percent = result.get("drop_percent")

    robust = drop_percent < 5 if drop_percent is not None else None

    return {
        "dataset": result["dataset"],
        "model": result["model"],
        "problem_type": problem_type,
        "baseline_score": result.get("baseline_score"),
        "small_train_score": result.get("small_train_score"),
        "score_drop": result.get("score_drop"),
        "drop_percent": drop_percent,
        "robust": robust,
    }


# ---------------------------------------------------------------------------
# Optimization
# ---------------------------------------------------------------------------


def optimize_model(
    dataset_id: str,
    target_column: str,
    model: str,
) -> dict[str, Any]:

    df = load_dataset(dataset_id)

    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' does not exist.")

    problem_type = detect_problem_type(
        df,
        target_column,
    )

    tuner = ModelTuner(MODELS_DIR)

    result = tuner.tune_and_build(
        df,
        target_column,
        problem_type,
        model,
    )

    if not result:
        raise RuntimeError("Optimization returned no results.")

    return {
        "status": "completed",
        "dataset_id": dataset_id,
        "target_column": target_column,
        "model_type": result["model_type"],
        "optimized_variant": result["optimized_variant"],
        "validation_score": result["validation_score"],
        "best_params": result["best_params"],
        "model_path": result["model_path"],
    }

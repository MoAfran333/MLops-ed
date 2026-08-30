from compare_train_size import run_comparison
from server.services.dataset_services import load_dataset
from src.meta_features import detect_problem_type


def verify_model(
    dataset_id: str,
    target_column: str,
    model: str,
) -> dict:

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

    return {
        "dataset": result["dataset"],
        "model": result["model"],
        "problem_type": problem_type,
        "baseline_score": result.get("baseline_score"),
        "small_train_score": result.get("small_train_score"),
        "score_drop": result.get("score_drop"),
        "drop_percent": drop_percent,
        "robust": (drop_percent < 5 if drop_percent is not None else None),
    }

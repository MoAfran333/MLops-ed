import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings("ignore")

DATA_DIR = Path(__file__).parent / "data" / "raw"
TEST_RESULTS_DIR = Path(__file__).parent / "results" / "test_results"

sys.path.insert(0, str(Path(__file__).parent / "src"))
from evaluator import compute_classification_metrics, compute_regression_metrics


def prepare_data(df, target_col):
    X = df.drop(columns=[target_col])
    y = df[target_col]

    if y.dtype == "object":
        le = LabelEncoder()
        y = le.fit_transform(y)

    for col in X.columns:
        if X[col].dtype == "object":
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))

    X = X.fillna(0)
    return X, y


def compute_baseline(df, dataset_name, target_col):

    X, y = prepare_data(df, target_col)

    # Check if regression or classification
    n_unique_classes = len(np.unique(y))
    is_classification = n_unique_classes <= 20

    if is_classification:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.15, stratify=y, shuffle=True, random_state=42
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.15, shuffle=True, random_state=42
        )

    if is_classification:
        models = {
            "LinearRegression": LogisticRegression(
                max_iter=2000, random_state=42, solver="lbfgs"
            ),
            "LogisticRegression": LogisticRegression(max_iter=2000, random_state=42),
            "DecisionTree": DecisionTreeClassifier(max_depth=10, random_state=42),
            "RandomForest": RandomForestClassifier(
                n_estimators=50, max_depth=10, random_state=42
            ),
            "GaussianNB": GaussianNB(),
        }
    else:
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.linear_model import LinearRegression as LinReg
        from sklearn.tree import DecisionTreeRegressor

        models = {
            "LinearRegression": LinReg(),
            "DecisionTree": DecisionTreeRegressor(max_depth=10, random_state=42),
            "RandomForest": RandomForestRegressor(
                n_estimators=50, max_depth=10, random_state=42
            ),
        }

    results = {}

    for model_name, model in models.items():
        model.fit(X_train, y_train)
        y_pred_test = model.predict(X_test)

        if is_classification:
            try:
                y_pred_proba = model.predict_proba(X_test)
            except:
                y_pred_proba = None
            metrics = compute_classification_metrics(y_test, y_pred_test, y_pred_proba)
            results[model_name] = metrics["composite_score"]
        else:
            metrics = compute_regression_metrics(y_test, y_pred_test)
            results[model_name] = metrics["composite_score"]

    return results, is_classification


def run_train_size_test(
    df, dataset_name, target_col, baseline_results, is_classification
):

    X, y = prepare_data(df, target_col)

    if is_classification:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.85, stratify=y, shuffle=True, random_state=42
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.85, shuffle=True, random_state=42
        )

    if is_classification:
        models = {
            "LinearRegression": LogisticRegression(
                max_iter=2000, random_state=42, solver="lbfgs"
            ),
            "LogisticRegression": LogisticRegression(max_iter=2000, random_state=42),
            "DecisionTree": DecisionTreeClassifier(max_depth=10, random_state=42),
            "RandomForest": RandomForestClassifier(
                n_estimators=50, max_depth=10, random_state=42
            ),
            "GaussianNB": GaussianNB(),
        }
    else:
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.linear_model import LinearRegression as LinReg
        from sklearn.tree import DecisionTreeRegressor

        models = {
            "LinearRegression": LinReg(),
            "DecisionTree": DecisionTreeRegressor(max_depth=10, random_state=42),
            "RandomForest": RandomForestRegressor(
                n_estimators=50, max_depth=10, random_state=42
            ),
        }

    results = []

    for model_name, model in models.items():
        model.fit(X_train, y_train)
        y_pred_test = model.predict(X_test)

        if is_classification:
            try:
                y_pred_proba = model.predict_proba(X_test)
            except:
                y_pred_proba = None
            metrics = compute_classification_metrics(y_test, y_pred_test, y_pred_proba)
            test_score = metrics["composite_score"]
        else:
            metrics = compute_regression_metrics(y_test, y_pred_test)
            test_score = metrics["composite_score"]

        baseline_score = baseline_results.get(model_name, None)

        if baseline_score:
            accuracy_drop = baseline_score - test_score
            drop_percent = (accuracy_drop / baseline_score) * 100
        else:
            accuracy_drop = None
            drop_percent = None

        results.append(
            {
                "dataset": dataset_name,
                "model": model_name,
                "baseline_score": baseline_score,
                "small_train_score": test_score,
                "score_drop": accuracy_drop,
                "drop_percent": drop_percent,
            }
        )

    return results


def main():
    print("\n" + "=" * 100)
    print("TRAIN SIZE IMPACT COMPARISON: 15% Training vs 85% Baseline")
    print("=" * 100)

    csv_files = sorted([f for f in DATA_DIR.glob("*.csv")])

    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}")
        return

    print("\nAvailable datasets:")
    for i, f in enumerate(csv_files, 1):
        print(f"  {i}. {f.name}")

    while True:
        try:
            choice = input(
                "\nSelect dataset(s) to compare (comma-separated, e.g. 1,2 or just 1): "
            ).strip()
            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            if all(0 <= i < len(csv_files) for i in indices):
                selected_files = [csv_files[i] for i in indices]
                break
            else:
                print(
                    f"Invalid selection. Enter numbers between 1 and {len(csv_files)}"
                )
        except ValueError:
            print("Invalid input. Try again.")

    datasets = []
    for csv_file in selected_files:
        target_col = input(f"Enter target column for {csv_file.name}: ").strip()
        datasets.append({"file": csv_file.name, "target": target_col})

    all_results = []

    for cfg in datasets:
        dataset_name = cfg["file"]
        target_col = cfg["target"]

        csv_path = DATA_DIR / dataset_name

        if not csv_path.exists():
            print(f"\n⚠️  {dataset_name} not found, skipping...")
            continue

        print(f"\nProcessing: {dataset_name}...")
        df = pd.read_csv(csv_path)

        print("  Computing baseline (85% train)...")
        baseline_results, is_classification = compute_baseline(
            df, dataset_name, target_col
        )

        print("  Computing small data test (15% train)...")
        results = run_train_size_test(
            df, dataset_name, target_col, baseline_results, is_classification
        )
        all_results.extend(results)

    TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results_df = pd.DataFrame(all_results)
    output_path = TEST_RESULTS_DIR / "train_size_comparison.csv"
    results_df.to_csv(output_path, index=False)

    print(f"\n{'=' * 100}")
    print("COMPARISON TABLE: 85% Train (Baseline) vs 15% Train")
    print("=" * 100)
    print(
        results_df[
            [
                "dataset",
                "model",
                "baseline_score",
                "small_train_score",
                "score_drop",
                "drop_percent",
            ]
        ].to_string(index=False)
    )

    print(f"\n{'=' * 100}")
    print("SUMMARY BY DATASET")
    print("=" * 100)

    for dataset in results_df["dataset"].unique():
        subset = results_df[results_df["dataset"] == dataset]
        print(f"\n{dataset}:")
        print(f"  {'Model':<20} {'Baseline':<12} {'15% Train':<12} {'Drop':<10}")
        print(f"  {'-' * 54}")
        for _, row in subset.iterrows():
            baseline = (
                f"{row['baseline_score']:.4f}"
                if pd.notna(row["baseline_score"])
                else "N/A"
            )
            small = f"{row['small_train_score']:.4f}"
            drop = (
                f"{row['drop_percent']:.2f}%"
                if pd.notna(row["drop_percent"])
                else "N/A"
            )
            print(f"  {row['model']:<20} {baseline:<12} {small:<12} {drop:<10}")


if __name__ == "__main__":
    main()

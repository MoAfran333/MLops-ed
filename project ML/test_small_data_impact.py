#!/usr/bin/env python
"""
TEST SCRIPT: Train on 15% of data, test on remaining 85%.
Compare accuracy drop vs baseline (trained on 85%).

Shows model sensitivity to training set size.
"""

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


def prepare_data(df, target_col):
    """
    Prepare data for modeling:
    - Separate features and target
    - Encode categorical features
    - Handle missing values

    Returns X, y (both ready for sklearn)
    """
    # Separate
    X = df.drop(columns=[target_col])
    y = df[target_col]

    # Encode target if categorical
    if y.dtype == "object":
        le = LabelEncoder()
        y = le.fit_transform(y)

    # Encode categorical features (use label encoding for simplicity)
    for col in X.columns:
        if X[col].dtype == "object":
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))

    # Fill any remaining NaNs with 0
    X = X.fillna(0)

    return X, y


def run_small_data_test(df, dataset_name, target_col):
    """
    Train on 15% of data, test on 85%.
    Compare vs baseline (85% train, 15% test).

    Returns comparison results.
    """
    print(f"\nPreparing data for {dataset_name}...")
    X, y = prepare_data(df, target_col)

    # Stratified split: 15% train, 85% test (REVERSED from baseline)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.85,  # 85% for testing
        stratify=y,
        shuffle=True,
        random_state=42,
    )

    print("\nSmall Data Training Setup:")
    print(f"  Train set: {X_train.shape}")
    print(f"  Test set:  {X_test.shape}")
    print(f"  Train/Total ratio: {X_train.shape[0] / X.shape[0]:.1%}")
    print(f"  Class distribution (train): {np.bincount(y_train)}")
    print(f"  Class distribution (test):  {np.bincount(y_test)}")

    # Define models
    models = {
        "LogisticRegression": LogisticRegression(max_iter=2000, random_state=42),
        "DecisionTree": DecisionTreeClassifier(max_depth=10, random_state=42),
        "RandomForest": RandomForestClassifier(
            n_estimators=50, max_depth=10, random_state=42
        ),
        "GaussianNB": GaussianNB(),
    }

    # Baseline results (from previous test: 85% train, 15% test)
    baseline = {
        "LogisticRegression": 0.8050,
        "DecisionTree": 0.8612,
        "RandomForest": 0.8639,
        "GaussianNB": 0.7973,
    }

    results = []

    print(f"\n{'=' * 90}")
    print("SMALL DATA TEST: Train on 15% → Evaluate on 85%")
    print("=" * 90)

    for model_name, model in models.items():
        print(f"\n  {model_name}...")

        try:
            # Train on small (15%) dataset
            model.fit(X_train, y_train)

            # Test on large (85%) held-out set
            test_acc = model.score(X_test, y_test)

            # Compare to baseline
            baseline_acc = baseline[model_name]
            accuracy_drop = baseline_acc - test_acc
            drop_percent = (accuracy_drop / baseline_acc) * 100

            print(f"    Baseline (85% train):      {baseline_acc:.4f}")
            print(f"    Small data (15% train):    {test_acc:.4f}")
            print(
                f"    Accuracy drop:             {accuracy_drop:.4f} ({drop_percent:.2f}%)"
            )

            results.append(
                {
                    "dataset": dataset_name,
                    "model": model_name,
                    "baseline_acc_85pct_train": baseline_acc,
                    "small_data_acc_15pct_train": test_acc,
                    "accuracy_drop": accuracy_drop,
                    "drop_percentage": drop_percent,
                }
            )
        except Exception as e:
            print(f"    ✗ Error: {e}")

    return results


def main():
    print("\n" + "=" * 90)
    print("TEST: SMALL DATA IMPACT (15% Training vs Baseline 85% Training)")
    print("=" * 90)
    print("\nScenario: What happens if we only have 15% of training data?")
    print(
        "Comparison: Baseline test (85% train, 15% test) vs Small Data (15% train, 85% test)"
    )

    # Configuration
    config = [
        {
            "dataset": "adult.csv",
            "target": "income",
        }
    ]

    all_results = []

    for cfg in config:
        dataset_name = cfg["dataset"]
        target_col = cfg["target"]

        csv_path = DATA_DIR / dataset_name
        print(f"\nLoading: {csv_path}")
        df = pd.read_csv(csv_path)

        results = run_small_data_test(df, dataset_name, target_col)
        all_results.extend(results)

    # Save results
    TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results_df = pd.DataFrame(all_results)
    output_path = TEST_RESULTS_DIR / "small_data_comparison.csv"
    results_df.to_csv(output_path, index=False)

    print(f"\n{'=' * 90}")
    print(f"Small Data Test Results saved to: {output_path}")
    print("=" * 90)
    print(results_df.to_string(index=False))

    # Print summary
    print(f"\n{'=' * 90}")
    print("SUMMARY: IMPACT OF REDUCED TRAINING DATA")
    print("=" * 90)
    for _, row in results_df.iterrows():
        print(f"\n{row['model']}:")
        print(f"  Baseline (85% train):     {row['baseline_acc_85pct_train']:.4f}")
        print(f"  Small data (15% train):   {row['small_data_acc_15pct_train']:.4f}")
        print(
            f"  Drop:                     {row['accuracy_drop']:.4f} ({row['drop_percentage']:.2f}%)"
        )

        if row["drop_percentage"] < 5:
            print("  Resilience:               ✓ Very resilient (< 5% drop)")
        elif row["drop_percentage"] < 10:
            print("  Resilience:               ✓ Resilient (5-10% drop)")
        else:
            print("  Resilience:               ⚠️ Sensitive to data size (> 10% drop)")


if __name__ == "__main__":
    main()

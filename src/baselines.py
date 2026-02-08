import warnings
warnings.filterwarnings('ignore')

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score, StratifiedKFold, KFold
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.naive_bayes import GaussianNB
from meta_features import detect_problem_type

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
RESULTS_DIR = Path(__file__).parent.parent / "results"


def prepare_data(df, target_col, problem_type):
    
    X = df.drop(columns=[target_col])
    y = df[target_col]

    # Handle target encoding based on problem type
    if problem_type == 'Classification':
        if y.dtype == 'object' or not pd.api.types.is_numeric_dtype(y):
            le = LabelEncoder()
            y = le.fit_transform(y)
    # For Regression, ensure y is numeric, drop NaNs in target if any (usually handled by dropna before)
    
    # Handle feature encoding
    for col in X.columns:
        if X[col].dtype == 'object':
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))

    X = X.fillna(0)
    
    return X, y


def run_baselines(df, dataset_name, target_col, problem_type=None):
    
    if problem_type is None:
        problem_type = detect_problem_type(df, target_col)
        
    print(f"\nPreparing data for {dataset_name} ({problem_type})...")
    X, y = prepare_data(df, target_col, problem_type)
    
    print(f"X shape: {X.shape}, y shape: {y.shape}")
    if problem_type == 'Classification':
        print(f"y unique classes: {np.unique(y)}")
    
    results = []
    
    if problem_type == 'Classification':
        models = {
            "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
            "DecisionTree": DecisionTreeClassifier(max_depth=10, random_state=42),
            "RandomForest": RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42),
            "GaussianNB": GaussianNB(),
        }
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scoring = 'accuracy'
    else:
        models = {
            "LinearRegression": LinearRegression(),
            "DecisionTree": DecisionTreeRegressor(max_depth=10, random_state=42),
            "RandomForest": RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42),
        }
        cv = KFold(n_splits=5, shuffle=True, random_state=42)
        scoring = 'neg_mean_squared_error' # Standard sklearn scoring for regression

    print(f"\nRunning 5-fold CV for {dataset_name}:")
    print("-" * 70)
    
    for model_name, model in models.items():
        print(f"\n  {model_name}...", end=" ", flush=True)
        
        try:
            scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)
            
            if problem_type == 'Regression':
                # Convert neg_mean_squared_error to RMSE
                scores = np.sqrt(-scores)
                mean_score = scores.mean() # This is now RMSE
                std_score = scores.std()
                score_name = "RMSE"
            else:
                mean_score = scores.mean()
                std_score = scores.std()
                score_name = "Accuracy"
            
            print(f"{score_name}: {mean_score:.4f} ± {std_score:.4f}")
            results.append({
                "dataset": dataset_name,
                "model": model_name,
                "problem_type": problem_type,
                "score_name": score_name,
                "mean_score": mean_score,
                "std_score": std_score,
            })
        except Exception as e:
            print(f"✗ Error: {e}")
    
    return results


def main():
    print("\n" + "="*70)
    print("BASELINE MODEL EVALUATION (5-fold CV)")
    print("="*70)
    
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
        
        results = run_baselines(df, dataset_name, target_col)
        all_results.extend(results)
    
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results_df = pd.DataFrame(all_results)
    output_path = RESULTS_DIR / "baseline_results.csv"
    results_df.to_csv(output_path, index=False)
    
    print(f"\n{'='*70}")
    print(f"Results saved to: {output_path}")
    print("="*70)
    print(results_df.to_string(index=False))


if __name__ == "__main__":
    main()

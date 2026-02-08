#!/usr/bin/env python
"""
TEST SCRIPT: Baseline model evaluation on held-out 15% test set.
No data leakage. Stratified split with shuffle.

This is a standalone test - NOT integrated to main pipeline.
Compares: 5-fold CV accuracy (on 85% train) vs Test accuracy (on 15% test)
"""

import warnings
warnings.filterwarnings('ignore')

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score, StratifiedKFold, train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB

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
    if y.dtype == 'object':
        le = LabelEncoder()
        y = le.fit_transform(y)
    
    # Encode categorical features (use label encoding for simplicity)
    for col in X.columns:
        if X[col].dtype == 'object':
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
    
    # Fill any remaining NaNs with 0
    X = X.fillna(0)
    
    return X, y


def run_test_comparison(df, dataset_name, target_col):
    """
    Run baseline models with strict train/test split:
    - 85% train (used for 5-fold CV)
    - 15% test (held-out, no data leakage)
    
    Returns list of results with CV accuracy and test accuracy.
    """
    print(f"\nPreparing data for {dataset_name}...")
    X, y = prepare_data(df, target_col)
    
    # Stratified train/test split (85/15)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.15, 
        stratify=y, 
        shuffle=True, 
        random_state=42
    )
    
    print(f"Train set: {X_train.shape}, Test set: {X_test.shape}")
    print(f"Class distribution (train): {np.bincount(y_train)}")
    print(f"Class distribution (test): {np.bincount(y_test)}")
    
    # Define models
    models = {
        "LinearRegression": LogisticRegression(max_iter=2000, random_state=42, solver='lbfgs'),
        "LogisticRegression": LogisticRegression(max_iter=2000, random_state=42),
        "DecisionTree": DecisionTreeClassifier(max_depth=10, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42),
        "GaussianNB": GaussianNB(),
    }
    
    # 5-fold Stratified CV on training set
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    results = []
    
    print(f"\n{'='*80}")
    print(f"Running 5-fold CV (on 85% train) + Test evaluation (on 15% test)")
    print('='*80)
    
    for model_name, model in models.items():
        print(f"\n  {model_name}...")
        
        try:
            # 5-fold CV on training set
            cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy')
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
            
            # Train on full training set and evaluate on test set
            model.fit(X_train, y_train)
            test_acc = model.score(X_test, y_test)
            
            # Compute overfitting metric
            overfitting_gap = cv_mean - test_acc
            
            print(f"    CV (5-fold):    {cv_mean:.4f} ± {cv_std:.4f}")
            print(f"    Test accuracy:  {test_acc:.4f}")
            print(f"    Overfitting gap: {overfitting_gap:.4f} {'⚠️ HIGH' if overfitting_gap > 0.05 else '✓ OK'}")
            
            results.append({
                "dataset": dataset_name,
                "model": model_name,
                "cv_mean_acc": cv_mean,
                "cv_std_acc": cv_std,
                "test_acc": test_acc,
                "overfitting_gap": overfitting_gap,
            })
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    return results


def main():
    print("\n" + "="*80)
    print("TEST: BASELINE MODELS ON HELD-OUT 15% TEST SET")
    print("="*80)
    print("Configuration: 85% train (5-fold CV) vs 15% test (held-out)")
    print("Split: Stratified, shuffled, no data leakage")
    
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
        
        results = run_test_comparison(df, dataset_name, target_col)
        all_results.extend(results)
    
    # Save results to test directory
    TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results_df = pd.DataFrame(all_results)
    output_path = TEST_RESULTS_DIR / "baseline_test_comparison.csv"
    results_df.to_csv(output_path, index=False)
    
    print(f"\n{'='*80}")
    print(f"Test Results saved to: {output_path}")
    print("="*80)
    print(results_df.to_string(index=False))
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print("="*80)
    for _, row in results_df.iterrows():
        print(f"\n{row['model']}:")
        print(f"  CV Accuracy:       {row['cv_mean_acc']:.4f} ± {row['cv_std_acc']:.4f}")
        print(f"  Test Accuracy:     {row['test_acc']:.4f}")
        print(f"  Generalization:    {'✓ Good' if abs(row['overfitting_gap']) < 0.05 else '⚠️ Check overfitting' if row['overfitting_gap'] > 0 else '✓ Underfitting likely'}")


if __name__ == "__main__":
    main()

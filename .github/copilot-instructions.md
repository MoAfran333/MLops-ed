# AI Copilot Instructions for ML Dataset Analysis System

## Project Overview

This is a meta-learning dataset analysis system that profiles ML datasets and evaluates baseline model performance. It:
1. **Profiles datasets** - Extracts 7 statistical meta-features (n_samples, n_features, missing_ratio, avg_variance, avg_abs_correlation, class_entropy, imbalance_ratio)
2. **Trains baselines** - Evaluates 4 baseline classifiers via 5-fold stratified cross-validation
3. **Analyzes data sensitivity** - Measures how model performance degrades with limited training data (85% train vs 15% train)

The codebase is intentionally simple - designed to establish baseline expectations and support AutoML algorithm selection strategies.

---

## Architecture & Key Components

### Module Structure
- **`src/meta_features.py`** - `compute_meta_features(df, target_col)` → Extracts 7 dataset characteristics
- **`src/baselines.py`** - `run_baselines(df, dataset_name, target_col)` → Trains 4 models with 5-fold stratified CV; `prepare_data()` → Label encodes categoricals, fills NaN with 0
- **`src/evaluator.py`** - Classification and regression metric computation; supports composite score normalization
- **`run_pipeline.py`** - Main entry point: interactive dataset selection → meta-features + baseline training
- **`compare_train_size.py`** - Compares model performance at 85% vs 15% training set size
- **`test_baseline_comparison.py`** - Validation: cross-validation accuracy vs held-out test accuracy
- **`test_small_data_impact.py`** - Validation: model performance with 15% training data

### Complete Dependency Graph
```
run_pipeline.py
  ├─→ src/meta_features.py (compute_meta_features)
  ├─→ src/baselines.py (run_baselines, prepare_data)
  └─→ src/evaluator.py (NOT USED in main pipeline)

compare_train_size.py
  ├─→ src/evaluator.py (compute_classification_metrics, compute_regression_metrics)
  ├─→ src/baselines.py (prepare_data - reimplemented locally)
  └─→ local functions (compute_baseline, run_train_size_test)

test_baseline_comparison.py (standalone, NO src imports)
test_small_data_impact.py (standalone, NO src imports)
```

### Directory Structure
```
project ML/
├── run_pipeline.py              # Main: meta-features + baselines
├── compare_train_size.py        # Training size sensitivity (85% vs 15%)
├── test_baseline_comparison.py  # Validation: CV vs test accuracy
├── test_small_data_impact.py    # Validation: 15% train degradation
├── data/raw/                    # Input CSV files (user-uploaded)
├── results/
│   ├── meta_features.csv        # Output: dataset characteristics
│   ├── baseline_results.csv     # Output: model CV scores
│   └── test_results/
│       ├── baseline_test_comparison.csv  # CV vs test accuracy
│       ├── small_data_comparison.csv     # 15% train metrics
│       └── train_size_comparison.csv     # Training size sensitivity
└── src/
    ├── meta_features.py
    ├── baselines.py
    └── evaluator.py
```

---

## Critical Implementation Patterns

### 1. Task Classification: Classification vs Regression (CORE LOGIC)
- **Where:** [src/meta_features.py](src/meta_features.py#L44-L52), [src/baselines.py](src/baselines.py)
- **Rule:** `n_unique_target_values ≤ 20` OR `target_dtype == 'object'` → **Classification**; otherwise **Regression**
- **Impact:** 
  - Classification: compute `class_entropy`, `imbalance_ratio`; use StratifiedKFold; train classifiers
  - Regression: these metrics return None; use standard KFold; train regressors
- **Critical:** This boundary determines available meta-features and available models

### 2. Data Preprocessing Convention (MUST BE IDENTICAL EVERYWHERE)
All scripts implement `prepare_data()` identically:
```python
1. Drop target column from X
2. Label-encode target if categorical (using LabelEncoder)
3. Label-encode ALL categorical features in X (using LabelEncoder)
4. Fill remaining NaN with 0 in X
5. Return (X, y) as numeric DataFrames/Series
```
**Location:** [src/baselines.py](src/baselines.py#L17-L33); **Reimplemented in:** compare_train_size.py, test_baseline_comparison.py, test_small_data_impact.py
**Note:** This is intentional simplification (not production ML); using consistent NaN handling enables baseline comparison

### 3. Meta-Feature Computation Edge Cases
| Scenario | avg_variance | avg_abs_correlation | class_entropy | imbalance_ratio |
|----------|--------------|---------------------|---------------|-----------------|
| No numeric features | `None` | `None` | computed | computed |
| Regression task | computed | `None` | `None` | `None` |
| No target column | computed | `None` | `None` | `None` |
| Single class | computed | computed | 0.0 | `None` |
| All NaN in feature | 0.0 | skipped | - | - |

**See:** [src/meta_features.py](src/meta_features.py) lines 25-95 for full logic

### 4. Cross-Validation Strategy
- **Pattern:** `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` for classification
- **Output format:** List of dicts `[{dataset, model, mean_acc, std_acc}, ...]`
- **Why stratified:** Preserves class distribution in each fold (critical for imbalanced datasets)

### 5. Baseline Models (Classification Only)
```python
models = {
    "LinearRegression": LogisticRegression(max_iter=1000, random_state=42, solver='lbfgs'),
    "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
    "DecisionTree": DecisionTreeClassifier(max_depth=10, random_state=42),
    "RandomForest": RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42),
    "GaussianNB": GaussianNB(),
}
```
**Note:** First model is misnamed ("LinearRegression" is actually LogisticRegression); do NOT fix (for consistency with existing results)

### 6. Metric Computation Strategy
**Classification** (via [src/evaluator.py](src/evaluator.py)):
- accuracy, precision (weighted), recall (weighted), F1 (weighted)
- ROC-AUC (binary classification only; None for multi-class)
- **Composite score:** mean(accuracy, precision, recall, f1)

**Regression** (via [src/evaluator.py](src/evaluator.py)):
- MAE, RMSE, R² (normalized to [0, 1])
- **Composite score:** mean(normalized_metrics)

---

## Developer Workflows

### Running the Main Pipeline
```bash
python run_pipeline.py
```
Interactive flow:
1. Lists CSV files in `data/raw/`
2. User selects dataset number
3. User enters target column name
4. Computes meta-features → saves to `results/meta_features.csv`
5. Trains baselines (5-fold CV) → saves to `results/baseline_results.csv`

### Testing Model Sensitivity to Training Data Size
```bash
python compare_train_size.py
```
Compares:
- **Baseline:** 85% train, 15% test
- **Small data:** 15% train, 85% test
Output: `results/test_results/train_size_comparison.csv` with columns: `dataset, model, baseline_score, small_train_score, score_drop, drop_percent`

### Running Validation Tests
```bash
python test_baseline_comparison.py   # Validates CV estimates vs held-out test set
python test_small_data_impact.py     # Tests model degradation with 15% training data
```
These are **standalone scripts** (no src imports) for independent validation.

---

## Project-Specific Conventions

1. **Results Organization:** 
   - Main results: `results/` (meta_features.csv, baseline_results.csv)
   - Test results: `results/test_results/` (auto-created)
   - Append mode: files are created if missing, appended if exist

2. **Reproducibility:** ALL sklearn models/CV use `random_state=42`

3. **Import Pattern:** Main scripts add src to path:
   ```python
   sys.path.insert(0, str(Path(__file__).parent / "src"))
   from meta_features import compute_meta_features
   ```

4. **Error Handling:** Model training errors are caught and logged; execution continues

5. **Hyperparameter Strategy:** Fixed hyperparameters for all models (no tuning; intentional baseline strategy)

6. **Data Type Handling:** Label encoding used uniformly (simple, handles mixed dtypes; not production-ready)

---

## Common Patterns to Follow When Extending

### Adding a New Baseline Model
1. Add entry to `models` dict in [src/baselines.py](src/baselines.py)
2. Ensure model supports `cross_val_score()`
3. Verify compatible with `StratifiedKFold` (for classification)
4. Use `random_state=42`

### Computing New Meta-Features
1. Add computation logic to `compute_meta_features()` [src/meta_features.py](src/meta_features.py)
2. Return `None` for regression/unsupported task types
3. Handle edge cases: empty features, all NaN, single value
4. Add key to return dict

### Creating New Test Scripts
Follow [test_baseline_comparison.py](test_baseline_comparison.py) pattern:
- Standalone script (NO imports from src)
- Reimplement `prepare_data()` locally
- Use StratifiedKFold for train/test splits
- Save results to `results/test_results/`

### Handling New Datasets
- Only requirement: CSV file with column headers + target column exists
- Preprocessing handles: mixed dtypes, missing values, categorical features
- Task type auto-detected via unique target values

---

## External Dependencies
```
pandas>=1.0
numpy>=1.19
scikit-learn>=0.24
```

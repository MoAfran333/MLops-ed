# ML Dataset Meta-Analysis & Baseline Comparison System

A Python-based system for analyzing machine learning datasets, computing meta-features, running baseline models, and comparing model sensitivity to training set sizes.

---

## System Overview

This system performs three core operations:

1. **Dataset Meta-Analysis** - Compute statistical meta-features of datasets
2. **Baseline Model Evaluation** - Train and cross-validate baseline classifiers
3. **Training Data Sensitivity Analysis** - Compare model performance with different training set sizes

---

## Directory Structure

```
project ML/
├── run_pipeline.py              # Main entry point: meta-features + baseline models
├── compare_train_size.py        # Training size impact analysis (15% vs 85% train)
├── test_baseline_comparison.py  # Standalone test: CV vs held-out test accuracy
├── test_small_data_impact.py    # Standalone test: small data impact evaluation
│
├── data/
│   └── raw/
│       ├── adult.csv
│       ├── Housing.csv
│       ├── iot_energy_management_dataset.csv
│       ├── sensor_maintenance_data.csv
│       ├── student_lifestyle_dataset.csv
│       └── WineQT.csv
│
├── results/
│   ├── baseline_results.csv     # Output: baseline model 5-fold CV scores
│   ├── meta_features.csv        # Output: computed dataset meta-features
│   └── test_results/
│       ├── baseline_test_comparison.csv      # Output: CV vs test accuracy
│       ├── small_data_comparison.csv         # Output: 15% train impact
│       └── train_size_comparison.csv         # Output: training size sensitivity
│
└── src/
    ├── meta_features.py         # Meta-feature computation
    ├── baselines.py             # Baseline model training
    └── evaluator.py             # Metric calculations
```

---

## Core Modules

### 1. `src/meta_features.py`
**Function:** `compute_meta_features(df, target_col)`

Computes statistical characteristics of a dataset:

- `n_samples` - Number of rows
- `n_features` - Number of feature columns
- `missing_ratio` - Proportion of missing values
- `avg_variance` - Average variance across numeric features
- `avg_abs_correlation` - Mean absolute correlation with target
- `class_entropy` - Shannon entropy of target distribution (classification)
- `imbalance_ratio` - Max/min class frequency ratio (classification)

**Key Logic:**
- Handles both classification (≤20 unique values) and regression tasks
- Factorizes categorical targets for correlation computation
- Returns None for regression-specific metrics

---

### 2. `src/baselines.py`
**Function:** `run_baselines(df, dataset_name, target_col)`

Trains baseline classifiers using 5-fold stratified cross-validation:

**Models (Classification only):**
- LogisticRegression (2 configurations)
- DecisionTreeClassifier (max_depth=10)
- RandomForestClassifier (50 trees, max_depth=10)
- GaussianNB

**Data Preprocessing:**
- `prepare_data()` - Label encodes categorical features, fills NaN with 0
- Stratified K-fold (5 splits) for reproducible evaluation

**Output:** List of dicts with `{dataset, model, mean_acc, std_acc}`

---

### 3. `src/evaluator.py`

**Function:** `compute_classification_metrics(y_true, y_pred, y_pred_proba)`

Computes classification evaluation metrics:
- Accuracy, Precision (weighted), Recall (weighted), F1-score (weighted)
- ROC-AUC (binary classification only)
- Composite score: mean of non-zero metric scores

**Function:** `compute_regression_metrics(y_true, y_pred)`

Computes regression evaluation metrics:
- MAE, RMSE, R²
- Normalized variants (NMAE, NRMSE) clipped to [0, 1]
- Composite score: mean of normalized metrics

---

## Usage

### 1. Run Full Pipeline (Meta-features + Baselines)

```bash
python run_pipeline.py
```

**Interactive Flow:**
1. Lists all CSV files in `data/raw/`
2. User selects dataset number
3. User enters target column name
4. System computes meta-features → saves to `results/meta_features.csv`
5. System runs 5-fold CV on baseline models → saves to `results/baseline_results.csv`

**Output Files:**
- `results/meta_features.csv` - One row per dataset with 7 meta-features
- `results/baseline_results.csv` - One row per (dataset, model) pair

---

### 2. Compare Training Set Size Impact

```bash
python compare_train_size.py
```

**Purpose:** Measure model sensitivity to training data volume

**Setup:**
- Baseline: 85% train, 15% test
- Small data: 15% train, 85% test

**Comparison Metrics:**
- `baseline_score` - Accuracy with 85% training
- `small_train_score` - Accuracy with 15% training
- `score_drop` - Absolute difference (baseline - small)
- `drop_percent` - Relative drop ((drop / baseline) × 100%)

**Output:** `results/test_results/train_size_comparison.csv`

---

### 3. Test: Baseline Comparison (Standalone)

```bash
python test_baseline_comparison.py
```

**Purpose:** Validate cross-validation estimates against held-out test set

**Setup:**
- 85% train → used for 5-fold CV
- 15% test → held-out, no data leakage

**Comparison:** CV accuracy vs Test set accuracy for each model

**Output:** `results/test_results/baseline_test_comparison.csv`

---

### 4. Test: Small Data Impact (Standalone)

```bash
python test_small_data_impact.py
```

**Purpose:** Evaluate model performance degradation with limited training data

**Setup:** Train on 15%, test on 85% (reverse of normal)

**Metrics:** Same as baseline (accuracy, precision, recall, F1)

**Output:** `results/test_results/small_data_comparison.csv`

---

## Data Requirements

**Input Format:**
- CSV files in `data/raw/`
- First row contains column headers
- One column must be designated as target (y)
- Remaining columns are features (X)

**Data Handling:**
- Categorical features → Label encoded
- Numeric features → Used as-is
- Missing values → Filled with 0

**Task Detection:**
- ≤20 unique target values → Classification
- >20 unique target values → Regression

---

## Configuration & Hyperparameters

**Cross-Validation:**
- Stratified K-Fold: 5 splits, shuffle=True, random_state=42

**Baseline Models (Classification):**
```python
LogisticRegression(max_iter=2000, random_state=42, solver='lbfgs')
DecisionTreeClassifier(max_depth=10, random_state=42)
RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
GaussianNB()
```

**Baseline Models (Regression):**
```python
LinearRegression()
DecisionTreeRegressor(max_depth=10, random_state=42)
RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
```

**Train/Test Splits:**
- Baseline: 85% train, 15% test
- Small data test: 15% train, 85% test

---

## Output Files

### `meta_features.csv`
Columns: `n_samples, n_features, missing_ratio, avg_variance, avg_abs_correlation, class_entropy, imbalance_ratio, dataset`

### `baseline_results.csv`
Columns: `dataset, model, mean_acc, std_acc`

### `train_size_comparison.csv`
Columns: `dataset, model, baseline_score, small_train_score, score_drop, drop_percent`

### `baseline_test_comparison.csv`
Columns: `dataset, model, cv_mean, cv_std, test_accuracy, difference`

### `small_data_comparison.csv`
Columns: `dataset, model, accuracy, precision, recall, f1, composite_score`

---

## Dependencies

**Required Packages:**
```
pandas>=1.0
numpy>=1.19
scikit-learn>=0.24
```

**Installation:**
```bash
pip install pandas numpy scikit-learn
```

---

## Key Design Decisions

1. **Label Encoding** - Simple, handles mixed categorical/numeric features
2. **Stratified Split** - Preserves class distribution in classification tasks
3. **5-fold CV** - Balances computational cost with variance reduction
4. **Composite Scores** - Allows comparing classification and regression on same scale
5. **Fixed Random State** - Ensures reproducibility across runs
6. **NaN Handling** - Filled with 0 (simple baseline; consider imputation for production)

---

## How to Rebuild the System

1. **Clone/setup files:**
   - Create `data/raw/` directory
   - Place CSV datasets in `data/raw/`
   - Verify `src/` module files exist

2. **Install dependencies:**
   ```bash
   pip install pandas numpy scikit-learn
   ```

3. **Run main pipeline:**
   ```bash
   python run_pipeline.py
   ```
   - Select dataset
   - Enter target column
   - Generates meta-features and baseline results

4. **(Optional) Run analysis scripts:**
   ```bash
   python compare_train_size.py      # Training size sensitivity
   python test_baseline_comparison.py # Validation test
   python test_small_data_impact.py   # Small data analysis
   ```

5. **Review outputs** in `results/` directory

---

## Notes

- **Classification detection:** Targets with ≤20 unique values treated as classification
- **Meta-features:** Only 2 classes needed for imbalance_ratio; None otherwise
- **Regression support:** Partial (baselines.py, evaluator.py); main pipeline classification-focused
- **Errors:** Models with errors are skipped with messages; execution continues
- **Random seed:** Always 42 for reproducibility

---

## System Workflow Diagram

```
data/raw/*.csv
      ↓
[run_pipeline.py]
      ├→ [meta_features.py] → results/meta_features.csv
      └→ [baselines.py] → results/baseline_results.csv
            ↓
[compare_train_size.py] (uses baseline results)
      └→ results/test_results/train_size_comparison.csv

[test_baseline_comparison.py] (standalone test)
      └→ results/test_results/baseline_test_comparison.csv

[test_small_data_impact.py] (standalone test)
      └→ results/test_results/small_data_comparison.csv
```

---

## Author Notes

This is a meta-learning dataset analysis system designed to:
- Profile dataset characteristics via meta-features
- Establish baseline model performance expectations
- Evaluate model sensitivity to training data volume
- Support AutoML algorithm selection strategies

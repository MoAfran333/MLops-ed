# ML Dataset Analysis System - AI Rebuild Specification

**Purpose:** Complete technical specification for AI to rebuild system from scratch.

---

## 1. Module Structure & Dependencies

### Directory Layout
```
project_ml/
├── src/
│   ├── __init__.py (empty)
│   ├── meta_features.py
│   ├── baselines.py
│   └── evaluator.py
├── data/raw/          (empty, user uploads CSVs)
├── results/
│   ├── meta_features.csv
│   ├── baseline_results.csv
│   └── test_results/  (auto-created)
├── run_pipeline.py
├── compare_train_size.py
├── test_baseline_comparison.py
├── test_small_data_impact.py
└── README.md
```

### Dependency Graph
```
run_pipeline.py
  ├─→ src/meta_features.py (compute_meta_features)
  ├─→ src/baselines.py (run_baselines, prepare_data)
  └─→ src/evaluator.py (not used in main pipeline)

compare_train_size.py
  ├─→ src/evaluator.py (compute_classification_metrics, compute_regression_metrics)
  ├─→ src/baselines.py (prepare_data)
  └─→ local functions (compute_baseline, run_train_size_test)

test_baseline_comparison.py (standalone, no imports from src)
test_small_data_impact.py (standalone, no imports from src)
```

### Required Imports (All Scripts)
```python
import warnings

warnings.filterwarnings("ignore")

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from pandas.api.types import is_numeric_dtype
```

---

## 2. Core Function Specifications

### 2.1 `src/meta_features.py`

#### `compute_meta_features(df: pd.DataFrame, target_col: Optional[str] = None) -> Dict[str, Optional[float]]`

**Purpose:** Extract 7 statistical characteristics from dataset

**Input:**
- `df` - Pandas DataFrame with mixed dtypes
- `target_col` - Column name to use as target (optional)

**Output:** Dictionary with exact keys:
```python
{
    "n_samples": int,  # len(df)
    "n_features": int,  # number of feature columns (excluding target)
    "missing_ratio": float,  # NaN count / total cells, in [0, 1]
    "avg_variance": float
    or None,  # mean variance of numeric features (None if no numeric)
    "avg_abs_correlation": float
    or None,  # mean |correlation with target| (None if regression/no correlation)
    "class_entropy": float
    or None,  # Shannon entropy of target distribution (None if regression)
    "imbalance_ratio": float
    or None,  # max_class_count / min_class_count (None if regression)
}
```

**Algorithm:**

```
1. Validate: df must be pd.DataFrame, else raise ValueError

2. Count samples & features
   n_samples = len(df)
   feature_cols = all columns except target_col (if provided)
   n_features = len(feature_cols)

3. Compute missing_ratio
   total_cells = n_samples * max(n_features, 1)
   missing_ratio = (number of NaN values in feature_cols) / total_cells
   
4. Compute avg_variance (numeric features only)
   numeric_features = columns in feature_cols with dtype in [int, float, int64, float64]
   IF no numeric features:
       avg_variance = None
   ELSE:
       variances = [var(col) for col in numeric_features]  # ddof=0, skipna=True
       avg_variance = mean(variances) or 0.0 if empty

5. Compute avg_abs_correlation (only if target_col provided)
   IF target_col not in df OR no numeric_features:
       avg_abs_correlation = None
   ELSE:
       target_series = df[target_col] (drop NaN)
       
       IF target_series dtype is object (categorical):
           treat_as_classification = True
           encoded_target = pd.factorize(df[target_col])[0]  # [0] is codes
       ELSE:
           nunique = target_series.nunique()
           IF nunique <= 20:
               treat_as_classification = True
               encoded_target = pd.factorize(df[target_col])[0]
           ELSE:
               treat_as_classification = False
               encoded_target = df[target_col].astype(float)
       
       FOR each numeric_feature in numeric_features:
           merged = concat([feature, encoded_target]) → drop NaN rows
           IF merged has <= 1 row: skip
           corr = pearson_correlation(feature, encoded_target)
           IF corr is NaN: skip
           abs_corrs.append(abs(corr))
       
       avg_abs_correlation = mean(abs_corrs) or None if empty

6. Compute class_entropy (only if target_col provided)
   IF target_col not in df:
       class_entropy = None
   ELSE:
       target_series = df[target_col] (drop NaN)
       IF target_series dtype is object:
           is_classification = True
       ELSE:
           nunique = target_series.nunique()
           is_classification = (nunique <= 20)
       
       IF is_classification:
           counts = value_counts(target_series)
           probs = counts / sum(counts)
           class_entropy = -sum(probs * log2(probs))
       ELSE:
           class_entropy = None

7. Compute imbalance_ratio (classification only)
   IF is_classification:
       counts = value_counts(target_series)
       imbalance_ratio = max(counts) / min(counts)
       IF min(counts) == 0: imbalance_ratio = None
   ELSE:
       imbalance_ratio = None

8. Return dict with all 7 keys
```

**Edge Cases:**
- `target_col is None` → set all target-dependent metrics to None
- No numeric features → `avg_variance = None`
- All NaN in target → skip computation for that metric
- Single-value column → variance = 0.0
- All same class → entropy = 0.0

---

### 2.2 `src/baselines.py`

#### `prepare_data(df: pd.DataFrame, target_col: str) -> Tuple[pd.DataFrame, pd.Series]`

**Purpose:** Preprocess data for modeling (encoding + NaN handling)

**Input:**
- `df` - Raw DataFrame
- `target_col` - Target column name

**Output:**
- `X` - Feature matrix (numeric only, NaN filled with 0)
- `y` - Target vector (numeric, encoded if categorical)

**Algorithm:**

```
1. Separate target and features
   X = df.drop(columns=[target_col])
   y = df[target_col]

2. Encode target if categorical
   IF y.dtype == 'object':
       le = LabelEncoder()
       y = le.fit_transform(y)

3. Encode all categorical features in X
   FOR each column in X.columns:
       IF X[column].dtype == 'object':
           le = LabelEncoder()
           X[column] = le.fit_transform(X[column].astype(str))

4. Fill remaining NaN with 0
   X = X.fillna(0)

5. Return (X, y)
```

**Data Types:**
- Input X: DataFrame with mixed dtypes (object, int, float)
- Input y: Series with mixed dtypes (object, int, float)
- Output X: DataFrame with numeric dtypes only (int64, float64)
- Output y: Series with int64 dtype (if was categorical) or original numeric

---

#### `run_baselines(df: pd.DataFrame, dataset_name: str, target_col: str) -> List[Dict]`

**Purpose:** Train baseline models with 5-fold cross-validation

**Input:**
- `df` - Dataset
- `dataset_name` - Dataset filename (for logging)
- `target_col` - Target column name

**Output:** List of dicts, each with keys:
```python
{
    "dataset": str,  # dataset_name
    "model": str,  # model name (e.g., "LogisticRegression")
    "mean_acc": float,  # cross-validation mean accuracy
    "std_acc": float,  # cross-validation std accuracy
}
```

**Algorithm:**

```
1. Preprocess
   X, y = prepare_data(df, target_col)
   Print: X.shape, y.shape, unique classes

2. Create 5 baseline models
   models = {
       "LinearRegression": LogisticRegression(max_iter=1000, random_state=42, solver='lbfgs'),
       "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
       "DecisionTree": DecisionTreeClassifier(max_depth=10, random_state=42),
       "RandomForest": RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42),
       "GaussianNB": GaussianNB(),
   }

3. Setup cross-validation
   cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

4. Train each model
   results = []
   FOR each (model_name, model) in models:
       TRY:
           scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
           mean_acc = scores.mean()
           std_acc = scores.std()
           results.append({
               "dataset": dataset_name,
               "model": model_name,
               "mean_acc": mean_acc,
               "std_acc": std_acc,
           })
       EXCEPT Exception as e:
           print(f"Error in {model_name}: {e}")
           continue

5. Return results list
```

**Fixed Hyperparameters:**
```python
LogisticRegression: max_iter=1000, random_state=42, solver='lbfgs'
DecisionTreeClassifier: max_depth=10, random_state=42
RandomForestClassifier: n_estimators=50, max_depth=10, random_state=42
GaussianNB: (no hyperparams)
StratifiedKFold: n_splits=5, shuffle=True, random_state=42
```

---

### 2.3 `src/evaluator.py`

#### `compute_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_pred_proba: Optional[np.ndarray] = None) -> Dict[str, float]`

**Purpose:** Compute classification metrics

**Input:**
- `y_true` - Ground truth labels (1D array)
- `y_pred` - Predicted labels (1D array)
- `y_pred_proba` - Predicted probabilities (2D array, optional)

**Output:** Dict with keys:
```python
{
    "accuracy": float,  # [0, 1]
    "precision": float,  # weighted average, [0, 1]
    "recall": float,  # weighted average, [0, 1]
    "f1": float,  # weighted average, [0, 1]
    "roc_auc": float or None,  # binary only, [0, 1]
    "composite_score": float,  # mean of accuracy, precision, recall, f1
}
```

**Algorithm:**

```
1. Calculate main metrics
   accuracy = accuracy_score(y_true, y_pred)
   precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
   recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
   f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

2. Calculate ROC-AUC (binary classification only)
   IF len(unique(y_true)) == 2 AND y_pred_proba is not None:
       roc_auc = roc_auc_score(y_true, y_pred_proba[:, 1])
   ELSE:
       roc_auc = None

3. Calculate composite score
   scores = [accuracy, precision, recall, f1]
   composite_score = mean(scores)  # all non-zero

4. Return dict
```

**Error Handling:**
- Wrap each metric calculation in TRY/EXCEPT
- On error, set metric to 0.0
- Continue with other metrics

---

#### `compute_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]`

**Purpose:** Compute regression metrics with normalization

**Input:**
- `y_true` - Ground truth values (1D array)
- `y_pred` - Predicted values (1D array)

**Output:** Dict with keys:
```python
{
    "mae": float,  # mean absolute error
    "rmse": float,  # root mean squared error
    "r2": float,  # [0, 1] (clipped)
    "nmae": float,  # normalized MAE, [0, 1]
    "nrmse": float,  # normalized RMSE, [0, 1]
    "composite_score": float,  # mean of nmae, nrmse, (r2+1)/2
}
```

**Algorithm:**

```
1. Calculate raw metrics
   mae = mean_absolute_error(y_true, y_pred)
   mse = mean_squared_error(y_true, y_pred)
   rmse = sqrt(mse)
   r2 = r2_score(y_true, y_pred)

2. Normalize
   y_range = max(y_true) - min(y_true)
   
   IF y_range > 0:
       nmae = 1.0 - (mae / y_range)
       nrmse = 1.0 - (rmse / y_range)
   ELSE:
       nmae = 0.0
       nrmse = 0.0
   
   r2_clipped = clip(r2, 0, 1)

3. Calculate composite score
   scores = [nmae, nrmse, (r2_clipped + 1) / 2]
   composite_score = mean(s for s in scores if 0 <= s <= 1)

4. Return dict
```

**Clipping Logic:**
- All normalized metrics clipped to [0, 1]
- Composite score only includes values in [0, 1]

---

## 3. Main Pipeline Scripts

### 3.1 `run_pipeline.py`

**Purpose:** Main entry point - compute meta-features + run baselines

**Flow:**

```
1. List all .csv files in data/raw/
2. Print numbered list
3. USER INPUT: select dataset number
4. USER INPUT: enter target column name
5. Load CSV with pd.read_csv()
6. COMPUTE: meta_features = compute_meta_features(df, target_col)
   - Add "dataset" key with filename
   - Print all meta-features
   - Save to results/meta_features.csv
7. COMPUTE: baseline_results = run_baselines(df, filename, target_col)
   - Print each model's scores
   - Save to results/baseline_results.csv
8. Print completion message
```

**Output Files:**
- `results/meta_features.csv` - one row, append if exists
- `results/baseline_results.csv` - multiple rows, append if exists

**Paths:**
```python
DATA_DIR = Path(__file__).parent / "data" / "raw"
RESULTS_DIR = Path(__file__).parent / "results"
```

---

### 3.2 `compare_train_size.py`

**Purpose:** Compare model performance at 85% train size vs 15% train size

**Flow:**

```
1. USER INPUT: select dataset(s) - comma separated (e.g., "1,2" or "1")
2. USER INPUT: for each dataset, enter target column
3. FOR each dataset:
   a. Load CSV
   b. COMPUTE baseline (85% train):
      - Split: 85% train, 15% test (stratified)
      - Train all models
      - Evaluate on test set
      - Store scores in baseline_results dict
   c. COMPUTE small train (15% train):
      - Split: 15% train, 85% test (stratified)
      - Train all models
      - Evaluate on test set
      - Store scores
   d. COMPARE:
      - score_drop = baseline_score - small_train_score
      - drop_percent = (score_drop / baseline_score) * 100
   e. Append results to all_results list
4. Save all_results to results/test_results/train_size_comparison.csv
5. Print summary table by dataset
```

**Key Functions:**

#### `prepare_data(df, target_col) -> Tuple[DataFrame, Series]`
Same as in baselines.py - reimplement locally

#### `compute_baseline(df, dataset_name, target_col) -> Tuple[Dict, bool]`
```
Split: 85% train, 15% test (stratified if <= 20 classes)
Train all models
Return: (scores_dict, is_classification boolean)
```

#### `run_train_size_test(df, dataset_name, target_col, baseline_results, is_classification) -> List[Dict]`
```
Split: 15% train, 85% test (stratified if classification)
Train all models
Compare vs baseline_results
Return: list of {dataset, model, baseline_score, small_train_score, score_drop, drop_percent}
```

**Task Detection:**
```python
n_unique_classes = len(np.unique(y))
is_classification = n_unique_classes <= 20
```

**Models to Train:**

If classification:
```python
{
    "LinearRegression": LogisticRegression(...),  # note: misnamed in original
    "LogisticRegression": LogisticRegression(...),
    "DecisionTree": DecisionTreeClassifier(...),
    "RandomForest": RandomForestClassifier(...),
    "GaussianNB": GaussianNB(),
}
```

If regression:
```python
{
    "LinearRegression": LinearRegression(),
    "DecisionTree": DecisionTreeRegressor(...),
    "RandomForest": RandomForestRegressor(...),
}
```

**Output CSV Schema:**
```
dataset, model, baseline_score, small_train_score, score_drop, drop_percent
```

---

### 3.3 `test_baseline_comparison.py`

**Purpose:** Validate 5-fold CV accuracy vs held-out test accuracy (standalone test)

**Flow:**

```
1. USER INPUT: select dataset(s)
2. USER INPUT: for each dataset, enter target_col
3. FOR each dataset:
   a. Load CSV
   b. prepare_data(df, target_col) → X, y
   c. Train/Test split: 85% train, 15% test (stratified)
   d. FOR each model:
      - Run 5-fold CV on 85% train data
      - Calculate cross-validation scores (mean, std)
      - Train on full 85% train, test on 15% test data
      - Calculate test accuracy
      - Compare: difference = cv_mean - test_accuracy
   e. Append results
4. Save to results/test_results/baseline_test_comparison.csv
5. Print comparison table
```

**Output CSV Schema:**
```
dataset, model, cv_mean, cv_std, test_accuracy, difference
```

---

### 3.4 `test_small_data_impact.py`

**Purpose:** Evaluate performance degradation with small training set (standalone test)

**Flow:**

```
1. USER INPUT: select dataset(s)
2. USER INPUT: for each dataset, enter target_col
3. FOR each dataset:
   a. Load CSV
   b. prepare_data(df, target_col) → X, y
   c. Train/Test split: 15% train, 85% test (reversed from baseline) (stratified)
   d. FOR each model:
      - Train on 15% training data
      - Evaluate on 85% test data
      - Compute metrics (accuracy, precision, recall, f1, composite_score)
   e. Append results
4. Save to results/test_results/small_data_comparison.csv
5. Print results table
```

**Output CSV Schema:**
```
dataset, model, accuracy, precision, recall, f1, composite_score
```

---

## 4. Data Types & Schemas

### Input: CSV Files in `data/raw/`

```
Example: adult.csv
┌──────────┬──────┬──────────┬─────────┐
│ age      │ fnlwgt │ education │ target  │
├──────────┼──────┼──────────┼─────────┤
│ 39       │ 77516 │ Bachelors │ <=50K   │
│ 50       │ 83311 │ Bachelors │ <=50K   │
│ NaN      │ 12345 │ HS-grad  │ >50K    │
└──────────┴──────┴──────────┴─────────┘

- Column types: mixed (int, float, object/string, NaN)
- First row: header
- Any column can be target (user specifies)
```

### Output: `meta_features.csv`

```
n_samples, n_features, missing_ratio, avg_variance, avg_abs_correlation, class_entropy, imbalance_ratio, dataset
1000, 14, 0.05, 125.3, 0.42, 0.95, 2.5, adult.csv
2000, 13, 0.02, 45.1, 0.38, None, None, Housing.csv
```

### Output: `baseline_results.csv`

```
dataset, model, mean_acc, std_acc
adult.csv, LogisticRegression, 0.8234, 0.0125
adult.csv, DecisionTree, 0.7932, 0.0234
adult.csv, RandomForest, 0.8412, 0.0098
Housing.csv, LinearRegression, 0.6543, 0.0432
```

### Output: `train_size_comparison.csv`

```
dataset, model, baseline_score, small_train_score, score_drop, drop_percent
adult.csv, LogisticRegression, 0.8234, 0.6543, 0.1691, 20.54
adult.csv, DecisionTree, 0.7932, 0.5123, 0.2809, 35.41
```

---

## 5. Constants & Configuration

### All Random States
```python
random_state = 42  # everywhere
```

### Cross-Validation
```python
StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
```

### Train/Test Splits
```python
# Baseline evaluation
train_size = 0.85, test_size = 0.15
stratify = y if classification else None

# Small data evaluation
train_size = 0.15, test_size = 0.85
stratify = y if classification else None
```

### Scikit-Learn Model Hyperparameters

```python
# Classification
LogisticRegression(max_iter=1000, random_state=42, solver="lbfgs")
DecisionTreeClassifier(max_depth=10, random_state=42)
RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
GaussianNB()

# Regression
LinearRegression()
DecisionTreeRegressor(max_depth=10, random_state=42)
RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
```

### Metric Calculations

```python
# Classification - weighted averages
precision_score(..., average="weighted", zero_division=0)
recall_score(..., average="weighted", zero_division=0)
f1_score(..., average="weighted", zero_division=0)

# Regression - normalization
nmae = 1.0 - (mae / y_range)
nrmse = 1.0 - (rmse / y_range)
r2_norm = clip(r2, 0, 1)
```

---

## 6. Error Handling Strategy

### Level 1: Model Training Errors
```python
try:
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
except Exception as e:
    print(f"Error training {model_name}: {e}")
    continue  # skip this model, continue with others
```

### Level 2: Metric Calculation Errors
```python
try:
    precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)
except:
    precision = 0.0  # default fallback
```

### Level 3: Missing Data
```python
# NaN handling
X.fillna(0)  # global strategy

# Missing target
if target_col not in df.columns:
    raise ValueError(f"Target column {target_col} not found")
```

### Level 4: Edge Cases
```python
# Empty correlation list
if len(abs_corrs) == 0:
    avg_abs_correlation = None

# Zero variance
if y_range == 0:
    nmae = 0.0
    nrmse = 0.0
```

---

## 7. Interactive Input Validation

### Dataset Selection
```
IF user enters non-integer:
    print("Invalid input. Enter a number.")
    repeat

IF user enters out-of-range number:
    print(f"Please enter 1-{num_datasets}")
    repeat
```

### Target Column Input
```
USER enters target column name
IF target_col not in df.columns:
    # Proceed anyway - let compute_meta_features/prepare_data handle it
    # OR print warning: "Warning: {target_col} not found in columns"

IF target_col is empty string:
    # Optional: skip that dataset or use default column
```

---

## 8. Code Quality Requirements

### Imports Organization
```python
# 1. Standard library
import warnings, sys
from pathlib import Path

# 2. Third-party
import numpy as np
import pandas as pd

# 3. Scikit-learn
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, ...

# 4. Local imports (only in main scripts)
sys.path.insert(0, str(Path(__file__).parent / "src"))
from meta_features import compute_meta_features
```

### Logging/Output
```python
print("=" * 70)
print("MAIN TITLE")
print("=" * 70)
print(f"\n  {key:<30} {value:.6f}")  # aligned output
```

### File Writing
```python
results_df = pd.DataFrame(results_list)
csv_path = RESULTS_DIR / "output.csv"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
results_df.to_csv(csv_path, index=False)
```

---

## 9. Important Notes for AI Reconstruction

1. **prepare_data is duplicated** - appears in both baselines.py and compare_train_size.py. Implement separately in each (or import from baselines in compare_train_size).

2. **"LinearRegression" is misnamed** - in classification models dict, "LinearRegression" key maps to LogisticRegression. Keep this quirk for compatibility.

3. **Task Detection:** ≤20 unique classes = Classification, else Regression

4. **Metric Averaging:** weighted averages for multi-class, binary ROC-AUC only when available

5. **Composite Scores:** arithmetic mean of all positive/valid component metrics

6. **Encoding Order:** Target first, then features (both use LabelEncoder, not OneHotEncoder)

7. **NaN Strategy:** Simple fillna(0) - not imputation

8. **Path Construction:** Always use Path(__file__).parent, never hardcoded paths

9. **CSV Append Mode:** Use append mode for results (a), or load existing + concat + write

10. **No Train/Test Leakage:** Stratification always used in splits, encoders fit separately per fold

---

## 10. Testing Checklist

- [ ] Meta-features computed for 6 datasets
- [ ] Baseline results saved (30 rows: 6 datasets × 5 models)
- [ ] Train size comparison runs (multiple datasets)
- [ ] Small data test isolates performance degradation
- [ ] Baseline comparison validates CV vs test correlation
- [ ] CSV outputs have correct schemas
- [ ] Edge cases (NaN, single class, missing column) handled gracefully
- [ ] Random seed 42 ensures reproducibility
- [ ] All paths relative (Path(__file__).parent)

---

**END OF REBUILD SPECIFICATION**

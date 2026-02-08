import math
from typing import Optional, Dict

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype


def compute_meta_features(df: pd.DataFrame, target_col: Optional[str] = None) -> Dict[str, Optional[float]]:
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("only pandas DF is allowed !!!!!!!!!!!!!!!!!!!!!!!")

    n_samples = int(len(df))

    cols = list(df.columns)
    if target_col is not None and target_col in cols:
        feature_cols = [c for c in cols if c != target_col]
    else:
        feature_cols = cols.copy()

    n_features = int(len(feature_cols))
    total_cells = max(n_samples * max(n_features, 1), 1)
    missing_ratio = float(df[feature_cols].isna().sum().sum()) / total_cells if n_features > 0 else 0.0
    if n_features > 0:
        numeric_features = df[feature_cols].select_dtypes(include=[np.number]).columns.tolist()
    else:
        numeric_features = []

        " avg over top featue , may be numeric ig , dont change "
    if len(numeric_features) == 0:
        avg_variance = None
    else:
        variances = df[numeric_features].var(ddof=0, skipna=True)
        variances = variances.dropna()
        avg_variance = float(variances.mean()) if not variances.empty else 0.0
    avg_abs_correlation = None
    if target_col is not None and target_col in df.columns and len(numeric_features) > 0:
        target_series = df[target_col].dropna()

        treat_as_classification = False
        if not is_numeric_dtype(target_series):
            treat_as_classification = True
            encoded_target = pd.factorize(df[target_col])[0]
        else:
            nunique = int(target_series.nunique())
            if nunique <= 20:
                treat_as_classification = True
                encoded_target = pd.factorize(df[target_col])[0]
            else:
                encoded_target = df[target_col].astype(float).values

        abs_corrs = []
        for col in numeric_features:
            feat = df[col]
            paired = pd.concat([feat, pd.Series(encoded_target, index=df.index, name="_tgt")], axis=1).dropna()
            if paired.shape[0] <= 1:
                continue
            corr = paired.iloc[:, 0].corr(paired["_tgt"])
            if pd.isna(corr):
                continue
            abs_corrs.append(abs(float(corr)))

        if len(abs_corrs) == 0:
            avg_abs_correlation = None
        else:
            avg_abs_correlation = float(np.mean(abs_corrs))

    class_entropy = None
    imbalance_ratio = None
    if target_col is not None and target_col in df.columns:
        tgt = df[target_col].dropna()
        if not tgt.empty:
            is_target_numeric = is_numeric_dtype(tgt)
            if (not is_target_numeric) or (tgt.nunique() <= 20):
                counts = tgt.value_counts()
                probs = counts / counts.sum()
                class_entropy = float(-(probs * np.log2(probs)).sum()) if not probs.empty else None
                if counts.min() == 0:
                    imbalance_ratio = None
                else:
                    imbalance_ratio = float(counts.max() / counts.min())
            else:
                class_entropy = None
                imbalance_ratio = None

    return {
        "n_samples": n_samples,
        "n_features": n_features,
        "missing_ratio": missing_ratio,
        "avg_variance": avg_variance,
        "avg_abs_correlation": avg_abs_correlation,
        "class_entropy": class_entropy,
        "imbalance_ratio": imbalance_ratio,
    }
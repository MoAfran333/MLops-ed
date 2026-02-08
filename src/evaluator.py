import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_absolute_error, mean_squared_error, r2_score
)

def compute_classification_metrics(y_true, y_pred, y_pred_proba=None):

    metrics = {}
    
    metrics['accuracy'] = accuracy_score(y_true, y_pred)
    
    try:
        metrics['precision'] = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    except:
        metrics['precision'] = 0.0
    
    try:
        metrics['recall'] = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    except:
        metrics['recall'] = 0.0
    
    try:
        metrics['f1'] = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    except:
        metrics['f1'] = 0.0
    

    try:
        if len(np.unique(y_true)) == 2 and y_pred_proba is not None:
            metrics['roc_auc'] = roc_auc_score(y_true, y_pred_proba[:, 1])
        else:
            metrics['roc_auc'] = None
    except:
        metrics['roc_auc'] = None
    
    scores = [metrics['accuracy'], metrics['precision'], metrics['recall'], metrics['f1']]
    metrics['composite_score'] = np.mean([s for s in scores if s > 0])
    
    return metrics


def compute_regression_metrics(y_true, y_pred):

    metrics = {}

    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)

    y_range = np.max(y_true) - np.min(y_true)
    
    if y_range > 0:
        nmae = 1.0 - (mae / y_range)
        metrics['nmae'] = max(0, min(1, nmae))                  # Clip to [0, 1]
        nrmse = 1.0 - (rmse / y_range)
        metrics['nrmse'] = max(0, min(1, nrmse))
    else:
        metrics['nmae'] = 0.0
        metrics['nrmse'] = 0.0
    
    metrics['r2'] = max(0, min(1, r2))                  # Clip to [0, 1]
    metrics['mae'] = mae
    metrics['rmse'] = rmse
    

    scores = [metrics['nmae'], metrics['nrmse'], (metrics['r2'] + 1) / 2]  # + or - 
    metrics['composite_score'] = np.mean([s for s in scores if 0 <= s <= 1])
    
    return metrics


def print_metrics(metrics, metric_type='classification'):
    
    if metric_type == 'classification':
        print(f"  Accuracy:        {metrics['accuracy']:.4f}")
        print(f"  Precision:       {metrics['precision']:.4f}")
        print(f"  Recall:          {metrics['recall']:.4f}")
        print(f"  F1-Score:        {metrics['f1']:.4f}")
        if metrics['roc_auc'] is not None:
            print(f"  ROC-AUC:         {metrics['roc_auc']:.4f}")
        print(f"  Composite Score: {metrics['composite_score']:.4f}")
    
    elif metric_type == 'regression':
        print(f"  NMAE (0-1):      {metrics['nmae']:.4f}")
        print(f"  NRMSE (0-1):     {metrics['nrmse']:.4f}")
        print(f"  R² Score:        {metrics['r2']:.4f}")
        print(f"  MAE (raw):       {metrics['mae']:.4f}")
        print(f"  RMSE (raw):      {metrics['rmse']:.4f}")
        print(f"  Composite Score: {metrics['composite_score']:.4f}")

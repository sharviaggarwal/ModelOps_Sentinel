
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)


def monitor_model_performance(
    y_true,
    y_pred,
    y_prob
):
    accuracy = accuracy_score(y_true, y_pred)

    precision = precision_score(
        y_true, y_pred, zero_division=0
    )

    recall = recall_score(
        y_true, y_pred, zero_division=0
    )

    f1 = f1_score(
        y_true, y_pred, zero_division=0
    )

    roc_auc = roc_auc_score(y_true, y_prob)

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1]
    )

    return {
        "total_samples": int(len(y_true)),
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "roc_auc": float(roc_auc),
        "confusion_matrix": {
            "true_negative": int(matrix[0][0]),
            "false_positive": int(matrix[0][1]),
            "false_negative": int(matrix[1][0]),
            "true_positive": int(matrix[1][1])
        }
    }

def detect_performance_degradation(
    current_metrics,
    baseline_metrics,
    warning_threshold=0.02,
    moderate_threshold=0.05,
    high_threshold=0.10,
    critical_threshold=0.20
):
    monitored_metrics = [
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "roc_auc"
    ]

    results = []

    for metric in monitored_metrics:
        baseline = baseline_metrics[metric]
        current = current_metrics[metric]

        # Positive value means performance has dropped
        degradation = baseline - current

        if degradation <= 0:
            severity = "None"
            status = "No Degradation"

        elif degradation < warning_threshold:
            severity = "Low"
            status = "Minor Degradation"

        elif degradation < moderate_threshold:
            severity = "Moderate"
            status = "Warning"

        elif degradation < high_threshold:
            severity = "High"
            status = "High Degradation"

        elif degradation < critical_threshold:
            severity = "Critical"
            status = "Critical Degradation"

        else:
            severity = "Critical"
            status = "Critical Degradation"

        results.append({
            "Metric": metric,
            "Baseline": float(baseline),
            "Current": float(current),
            "Degradation": float(degradation),
            "Severity": severity,
            "Status": status
        })

    return results

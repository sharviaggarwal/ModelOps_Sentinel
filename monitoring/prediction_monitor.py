
import numpy as np
from scipy.stats import chi2_contingency, ks_2samp


def monitor_prediction_distribution(
    model,
    reference_df,
    production_df
):
    # Generate predictions for both datasets
    reference_predictions = model.predict(reference_df)
    production_predictions = model.predict(production_df)

    # Generate churn probabilities
    reference_probabilities = model.predict_proba(reference_df)[:, 1]
    production_probabilities = model.predict_proba(production_df)[:, 1]

    # Count Stay (0) and Churn (1) predictions
    reference_counts = np.bincount(
        reference_predictions.astype(int),
        minlength=2
    )

    production_counts = np.bincount(
        production_predictions.astype(int),
        minlength=2
    )

    # Compare prediction class distributions
    contingency_table = np.array([
        reference_counts,
        production_counts
    ])

    chi2, class_p_value, _, expected = chi2_contingency(
        contingency_table
    )

    # Compare probability distributions
    probability_result = ks_2samp(
        reference_probabilities,
        production_probabilities
    )

    # Calculate churn prediction rates
    reference_churn_rate = (
        reference_counts[1] / len(reference_predictions)
    )

    production_churn_rate = (
        production_counts[1] / len(production_predictions)
    )

    # Bonferroni correction for two statistical tests
    adjusted_threshold = 0.05 / 2

    class_drift = class_p_value < adjusted_threshold
    probability_drift = (
        probability_result.pvalue < adjusted_threshold
    )

    return {
        "reference": {
            "total_predictions": int(len(reference_predictions)),
            "stay_predictions": int(reference_counts[0]),
            "churn_predictions": int(reference_counts[1]),
            "churn_rate": float(reference_churn_rate)
        },
        "production": {
            "total_predictions": int(len(production_predictions)),
            "stay_predictions": int(production_counts[0]),
            "churn_predictions": int(production_counts[1]),
            "churn_rate": float(production_churn_rate)
        },
        "churn_rate_change_percentage_points": float(
            (production_churn_rate - reference_churn_rate) * 100
        ),
        "class_distribution": {
            "chi_square_statistic": float(chi2),
            "p_value": float(class_p_value),
            "drift_detected": bool(class_drift),
            "minimum_expected_count": float(expected.min())
        },
        "probability_distribution": {
            "ks_statistic": float(probability_result.statistic),
            "p_value": float(probability_result.pvalue),
            "drift_detected": bool(probability_drift)
        },
        "adjusted_threshold": adjusted_threshold
    }

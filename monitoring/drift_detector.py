
import pandas as pd
from scipy.stats import ks_2samp, chi2_contingency


def detect_data_drift(reference_df, production_df):

    numeric_columns = [
        "tenure",
        "MonthlyCharges",
        "TotalCharges"
    ]

    # -------------------------------
    # 1. INPUT VALIDATION
    # -------------------------------

    if reference_df.empty or production_df.empty:
        raise ValueError("Reference and production datasets cannot be empty.")

    missing_columns = set(reference_df.columns) - set(production_df.columns)

    if missing_columns:
        raise ValueError(
            f"Production data is missing columns: {missing_columns}"
        )

    if set(reference_df.columns) != set(production_df.columns):
        raise ValueError("Reference and production columns must match.")

    if reference_df.isnull().any().any():
        raise ValueError("Reference dataset contains missing values.")

    if production_df.isnull().any().any():
        raise ValueError("Production dataset contains missing values.")

    if len(reference_df) < 2 or len(production_df) < 2:
        raise ValueError("Both datasets must contain at least 2 records.")

    categorical_columns = [
        col for col in reference_df.columns
        if col not in numeric_columns
    ]

    drift_results = []

    # -------------------------------
    # 2. NUMERICAL DRIFT DETECTION
    # -------------------------------

    for column in numeric_columns:

        if column not in reference_df.columns:
            raise ValueError(f"Required numerical column missing: {column}")

        result = ks_2samp(
            reference_df[column],
            production_df[column]
        )

        # KS statistic itself measures distribution difference.
        effect_size = float(result.statistic)

        drift_results.append({
            "Feature": column,
            "Test": "KS Test",
            "Statistic": float(result.statistic),
            "P_Value": float(result.pvalue),
            "Effect_Size": effect_size,
            "Expected_Min": None,
            "Test_Validity": "Valid"
        })

    # -------------------------------
    # 3. CATEGORICAL DRIFT DETECTION
    # -------------------------------

    for column in categorical_columns:

        # Include categories found in either dataset.
        categories = sorted(
            set(reference_df[column].unique())
            | set(production_df[column].unique()),
            key=str
        )

        ref_counts = (
            reference_df[column]
            .value_counts()
            .reindex(categories, fill_value=0)
        )

        prod_counts = (
            production_df[column]
            .value_counts()
            .reindex(categories, fill_value=0)
        )

        contingency_table = pd.DataFrame({
            "Reference": ref_counts,
            "Production": prod_counts
        }).T

        # A test needs at least two categories.
        if len(categories) < 2:
            chi2 = 0.0
            p_value = 1.0
            expected_min = None
            effect_size = 0.0
            validity = "Not enough categories"

        else:
            chi2, p_value, dof, expected = chi2_contingency(
                contingency_table
            )

            expected_min = float(expected.min())

            # Cramer's V: effect size for categorical drift.
            total_count = contingency_table.values.sum()
            min_dimension = min(contingency_table.shape) - 1

            effect_size = (
                float((chi2 / (total_count * min_dimension)) ** 0.5)
                if total_count > 0 and min_dimension > 0
                else 0.0
            )

            validity = (
                "Valid"
                if expected_min >= 5
                else "Warning: expected count below 5"
            )

        drift_results.append({
            "Feature": column,
            "Test": "Chi-Square",
            "Statistic": float(chi2),
            "P_Value": float(p_value),
            "Effect_Size": effect_size,
            "Expected_Min": expected_min,
            "Test_Validity": validity
        })

    # -------------------------------
    # 4. UNIFIED REPORT
    # -------------------------------

    drift_report = pd.DataFrame(drift_results)

    drift_report = drift_report.astype(object).where(
    pd.notna(drift_report),
    None
)

    # Bonferroni correction for multiple tests.
    alpha = 0.05
    adjusted_threshold = alpha / len(drift_report)

    drift_report["Adjusted_Threshold"] = adjusted_threshold

    drift_report["Drift_Detected"] = (
        drift_report["P_Value"] < adjusted_threshold
    )

    def classify_severity(row):
        if not row["Drift_Detected"]:
            return "None"

        effect = row["Effect_Size"]

        if effect < 0.10:
            return "Low"
        elif effect < 0.20:
            return "Moderate"
        elif effect < 0.30:
            return "High"
        else:
            return "Critical"

    drift_report["Severity"] = drift_report.apply(
        classify_severity,
        axis=1
    )
    return drift_report


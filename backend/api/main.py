from monitoring.drift_detector import detect_data_drift
from fastapi.middleware.cors import CORSMiddleware
from langgraph.types import Command
from uuid import uuid4
from agent.investigator import app as investigator_graph
from monitoring.prediction_monitor import monitor_prediction_distribution
from monitoring.production_logger import log_production_data
from backend.database.connection import SessionLocal
from backend.database.models import (
    PredictionLog,
    MonitoringRun,
    Incident
)
from fastapi import FastAPI
from datetime import datetime, timezone
from fastapi import HTTPException
from backend.database.connection import SessionLocal
from pathlib import Path
import joblib
import pandas as pd

from backend.api.schemas import CustomerData


# Initialize FastAPI
app = FastAPI(
    title="ModelOps Sentinel",
    description="ML Model Monitoring and Investigation Platform",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {
        "message": "Welcome to ModelOps Sentinel",
        "status": "API is running",
        "docs": "/docs"
    }

# Locate saved model
PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "models" / "logistic_regression.pkl"

# Load model once when application starts
model = joblib.load(MODEL_PATH)


# Health endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "project": "ModelOps Sentinel"
    }


# Prediction endpoint
@app.post("/predict")
def predict_churn(customer: CustomerData):

    # Convert validated customer data into DataFrame
    customer_df = pd.DataFrame([customer.model_dump()])

    # Generate prediction
    prediction = int(model.predict(customer_df)[0])

    # Generate churn probability
    churn_probability = float(
        model.predict_proba(customer_df)[0][1]
    )

    # Convert prediction into readable output
    result = "Churn" if prediction == 1 else "Stay"
    log_production_data(customer.model_dump())
    db = SessionLocal()

    try:
        log = PredictionLog(
            customer_data=customer.model_dump(),
            prediction=result,
            churn_probability=churn_probability,
            model_name="Logistic Regression",
            model_version="1.0"
        )

        db.add(log)
        db.commit()
        db.refresh(log)

    finally:
        db.close()

    return {
        "prediction": result,
        "churn_probability": round(churn_probability, 4),
        "churn_percentage": round(churn_probability * 100, 2),
        "model_name": "Logistic Regression",
        "model_version": "1.0"
    }
@app.get("/monitor/drift")
def monitor_drift():

    reference_path = (
        PROJECT_ROOT / "data" / "processed" / "reference_data.csv"
    )

    production_path = (
        PROJECT_ROOT / "data" / "processed" / "simulated_production_data.csv"
    )

    reference_df = pd.read_csv(reference_path)
    production_df = pd.read_csv(production_path)

    drift_report = detect_data_drift(
        reference_df,
        production_df
    )

    severity_counts = drift_report["Severity"].value_counts()

    critical = int(severity_counts.get("Critical", 0))
    high = int(severity_counts.get("High", 0))
    moderate = int(severity_counts.get("Moderate", 0))
    low = int(severity_counts.get("Low", 0))
    no_drift = int(severity_counts.get("None", 0))

    if critical > 0:
        health_status = "CRITICAL"
    elif high > 0 or moderate > 0:
        health_status = "DEGRADED"
    elif low > 0:
        health_status = "WARNING"
    else:
        health_status = "HEALTHY"


    return {
        "model_name": "Logistic Regression",
        "model_version": "1.0",
        "overall_health": health_status,
        "total_features": len(drift_report),
        "drifted_features": int(
            drift_report["Drift_Detected"].sum()
        ),
        "severity_summary": {
            "critical": critical,
            "high": high,
            "moderate": moderate,
            "low": low,
            "no_drift": no_drift
        },
        "drift_report": drift_report.to_dict(
            orient="records"
        )
    }
@app.get("/monitor/predictions")
def monitor_predictions():

    reference_path = (
        PROJECT_ROOT / "data" / "processed" / "reference_data.csv"
    )

    production_path = (
        PROJECT_ROOT / "data" / "processed" / "simulated_production_data.csv"
    )

    reference_df = pd.read_csv(reference_path)
    production_df = pd.read_csv(production_path)

    prediction_report = monitor_prediction_distribution(
        model=model,
        reference_df=reference_df,
        production_df=production_df
    )

    return {
        "model_name": "Logistic Regression",
        "model_version": "1.0",
        "monitoring_status": (
            "DRIFT DETECTED"
            if (
                prediction_report["class_distribution"]["drift_detected"]
                or prediction_report["probability_distribution"]["drift_detected"]
            )
            else "HEALTHY"
        ),
        "prediction_monitoring": prediction_report
    }
from monitoring.performance_monitor import (
    monitor_model_performance,
    detect_performance_degradation
)


@app.get("/monitor/performance")
def monitor_performance():

    import json

    # 1. Load held-out test dataset
    test_path = (
        PROJECT_ROOT / "data" / "processed" / "test_data.csv"
    )

    test_df = pd.read_csv(test_path)

    # 2. Separate features and actual labels
    X_test_api = test_df.drop(columns=["Churn"])

    # Handle numeric labels (0, 1) and text labels (No, Yes)
    y_test_api = (
        test_df["Churn"]
        .astype(str)
        .str.strip()
        .replace({
            "No": "0",
            "Yes": "1"
        })
    )

    y_test_api = pd.to_numeric(
        y_test_api,
        errors="raise"
    ).astype(int)

    # Validate target labels
    if y_test_api.isna().any():
        raise ValueError(
            "Test dataset contains missing target labels."
        )

    if not set(y_test_api.unique()).issubset({0, 1}):
        raise ValueError(
            "Churn labels must contain only 0 and 1."
        )

    # 3. Generate model predictions
    y_pred = model.predict(X_test_api)

    y_prob = model.predict_proba(X_test_api)[:, 1]

    # 4. Calculate current performance
    current_metrics = monitor_model_performance(
        y_true=y_test_api,
        y_pred=y_pred,
        y_prob=y_prob
    )

    # 5. Load baseline metrics
    baseline_path = (
        PROJECT_ROOT / "models" / "baseline_metrics.json"
    )

    with open(baseline_path, "r") as file:
        baseline_metrics = json.load(file)

    # 6. Detect performance degradation
    degradation_report = detect_performance_degradation(
        current_metrics=current_metrics,
        baseline_metrics=baseline_metrics
    )

    # 7. Determine monitoring status
    if any(
        item["Severity"] in ["High", "Critical"]
        for item in degradation_report
    ):
        monitoring_status = "DEGRADATION DETECTED"
    elif any(
        item["Severity"] in ["Low", "Moderate"]
        for item in degradation_report
    ):
        monitoring_status = "WARNING"
    else:
        monitoring_status = "HEALTHY"

    # 8. Return monitoring report
    return {
        "model_name": "Logistic Regression",
        "model_version": "1.0",
        "monitoring_status": monitoring_status,
        "current_performance": current_metrics,
        "baseline_performance": baseline_metrics,
        "degradation_report": degradation_report
    }


def save_monitoring_run(
    overall_status,
    drift_status,
    prediction_status,
    performance_status,
    monitoring_report
):
    db = SessionLocal()

    try:
        monitoring_run = MonitoringRun(
            model_name="Logistic Regression",
            model_version="1.0",
            overall_status=overall_status,
            drift_status=drift_status,
            prediction_status=prediction_status,
            performance_status=performance_status,
            monitoring_report=monitoring_report
        )

        db.add(monitoring_run)
        db.commit()
        

        return monitoring_run.id

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
def create_incident(
    monitoring_run_id,
    title,
    description,
    severity,
    source
):
    db = SessionLocal()

    try:
        # Check whether an incident of this source is already open
        existing_incident = db.query(Incident).filter(
            Incident.source == source,
            Incident.status == "OPEN"
        ).first()

        # Avoid duplicate open incidents
        if existing_incident:
            return existing_incident.id

        incident = Incident(
            monitoring_run_id=monitoring_run_id,
            title=title,
            description=description,
            severity=severity,
            source=source,
            status="OPEN"
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)

        return incident.id

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

@app.get("/monitor/health")
def unified_model_health():

    # Run all three monitoring checks
    drift_result = monitor_drift()
    prediction_result = monitor_predictions()
    performance_result = monitor_performance()

    # Extract individual statuses
    drift_status = drift_result["overall_health"]
    prediction_status = prediction_result["monitoring_status"]
    performance_status = performance_result["monitoring_status"]

    # Determine overall model health
    if (
        drift_status == "CRITICAL"
        or performance_status == "DEGRADATION DETECTED"
    ):
        overall_status = "CRITICAL"

    elif (
        drift_status == "DEGRADED"
        or prediction_status == "DRIFT DETECTED"
        or performance_status == "WARNING"
    ):
        overall_status = "DEGRADED"

    elif drift_status == "WARNING":
        overall_status = "WARNING"

    else:
        overall_status = "HEALTHY"

    # Prepare monitoring report
    monitoring_report = {
        "drift": drift_result,
        "predictions": prediction_result,
        "performance": performance_result
    }

    # Save monitoring run in PostgreSQL
    monitoring_run_id = save_monitoring_run(
        overall_status=overall_status,
        drift_status=drift_status,
        prediction_status=prediction_status,
        performance_status=performance_status,
        monitoring_report=monitoring_report
    )

    # Create incident for critical input data drift
    if drift_status == "CRITICAL":
        create_incident(
            monitoring_run_id=monitoring_run_id,
            title="Critical Input Data Drift Detected",
            description=(
                f"Significant drift detected in input features. "
                f"Overall drift status: {drift_status}"
            ),
            severity="CRITICAL",
            source="input_data_drift"
        )

    # Create incident for prediction distribution drift
    if prediction_status == "DRIFT DETECTED":
        create_incident(
            monitoring_run_id=monitoring_run_id,
            title="Prediction Distribution Drift Detected",
            description=(
                "Production prediction distribution has changed "
                "significantly compared to reference data."
            ),
            severity="HIGH",
            source="prediction_drift"
        )

    # Create incident for model performance degradation
    if performance_status == "DEGRADATION DETECTED":
        create_incident(
            monitoring_run_id=monitoring_run_id,
            title="Model Performance Degradation",
            description=(
                "Model performance has degraded compared to "
                "baseline performance."
            ),
            severity="CRITICAL",
            source="model_performance"
        )

    # Return unified health report
    return {
        "monitoring_run_id": monitoring_run_id,
        "model_name": "Logistic Regression",
        "model_version": "1.0",
        "overall_health": overall_status,

        "monitoring_checks": {
            "input_data_drift": drift_status,
            "prediction_distribution": prediction_status,
            "model_performance": performance_status
        },

        "detailed_reports": {
            "drift": drift_result,
            "predictions": prediction_result,
            "performance": performance_result
        }
    }
@app.get("/incidents")
def get_all_incidents():

    db = SessionLocal()

    try:
        incidents = db.query(Incident).order_by(
            Incident.created_at.desc()
        ).all()

        return [
            {
                "id": incident.id,
                "monitoring_run_id": incident.monitoring_run_id,
                "title": incident.title,
                "description": incident.description,
                "severity": incident.severity,
                "source": incident.source,
                "status": incident.status,
                "created_at": incident.created_at,
                "resolved_at": incident.resolved_at
            }
            for incident in incidents
        ]

    finally:
        db.close()
@app.get("/incidents/{incident_id}")
def get_incident(incident_id: int):

    db = SessionLocal()

    try:
        incident = db.query(Incident).filter(
            Incident.id == incident_id
        ).first()

        if not incident:
            raise HTTPException(
                status_code=404,
                detail="Incident not found"
            )

        return {
            "id": incident.id,
            "monitoring_run_id": incident.monitoring_run_id,
            "title": incident.title,
            "description": incident.description,
            "severity": incident.severity,
            "source": incident.source,
            "status": incident.status,
            "created_at": incident.created_at,
            "resolved_at": incident.resolved_at
        }

    finally:
        db.close()
@app.patch("/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: int):

    db = SessionLocal()

    try:
        incident = db.query(Incident).filter(
            Incident.id == incident_id
        ).first()

        if not incident:
            raise HTTPException(
                status_code=404,
                detail="Incident not found"
            )

        if incident.status == "RESOLVED":
            return {
                "message": "Incident already resolved",
                "incident_id": incident.id
            }

        incident.status = "RESOLVED"
        incident.resolved_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(incident)

        return {
            "message": "Incident resolved successfully",
            "incident_id": incident.id,
            "status": incident.status,
            "resolved_at": incident.resolved_at
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

@app.post("/agent/investigate/{incident_id}")
def trigger_investigation(incident_id: int):

    # Generate a unique ID for this investigation
    thread_id = str(uuid4())

    # Prepare initial agent state
    initial_state = {
        "incident_id": incident_id,
        "incident": None,
        "monitoring_report": None,
        "investigation": None,
        "root_cause": None,
        "recommendations": None,
        "approval_status": None,
        "error": None
    }

    # Configure persistent workflow thread
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    try:
        # Execute the LangGraph workflow
        result = investigator_graph.invoke(
            initial_state,
            config=config
        )

        if result.get("error"):
            raise HTTPException(
                status_code=404,
                detail=result["error"]
            )

        # Extract human approval interruption
        interrupts = result.get("__interrupt__", [])

        approval_details = [
            item.value for item in interrupts
        ]

        return {
            "message": "Investigation completed. Awaiting human approval.",
            "incident_id": incident_id,
            "thread_id": thread_id,
            "investigation": result.get("investigation"),
            "approval_status": result.get("approval_status"),
            "approval_required": bool(interrupts),
            "approval_details": approval_details
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/agent/approve/{thread_id}")
def approve_investigation(
    thread_id: str,
    decision: str
):

    decision = decision.upper()

    if decision not in ["APPROVED", "REJECTED"]:
        raise HTTPException(
            status_code=400,
            detail="Decision must be APPROVED or REJECTED"
        )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    try:
        result = investigator_graph.invoke(
            Command(resume=decision),
            config=config
        )

        return {
            "message": "Human decision recorded successfully",
            "thread_id": thread_id,
            "approval_status": result.get("approval_status"),
            "incident_id": result.get("incident", {}).get("id"),
            "workflow_completed": not bool(
                result.get("__interrupt__")
            )
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

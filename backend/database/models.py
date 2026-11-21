
from sqlalchemy import Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Float, DateTime, JSON, ForeignKey


class Base(DeclarativeBase):
    pass


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    customer_data: Mapped[dict] = mapped_column(JSON)

    prediction: Mapped[str] = mapped_column(String(20))

    churn_probability: Mapped[float] = mapped_column(Float)

    model_name: Mapped[str] = mapped_column(String(100))

    model_version: Mapped[str] = mapped_column(String(20))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

class MonitoringRun(Base):
    __tablename__ = "monitoring_runs"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    model_name: Mapped[str] = mapped_column(String(100))
    model_version: Mapped[str] = mapped_column(String(20))

    overall_status: Mapped[str] = mapped_column(String(30))

    drift_status: Mapped[str] = mapped_column(String(30))
    prediction_status: Mapped[str] = mapped_column(String(30))
    performance_status: Mapped[str] = mapped_column(String(30))

    monitoring_report: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    monitoring_run_id: Mapped[int] = mapped_column(
        ForeignKey("monitoring_runs.id")
    )

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(1000))

    severity: Mapped[str] = mapped_column(String(30))
    source: Mapped[str] = mapped_column(String(50))

    status: Mapped[str] = mapped_column(
        String(30), default="OPEN"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

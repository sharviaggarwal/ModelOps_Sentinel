
import csv
from pathlib import Path

# Locate project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Production data storage
PRODUCTION_DATA_PATH = (
    PROJECT_ROOT / "data" / "processed" / "production_data.csv"
)

def log_production_data(customer_data: dict):

    # Ensure directory exists
    PRODUCTION_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    file_exists = PRODUCTION_DATA_PATH.exists()

    with open(
        PRODUCTION_DATA_PATH,
        mode="a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=customer_data.keys()
        )

        # Write column names only for a new file
        if not file_exists or PRODUCTION_DATA_PATH.stat().st_size == 0:
            writer.writeheader()

        writer.writerow(customer_data)
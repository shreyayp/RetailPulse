from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORTS_DIR = ROOT / "reports"
DB_PATH = PROCESSED_DIR / "retailpulse.db"
SALES_OUTPUT = PROCESSED_DIR / "sales_clean.csv"
INVENTORY_OUTPUT = PROCESSED_DIR / "inventory_clean.csv"
DATASET_URL = "https://data.mendeley.com/datasets/27x8mjm8k4/1"

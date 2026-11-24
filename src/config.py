from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

RAW_FILE = DATA_RAW / "AmesHousing.csv"

TARGET = "SalePrice"
RANDOM_STATE = 42
TEST_SIZE = 0.2
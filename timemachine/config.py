import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

CORPUS_DIR = ROOT / "corpus"
METADATA_CSV = CORPUS_DIR / "metadata.csv"
GOLD_DEV = ROOT / "week2" / "gold_qa_dev.jsonl"
GOLD_HELDOUT = ROOT / "week2" / "gold_qa_heldout.jsonl"
CACHE_DIR = ROOT / ".cache"
RESULTS_DIR = ROOT / "results"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
GEMINI_MIN_INTERVAL = float(os.getenv("GEMINI_MIN_INTERVAL", "4"))

DEFAULT_K = 5

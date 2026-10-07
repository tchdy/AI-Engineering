"""Shared loading for Task 2: one source of truth for the data and record IDs."""
from pathlib import Path

import pandas as pd

HW_DIR = Path(__file__).resolve().parent.parent          # homework-01/
SOURCE_FILE = HW_DIR / "data/raw/tobi-bueck/aa_dataset-tickets-multi-lang-5-2-50-version.csv"
SOURCE_COMMIT = "ddf1c81a5475992c4fa6752bf1e8b4e31f07bbeb"
TEXT_FIELD = "body"
LABEL_FIELD = "queue"
LANGUAGE_FIELD = "language"
ENGLISH_CODE = "en"


def is_missing(values: pd.Series) -> pd.Series:
    """True where a value is null (NaN/None), an empty string, or whitespace only.

    Both scripts use this, so "missing" means the same thing everywhere.
    """
    stripped = values.astype("string").str.strip()
    return (values.isna() | stripped.eq("")).fillna(True).astype(bool)


def load_source() -> pd.DataFrame:
    """Read the raw CSV and add a stable record_id. No filtering here."""
    df = pd.read_csv(SOURCE_FILE)
    # DECISION: record_id is the 1-based row position in the raw CSV, formatted
    # as "R00001". It is stable because the file is pinned to SOURCE_COMMIT and
    # the ID is assigned straight after reading, before any sorting or
    # filtering, so the same row always gets the same ID in every script/run.
    df.insert(0, "record_id", [f"R{i:05d}" for i in range(1, len(df) + 1)])
    assert df["record_id"].is_unique, "record_id values are not unique"
    return df


def filter_english(df: pd.DataFrame) -> pd.DataFrame:
    """Basic filter used by both scripts."""
    # DECISION: keep rows whose `language` equals "en" (after trimming spaces
    # and lower-casing). Rows with a missing language are dropped, because we
    # cannot confirm that they are English.
    lang = df[LANGUAGE_FIELD].astype("string").str.strip().str.lower()
    return df[lang.eq(ENGLISH_CODE).fillna(False).astype(bool)].copy()

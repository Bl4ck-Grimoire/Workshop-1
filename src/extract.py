from __future__ import annotations
from pathlib import Path

import pandas as pd

CSV_SEPARATOR = ";"
RAW_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "candidates.csv"


def extract(path: Path | str = RAW_DATA_PATH) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}\n"
            "Verify that candidates.csv is in data/raw/"
        )

    df_raw = pd.read_csv(path, sep=CSV_SEPARATOR)

    print(f"[EXTRACT] File read: {path.name}")
    print(f"[EXTRACT] Rows: {df_raw.shape[0]} | Columns: {df_raw.shape[1]}")

    return df_raw


if __name__ == "__main__":
    df = extract()
    print(df.head())

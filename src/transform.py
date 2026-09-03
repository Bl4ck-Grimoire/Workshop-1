from __future__ import annotations
import pandas as pd

HIRE_THRESHOLD = 7

def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["Application Date"] = pd.to_datetime(df["Application Date"], errors="coerce")
    df["YOE"] = pd.to_numeric(df["YOE"], errors="coerce")
    df["Code Challenge Score"] = pd.to_numeric(df["Code Challenge Score"], errors="coerce")
    df["Technical Interview Score"] = pd.to_numeric(df["Technical Interview Score"], errors="coerce")

    for col in ["Country", "Seniority", "Technology"]:
        df[col] = df[col].astype(str).str.strip()

    before = len(df)
    df = df.dropna(subset=["Application Date", "Code Challenge Score", "Technical Interview Score"])
    dropped = before - len(df)
    if dropped:
        print(f"[TRANSFORM] {dropped} rows with missing critical data were discarded")

    full_duplicates = df.duplicated().sum()
    if full_duplicates:
        df = df.drop_duplicates()
        print(f"[TRANSFORM] {full_duplicates} rows totally duplicated were removed")

    return df.reset_index(drop=True)


def apply_business_rules(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["is_hired"] = (
        (df["Code Challenge Score"] >= HIRE_THRESHOLD)
        & (df["Technical Interview Score"] >= HIRE_THRESHOLD)
    ).astype(int)

    df["score_gap"] = (df["Code Challenge Score"] - df["Technical Interview Score"]).abs()

    print(
        f"[TRANSFORM] Hired Candidates: {df['is_hired'].sum()} "
        f"({df['is_hired'].mean() * 100:.2f}% hiring rate)"
    )

    return df


def transform(df_raw: pd.DataFrame) -> pd.DataFrame:
    df_prepared = prepare_data(df_raw)
    df_transformed = apply_business_rules(df_prepared)
    return df_transformed


if __name__ == "__main__":
    from extract import extract

    df = transform(extract())
    print(df.head())

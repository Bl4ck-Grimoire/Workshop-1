"""
Task 4 - Dimensional Transformation

Construye las 5 dimensiones y el FACT_APPLICATION definidos en el punto 9
(Star Schema), generando surrogate keys y mapeando cada postulacion a sus
llaves de dimension.

Conceptualmente:
Prepared Candidate Data -> Dimension Records -> Surrogate Keys ->
Key Mapping -> Fact Table
"""
from __future__ import annotations

import pandas as pd

# Bandas de experiencia (YOE real observado: 0-30 anios, ver Task 1)
YOE_BINS = [-1, 5, 10, 15, 20, 25, 30]
YOE_LABELS = ["0-5", "6-10", "11-15", "16-20", "21-25", "26-30"]

# Orden logico de seniority, para el atributo seniority_rank (ordenar en BI)
SENIORITY_ORDER = ["Trainee", "Intern", "Junior", "Mid-Level", "Senior", "Lead", "Architect"]


def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    dates = df["Application Date"].dropna().dt.normalize().unique()
    dim = pd.DataFrame({"full_date": sorted(dates)})
    dim.insert(0, "date_key", range(1, len(dim) + 1))
    dim["day"] = dim["full_date"].dt.day
    dim["month"] = dim["full_date"].dt.month
    dim["month_name"] = dim["full_date"].dt.month_name()
    dim["quarter"] = dim["full_date"].dt.quarter
    dim["year"] = dim["full_date"].dt.year
    return dim[["date_key", "full_date", "day", "month", "month_name", "quarter", "year"]]


def build_dim_technology(df: pd.DataFrame) -> pd.DataFrame:
    values = sorted(df["Technology"].dropna().unique())
    dim = pd.DataFrame({"technology_name": values})
    dim.insert(0, "technology_key", range(1, len(dim) + 1))
    return dim


def build_dim_country(df: pd.DataFrame) -> pd.DataFrame:
    values = sorted(df["Country"].dropna().unique())
    dim = pd.DataFrame({"country_name": values})
    dim.insert(0, "country_key", range(1, len(dim) + 1))
    return dim


def build_dim_seniority(df: pd.DataFrame) -> pd.DataFrame:
    values = sorted(df["Seniority"].dropna().unique())
    dim = pd.DataFrame({"seniority_level": values})
    rank_map = {level: i + 1 for i, level in enumerate(SENIORITY_ORDER)}
    dim["seniority_rank"] = (
        dim["seniority_level"].map(rank_map).fillna(len(SENIORITY_ORDER) + 1).astype(int)
    )
    dim.insert(0, "seniority_key", range(1, len(dim) + 1))
    return dim


def build_dim_experience_range() -> pd.DataFrame:
    dim = pd.DataFrame({
        "yoe_range": YOE_LABELS,
        "yoe_min": [b + 1 if b != -1 else 0 for b in YOE_BINS[:-1]],
        "yoe_max": YOE_BINS[1:],
    })
    dim.insert(0, "experience_key", range(1, len(dim) + 1))
    return dim


def build_fact_application(
    df: pd.DataFrame,
    dim_date: pd.DataFrame,
    dim_technology: pd.DataFrame,
    dim_country: pd.DataFrame,
    dim_seniority: pd.DataFrame,
    dim_experience: pd.DataFrame,
) -> pd.DataFrame:
    fact = df.copy()
    fact["yoe_range"] = pd.cut(fact["YOE"], bins=YOE_BINS, labels=YOE_LABELS).astype(str)
    fact["_app_date"] = fact["Application Date"].dt.normalize()

    fact = fact.merge(dim_date[["date_key", "full_date"]], left_on="_app_date", right_on="full_date", how="left")
    fact = fact.merge(dim_technology, left_on="Technology", right_on="technology_name", how="left")
    fact = fact.merge(dim_country, left_on="Country", right_on="country_name", how="left")
    fact = fact.merge(dim_seniority, left_on="Seniority", right_on="seniority_level", how="left")
    fact = fact.merge(dim_experience, on="yoe_range", how="left")

    # Validacion de integridad: ninguna postulacion debe quedar sin llave
    key_cols = ["date_key", "technology_key", "country_key", "seniority_key", "experience_key"]
    missing = fact[key_cols].isnull().any(axis=1).sum()
    if missing:
        raise ValueError(f"[DIMENSIONAL_MODEL] {missing} filas no pudieron mapearse a una dimension")

    fact = fact.reset_index(drop=True)
    fact.insert(0, "application_key", range(1, len(fact) + 1))

    fact = fact.rename(columns={
        "Code Challenge Score": "code_challenge_score",
        "Technical Interview Score": "technical_interview_score",
    })

    final_cols = [
        "application_key", "date_key", "technology_key", "country_key",
        "seniority_key", "experience_key",
        "code_challenge_score", "technical_interview_score", "score_gap", "is_hired",
    ]
    return fact[final_cols]


def build_star_schema(df_transformed: pd.DataFrame) -> dict:
    """Construye las 5 dimensiones y el fact table a partir de los datos ya transformados."""
    dim_date = build_dim_date(df_transformed)
    dim_technology = build_dim_technology(df_transformed)
    dim_country = build_dim_country(df_transformed)
    dim_seniority = build_dim_seniority(df_transformed)
    dim_experience = build_dim_experience_range()

    fact_application = build_fact_application(
        df_transformed, dim_date, dim_technology, dim_country, dim_seniority, dim_experience
    )

    print("[DIMENSIONAL_MODEL] Tablas construidas:")
    print(f"  dim_date:             {len(dim_date)} filas")
    print(f"  dim_technology:       {len(dim_technology)} filas")
    print(f"  dim_country:          {len(dim_country)} filas")
    print(f"  dim_seniority:        {len(dim_seniority)} filas")
    print(f"  dim_experience_range: {len(dim_experience)} filas")
    print(f"  fact_application:     {len(fact_application)} filas")

    return {
        "dim_date": dim_date,
        "dim_technology": dim_technology,
        "dim_country": dim_country,
        "dim_seniority": dim_seniority,
        "dim_experience_range": dim_experience,
        "fact_application": fact_application,
    }


if __name__ == "__main__":
    from extract import extract
    from transform import transform

    tables = build_star_schema(transform(extract()))
    for name, tdf in tables.items():
        print(f"\n{name}")
        print(tdf.head())

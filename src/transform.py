"""
Task 3.2 - Data Preparation
Task 3.3 - Business Transformation
"""
from __future__ import annotations

import pandas as pd

HIRE_THRESHOLD = 7  # Code Challenge Score >= 7 AND Technical Interview Score >= 7


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Data Preparation (Task 3.2).

    Decisiones documentadas:
      - Se corrigen tipos: Application Date -> datetime, YOE y los dos
        scores -> numericos.
      - Se estandariza texto (strip) en las columnas categoricas.
      - El profiling (Task 1) confirmo 0 nulos y 0 filas totalmente
        duplicadas en el dataset original; se dejan validaciones
        defensivas por si el archivo fuente llegara a cambiar.
      - NO se eliminan los 167 emails duplicados detectados en el
        profiling: el grain del modelo es "una postulacion", no "un
        candidato unico", asi que cada fila del CSV es una postulacion
        valida por si misma.
    """
    df = df.copy()

    # --- Tipos de datos ---
    df["Application Date"] = pd.to_datetime(df["Application Date"], errors="coerce")
    df["YOE"] = pd.to_numeric(df["YOE"], errors="coerce")
    df["Code Challenge Score"] = pd.to_numeric(df["Code Challenge Score"], errors="coerce")
    df["Technical Interview Score"] = pd.to_numeric(df["Technical Interview Score"], errors="coerce")

    # --- Estandarizacion de texto en categoricas ---
    for col in ["Country", "Seniority", "Technology"]:
        df[col] = df[col].astype(str).str.strip()

    # --- Nulos (defensivo) ---
    before = len(df)
    df = df.dropna(subset=["Application Date", "Code Challenge Score", "Technical Interview Score"])
    dropped = before - len(df)
    if dropped:
        print(f"[TRANSFORM] Se descartaron {dropped} filas con datos criticos faltantes")

    # --- Filas totalmente duplicadas (defensivo) ---
    full_duplicates = df.duplicated().sum()
    if full_duplicates:
        df = df.drop_duplicates()
        print(f"[TRANSFORM] Se eliminaron {full_duplicates} filas totalmente duplicadas")

    return df.reset_index(drop=True)


def apply_business_rules(df: pd.DataFrame) -> pd.DataFrame:
    """
    Business Transformation (Task 3.3).

      - is_hired: regla de negocio oficial del workshop.
      - score_gap: atributo derivado requerido por R4 (brecha entre
        Code Challenge y Technical Interview).

    No se crean columnas derivadas adicionales sin proposito analitico,
    tal como pide el documento.
    """
    df = df.copy()

    df["is_hired"] = (
        (df["Code Challenge Score"] >= HIRE_THRESHOLD)
        & (df["Technical Interview Score"] >= HIRE_THRESHOLD)
    ).astype(int)

    df["score_gap"] = (df["Code Challenge Score"] - df["Technical Interview Score"]).abs()

    print(
        f"[TRANSFORM] Candidatos contratados: {df['is_hired'].sum()} "
        f"({df['is_hired'].mean() * 100:.2f}% tasa de contratacion)"
    )

    return df


def transform(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Orquesta Data Preparation -> Business Transformation."""
    df_prepared = prepare_data(df_raw)
    df_transformed = apply_business_rules(df_prepared)
    return df_transformed


if __name__ == "__main__":
    from extract import extract

    df = transform(extract())
    print(df.head())

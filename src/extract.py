"""
Task 3.1 - Extract

Lee el archivo fuente candidates.csv y lo carga en un DataFrame de Pandas.
No se realiza NINGUNA transformacion de negocio aqui - solo lectura y
preservacion del archivo original, tal como pide el documento.
"""
from __future__ import annotations
from pathlib import Path

import pandas as pd

# El profiling (Task 1 / notebooks/data_profiling.ipynb) confirmo que el
# archivo fuente usa ';' como separador de columnas, no ','.
CSV_SEPARATOR = ";"
RAW_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "candidates.csv"


def extract(path: Path | str = RAW_DATA_PATH) -> pd.DataFrame:
    """
    Lee el CSV fuente exactamente como fue entregado.
    Devuelve un DataFrame crudo, sin modificar.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontro el archivo fuente en: {path}\n"
            "Verifica que candidates.csv este en data/raw/"
        )

    df_raw = pd.read_csv(path, sep=CSV_SEPARATOR)

    print(f"[EXTRACT] Archivo leido: {path.name}")
    print(f"[EXTRACT] Filas: {df_raw.shape[0]} | Columnas: {df_raw.shape[1]}")

    return df_raw


if __name__ == "__main__":
    df = extract()
    print(df.head())

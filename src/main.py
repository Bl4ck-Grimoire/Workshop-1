"""
main.py - Orquesta el pipeline ETL completo:
Extract -> Transform -> Dimensional Model -> Load (MySQL)
"""
from extract import extract
from transform import transform
from dimensional_model import build_star_schema
from load import load_all, get_engine
from analytics import generate_report

def run_pipeline() -> None:
    print("=" * 60)
    print("WORKSHOP 1 - Recruitment Data Warehouse")
    print("=" * 60)

    print("\n[1/5] EXTRACT")
    df_raw = extract()

    print("\n[2/5] TRANSFORM")
    df_transformed = transform(df_raw)

    print("\n[3/5] DIMENSIONAL MODEL")
    star_schema = build_star_schema(df_transformed)

    print("\n[4/5] LOAD")
    load_all(star_schema)

    print("\n[5/5] ANALYTICAL REPORT")
    generate_report(get_engine())

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()

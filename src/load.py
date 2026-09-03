from __future__ import annotations
import os
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine, text
load_dotenv()
SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
CREATE_TABLES_SQL = SQL_DIR / "create_tables.sql"

TABLE_ORDER = [
    "dim_date",
    "dim_technology",
    "dim_country",
    "dim_seniority",
    "dim_experience_range",
    "fact_application",
]

FK_TO_DIMENSION = {
    "date_key": "dim_date",
    "technology_key": "dim_technology",
    "country_key": "dim_country",
    "seniority_key": "dim_seniority",
    "experience_key": "dim_experience_range",
}


def get_engine():
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    host = os.getenv("MYSQL_HOST")
    port = os.getenv("MYSQL_PORT")
    database = os.getenv("MYSQL_DATABASE")

    base_url = f"mysql+pymysql://{user}:{password}@{host}:{port}"
    temp_engine = create_engine(base_url)

    with temp_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {database}"))

    final_url = f"{base_url}/{database}"
    return create_engine(final_url)


def create_schema(engine) -> None:
    ddl = CREATE_TABLES_SQL.read_text(encoding="utf-8")
    statements = [s.strip() for s in ddl.split(";") if s.strip()]

    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))

    print(f"[LOAD] Schema verified/created from {CREATE_TABLES_SQL.name}")


def reset_tables(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for table in reversed(TABLE_ORDER):
            conn.execute(text(f"TRUNCATE TABLE {table}"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

    print("[LOAD] Tables cleaned before loading")


def load_tables(engine, tables: dict) -> None:
    for table_name in TABLE_ORDER:
        df = tables[table_name]
        df.to_sql(table_name, con=engine, if_exists="append", index=False)
        print(f"[LOAD] {table_name}: {len(df)} rows loaded")


def validate_load(engine) -> None:
    print("\n[VALIDATE] Row counts:")
    with engine.connect() as conn:
        for table in TABLE_ORDER:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  {table}: {count} rows")

        print("\n[VALIDATE] Verifying invalid dimension references.")
        all_ok = True
        for fk_col, dim_table in FK_TO_DIMENSION.items():
            query = text(f"""
                SELECT COUNT(*) FROM fact_application f
                LEFT JOIN {dim_table} d ON f.{fk_col} = d.{fk_col}
                WHERE d.{fk_col} IS NULL
            """)
            orphans = conn.execute(query).scalar()
            status = "OK" if orphans == 0 else "ERROR"
            all_ok = all_ok and orphans == 0
            print(f"  {fk_col} -> {dim_table}: {orphans} invalid references [{status}]")

    print("\n[VALIDATE] Referential integrity is correct" if all_ok
          else "\n[VALIDATE] ATTENTION: invalid references found")


def load_all(tables: dict, reset: bool = True) -> None:
    engine = get_engine()
    create_schema(engine)
    if reset:
        reset_tables(engine)
    load_tables(engine, tables)
    validate_load(engine)


if __name__ == "__main__":
    from extract import extract
    from transform import transform
    from dimensional_model import build_star_schema

    star_schema = build_star_schema(transform(extract()))
    load_all(star_schema)

"""
Task 6 - Analytical Queries and KPIs

Ejecuta las 5 consultas analiticas directamente sobre el Data Warehouse
(MySQL) y genera un reporte en Markdown (results/analytical_report.md)
con, por cada requisito: la pregunta de negocio, la consulta SQL y una
vista previa del resultado.

IMPORTANTE: estas consultas deben mantenerse identicas a las de
sql/analytical_queries.sql. Si editas una alla, edita tambien aqui.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
REPORT_PATH = RESULTS_DIR / "analytical_report.md"

QUERIES = [
    {
        "id": "R1",
        "title": "Hiring Trends",
        "question": "How do applications and hires evolve over time (month/quarter/year)?",
        "sql": """
            SELECT
                d.year,
                d.month,
                d.month_name,
                COUNT(*) AS total_applications,
                SUM(f.is_hired) AS total_hired,
                ROUND(SUM(f.is_hired) / COUNT(*) * 100, 2) AS hire_rate_pct
            FROM fact_application f
            JOIN dim_date d ON f.date_key = d.date_key
            GROUP BY d.year, d.month, d.month_name
            ORDER BY d.year, d.month
        """,
    },
    {
        "id": "R2",
        "title": "Technology Analysis",
        "question": "Which technologies generate the highest number and proportion of hired candidates?",
        "sql": """
            SELECT
                t.technology_name,
                COUNT(*) AS total_applications,
                SUM(f.is_hired) AS total_hired,
                ROUND(SUM(f.is_hired) / COUNT(*) * 100, 2) AS hire_rate_pct
            FROM fact_application f
            JOIN dim_technology t ON f.technology_key = t.technology_key
            GROUP BY t.technology_name
            ORDER BY total_hired DESC
        """,
    },
    {
        "id": "R3",
        "title": "Candidate Profile Analysis",
        "question": "How do hiring outcomes vary according to candidate seniority and years of experience?",
        "sql": """
            SELECT
                s.seniority_level,
                e.yoe_range,
                COUNT(*) AS total_applications,
                SUM(f.is_hired) AS total_hired,
                ROUND(SUM(f.is_hired) / COUNT(*) * 100, 2) AS hire_rate_pct
            FROM fact_application f
            JOIN dim_seniority s ON f.seniority_key = s.seniority_key
            JOIN dim_experience_range e ON f.experience_key = e.experience_key
            GROUP BY s.seniority_level, s.seniority_rank, e.yoe_range, e.yoe_min
            ORDER BY s.seniority_rank, e.yoe_min
        """,
    },
    {
        "id": "R4",
        "title": "Gap between Technical Assessments",
        "question": (
            "Is there a significant difference in performance between the Code Challenge "
            "and the Technical Interview depending on the technology or seniority level?"
        ),
        "sql": """
            SELECT
                t.technology_name,
                s.seniority_level,
                COUNT(*) AS total_applications,
                ROUND(AVG(f.code_challenge_score), 2) AS avg_code_challenge,
                ROUND(AVG(f.technical_interview_score), 2) AS avg_technical_interview,
                ROUND(AVG(f.score_gap), 2) AS avg_score_gap,
                MAX(f.score_gap) AS max_score_gap
            FROM fact_application f
            JOIN dim_technology t ON f.technology_key = t.technology_key
            JOIN dim_seniority s ON f.seniority_key = s.seniority_key
            GROUP BY t.technology_name, s.seniority_level
            ORDER BY avg_score_gap DESC
        """,
    },
    {
        "id": "R5",
        "title": "Geographic Concentration by Technology",
        "question": "Which technology profiles have their candidate pool highly concentrated in specific countries?",
        "sql": """
            WITH tech_country_counts AS (
                SELECT
                    t.technology_key,
                    t.technology_name,
                    c.country_name,
                    COUNT(*) AS applications_in_country
                FROM fact_application f
                JOIN dim_technology t ON f.technology_key = t.technology_key
                JOIN dim_country c ON f.country_key = c.country_key
                GROUP BY t.technology_key, t.technology_name, c.country_name
            ),
            tech_totals AS (
                SELECT technology_key, SUM(applications_in_country) AS total_applications
                FROM tech_country_counts
                GROUP BY technology_key
            ),
            top_country_per_tech AS (
                SELECT
                    tcc.technology_key,
                    tcc.technology_name,
                    tcc.country_name AS top_country,
                    tcc.applications_in_country AS top_country_applications,
                    ROW_NUMBER() OVER (
                        PARTITION BY tcc.technology_key ORDER BY tcc.applications_in_country DESC
                    ) AS rn
                FROM tech_country_counts tcc
            )
            SELECT
                top.technology_name,
                top.top_country,
                top.top_country_applications,
                tt.total_applications,
                ROUND(top.top_country_applications / tt.total_applications * 100, 2)
                    AS top_country_concentration_pct
            FROM top_country_per_tech top
            JOIN tech_totals tt ON top.technology_key = tt.technology_key
            WHERE top.rn = 1
            ORDER BY top_country_concentration_pct DESC
        """,
    },
]


def run_query(engine, sql: str) -> pd.DataFrame:
    return pd.read_sql(sql, con=engine)


def generate_report(engine, top_n: int = 10) -> Path:
    """
    Ejecuta las 5 consultas contra el DW y escribe results/analytical_report.md
    con la pregunta de negocio, la consulta SQL y una vista previa (top_n filas)
    del resultado de cada una.
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Analytical Report — Recruitment Data Warehouse",
        "",
        f"_Generated automatically on {datetime.now():%Y-%m-%d %H:%M}_",
        "",
    ]

    for query in QUERIES:
        print(f"[ANALYTICS] Ejecutando {query['id']} - {query['title']}...")
        df = run_query(engine, query["sql"])

        lines += [
            f"## {query['id']} — {query['title']}",
            "",
            f"**Business question:** {query['question']}",
            "",
            "```sql",
            query["sql"].strip(),
            "```",
            "",
            f"**Result** (showing top {top_n} of {len(df)} rows):",
            "",
            df.head(top_n).to_markdown(index=False),
            "",
        ]

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"[ANALYTICS] Reporte generado en {REPORT_PATH}")
    return REPORT_PATH


if __name__ == "__main__":
    from load import get_engine

    generate_report(get_engine())
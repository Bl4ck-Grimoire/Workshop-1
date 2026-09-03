-- ============================================================
-- Workshop 1 - ETL (G01) - Task 6: Analytical Queries and KPIs
-- Todas las consultas se ejecutan directamente sobre el Data
-- Warehouse (recruitment_dw), nunca sobre el CSV fuente.
-- Requiere MySQL 8.0+ (CTEs y funciones de ventana en R5).
-- ============================================================


-- ============================================================
-- R1 - Hiring Trends
-- Pregunta: ¿Como evolucionan las postulaciones y las contrataciones
--           a lo largo del tiempo (mes/anio)?
-- ============================================================
SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(*)                                   AS total_applications,
    SUM(f.is_hired)                            AS total_hired,
    ROUND(SUM(f.is_hired) / COUNT(*) * 100, 2) AS hire_rate_pct
FROM fact_application f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;


-- ============================================================
-- R2 - Technology Analysis
-- Pregunta: ¿Que tecnologias generan el mayor numero y proporcion
--           de candidatos contratados?
-- ============================================================
SELECT
    t.technology_name,
    COUNT(*)                                   AS total_applications,
    SUM(f.is_hired)                            AS total_hired,
    ROUND(SUM(f.is_hired) / COUNT(*) * 100, 2) AS hire_rate_pct
FROM fact_application f
JOIN dim_technology t ON f.technology_key = t.technology_key
GROUP BY t.technology_name
ORDER BY total_hired DESC;


-- ============================================================
-- R3 - Candidate Profile Analysis
-- Pregunta: ¿Como varian los resultados de contratacion segun
--           seniority y anios de experiencia?
-- ============================================================
SELECT
    s.seniority_level,
    e.yoe_range,
    COUNT(*)                                   AS total_applications,
    SUM(f.is_hired)                            AS total_hired,
    ROUND(SUM(f.is_hired) / COUNT(*) * 100, 2) AS hire_rate_pct
FROM fact_application f
JOIN dim_seniority s        ON f.seniority_key = s.seniority_key
JOIN dim_experience_range e ON f.experience_key = e.experience_key
GROUP BY s.seniority_level, e.yoe_range
ORDER BY s.seniority_rank, e.yoe_min;


-- ============================================================
-- R4 - Gap between Technical Assessments  (requisito modificado)
-- Pregunta: ¿Hay una diferencia significativa entre el Code
--           Challenge y la Entrevista Tecnica segun tecnologia
--           o nivel de seniority?
-- Decision: auditar la validez de las pruebas y rediseñar las que
--           produzcan resultados sistematicamente inconsistentes.
-- ============================================================
SELECT
    t.technology_name,
    s.seniority_level,
    COUNT(*)                                       AS total_applications,
    ROUND(AVG(f.code_challenge_score), 2)          AS avg_code_challenge,
    ROUND(AVG(f.technical_interview_score), 2)     AS avg_technical_interview,
    ROUND(AVG(f.score_gap), 2)                     AS avg_score_gap,
    MAX(f.score_gap)                               AS max_score_gap
FROM fact_application f
JOIN dim_technology t ON f.technology_key = t.technology_key
JOIN dim_seniority s  ON f.seniority_key = s.seniority_key
GROUP BY t.technology_name, s.seniority_level
ORDER BY avg_score_gap DESC;


-- ============================================================
-- R5 - Geographic Concentration by Technology  (requisito modificado)
-- Pregunta: ¿Que tecnologias tienen su pool de candidatos muy
--           concentrado en pocos paises?
-- Decision: diversificar el sourcing y abrir campañas remotas en
--           nuevos mercados para las tecnologias mas concentradas.
-- ============================================================
WITH tech_country_counts AS (
    SELECT
        t.technology_key,
        t.technology_name,
        c.country_name,
        COUNT(*) AS applications_in_country
    FROM fact_application f
    JOIN dim_technology t ON f.technology_key = t.technology_key
    JOIN dim_country c    ON f.country_key    = c.country_key
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
    ROUND(top.top_country_applications / tt.total_applications * 100, 2) AS top_country_concentration_pct
FROM top_country_per_tech top
JOIN tech_totals tt ON top.technology_key = tt.technology_key
WHERE top.rn = 1
ORDER BY top_country_concentration_pct DESC;

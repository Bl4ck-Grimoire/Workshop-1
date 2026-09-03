-- ============================================================
-- Workshop 1 - ETL (G01) - Recruitment Data Warehouse
-- Motor: MySQL 8.0+
--
-- Prerrequisito: crear (una sola vez) una base de datos vacia,
-- por ejemplo desde MySQL Workbench:
--   CREATE DATABASE recruitment_dw;
-- y apuntar la conexion (src/load.py) a esa base.
-- ============================================================

-- ------------------------------------------------------------
-- Dimension: DIM_DATE  (soporta R1)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_date (
    date_key    INT PRIMARY KEY,
    full_date   DATE NOT NULL,
    day         TINYINT UNSIGNED NOT NULL,
    month       TINYINT UNSIGNED NOT NULL,
    month_name  VARCHAR(20) NOT NULL,
    quarter     TINYINT UNSIGNED NOT NULL,
    year        SMALLINT UNSIGNED NOT NULL
);

-- ------------------------------------------------------------
-- Dimension: DIM_TECHNOLOGY  (soporta R2, R4, R5)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_technology (
    technology_key   INT PRIMARY KEY,
    technology_name  VARCHAR(100) NOT NULL
);

-- ------------------------------------------------------------
-- Dimension: DIM_COUNTRY  (soporta R5)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_country (
    country_key   INT PRIMARY KEY,
    country_name  VARCHAR(100) NOT NULL
);

-- ------------------------------------------------------------
-- Dimension: DIM_SENIORITY  (soporta R3, R4)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_seniority (
    seniority_key    INT PRIMARY KEY,
    seniority_level  VARCHAR(50) NOT NULL,
    seniority_rank   TINYINT UNSIGNED NOT NULL
);

-- ------------------------------------------------------------
-- Dimension: DIM_EXPERIENCE_RANGE  (soporta R3)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_experience_range (
    experience_key  INT PRIMARY KEY,
    yoe_range       VARCHAR(20) NOT NULL,
    yoe_min         TINYINT UNSIGNED NOT NULL,
    yoe_max         TINYINT UNSIGNED NOT NULL
);

-- ------------------------------------------------------------
-- Fact: FACT_APPLICATION
-- Grain: una fila = una postulacion evaluada en el proceso de seleccion
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_application (
    application_key             INT PRIMARY KEY,
    date_key                    INT NOT NULL,
    technology_key               INT NOT NULL,
    country_key                 INT NOT NULL,
    seniority_key                INT NOT NULL,
    experience_key               INT NOT NULL,
    code_challenge_score         TINYINT UNSIGNED NOT NULL,
    technical_interview_score    TINYINT UNSIGNED NOT NULL,
    score_gap                    TINYINT UNSIGNED NOT NULL,
    is_hired                     TINYINT(1) NOT NULL,

    CONSTRAINT fk_fact_date       FOREIGN KEY (date_key)       REFERENCES dim_date(date_key),
    CONSTRAINT fk_fact_technology FOREIGN KEY (technology_key) REFERENCES dim_technology(technology_key),
    CONSTRAINT fk_fact_country    FOREIGN KEY (country_key)    REFERENCES dim_country(country_key),
    CONSTRAINT fk_fact_seniority  FOREIGN KEY (seniority_key)  REFERENCES dim_seniority(seniority_key),
    CONSTRAINT fk_fact_experience FOREIGN KEY (experience_key) REFERENCES dim_experience_range(experience_key)
);

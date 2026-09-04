# Analytical Report — Recruitment Data Warehouse

_Generated automatically on 2026-09-03 22:52_

## R1 — Hiring Trends

**Business question:** How do applications and hires evolve over time (month/quarter/year)?

```sql
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
```

**Result** (showing top 10 of 55 rows):

|   year |   month | month_name   |   total_applications |   total_hired |   hire_rate_pct |
|-------:|--------:|:-------------|---------------------:|--------------:|----------------:|
|   2018 |       1 | January      |                  922 |           112 |           12.15 |
|   2018 |       2 | February     |                  867 |           123 |           14.19 |
|   2018 |       3 | March        |                  899 |           116 |           12.9  |
|   2018 |       4 | April        |                  879 |           101 |           11.49 |
|   2018 |       5 | May          |                  924 |           130 |           14.07 |
|   2018 |       6 | June         |                  923 |           125 |           13.54 |
|   2018 |       7 | July         |                  965 |           123 |           12.75 |
|   2018 |       8 | August       |                  951 |           117 |           12.3  |
|   2018 |       9 | September    |                  944 |           108 |           11.44 |
|   2018 |      10 | October      |                  922 |           126 |           13.67 |

## R2 — Technology Analysis

**Business question:** Which technologies generate the highest number and proportion of hired candidates?

```sql
SELECT
                t.technology_name,
                COUNT(*) AS total_applications,
                SUM(f.is_hired) AS total_hired,
                ROUND(SUM(f.is_hired) / COUNT(*) * 100, 2) AS hire_rate_pct
            FROM fact_application f
            JOIN dim_technology t ON f.technology_key = t.technology_key
            GROUP BY t.technology_name
            ORDER BY total_hired DESC
```

**Result** (showing top 10 of 24 rows):

| technology_name           |   total_applications |   total_hired |   hire_rate_pct |
|:--------------------------|---------------------:|--------------:|----------------:|
| Game Development          |                 3818 |           519 |           13.59 |
| DevOps                    |                 3808 |           495 |           13    |
| System Administration     |                 2014 |           293 |           14.55 |
| Development - CMS Backend |                 1882 |           284 |           15.09 |
| Adobe Experience Manager  |                 1954 |           282 |           14.43 |
| Database Administration   |                 1933 |           282 |           14.59 |
| Client Success            |                 1927 |           271 |           14.06 |
| Security                  |                 1936 |           266 |           13.74 |
| Development - Frontend    |                 1887 |           266 |           14.1  |
| Mulesoft                  |                 1973 |           260 |           13.18 |

## R3 — Candidate Profile Analysis

**Business question:** How do hiring outcomes vary according to candidate seniority and years of experience?

```sql
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
```

**Result** (showing top 10 of 42 rows):

| seniority_level   | yoe_range   |   total_applications |   total_hired |   hire_rate_pct |
|:------------------|:------------|---------------------:|--------------:|----------------:|
| Trainee           | 0-5         |                 1356 |           191 |           14.09 |
| Trainee           | 6-10        |                 1154 |           159 |           13.78 |
| Trainee           | 11-15       |                 1144 |           155 |           13.55 |
| Trainee           | 16-20       |                 1142 |           155 |           13.57 |
| Trainee           | 21-25       |                 1216 |           150 |           12.34 |
| Trainee           | 26-30       |                 1171 |           163 |           13.92 |
| Intern            | 0-5         |                 1281 |           198 |           15.46 |
| Intern            | 6-10        |                 1194 |           148 |           12.4  |
| Intern            | 11-15       |                 1096 |           140 |           12.77 |
| Intern            | 16-20       |                 1251 |           180 |           14.39 |

## R4 — Gap between Technical Assessments

**Business question:** Is there a significant difference in performance between the Code Challenge and the Technical Interview depending on the technology or seniority level?

```sql
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
```

**Result** (showing top 10 of 168 rows):

| technology_name                   | seniority_level   |   total_applications |   avg_code_challenge |   avg_technical_interview |   avg_score_gap |   max_score_gap |
|:----------------------------------|:------------------|---------------------:|---------------------:|--------------------------:|----------------:|----------------:|
| Social Media Community Management | Junior            |                  275 |                 4.96 |                      4.87 |            4.02 |              10 |
| Sales                             | Mid-Level         |                  267 |                 5.05 |                      4.91 |            4.01 |              10 |
| System Administration             | Lead              |                  259 |                 4.86 |                      5.1  |            3.97 |              10 |
| Social Media Community Management | Mid-Level         |                  310 |                 4.7  |                      5.01 |            3.95 |              10 |
| Sales                             | Architect         |                  290 |                 4.91 |                      5.02 |            3.93 |              10 |
| Development - FullStack           | Senior            |                  290 |                 4.76 |                      5.11 |            3.93 |              10 |
| Social Media Community Management | Trainee           |                  287 |                 4.83 |                      4.48 |            3.92 |              10 |
| System Administration             | Senior            |                  274 |                 4.92 |                      5.18 |            3.91 |              10 |
| Development - Backend             | Mid-Level         |                  284 |                 5.02 |                      4.65 |            3.9  |              10 |
| Business Intelligence             | Lead              |                  263 |                 5.18 |                      4.95 |            3.9  |              10 |

## R5 — Geographic Concentration by Technology

**Business question:** Which technology profiles have their candidate pool highly concentrated in specific countries?

```sql
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
```

**Result** (showing top 10 of 24 rows):

| technology_name                   | top_country          |   top_country_applications |   total_applications |   top_country_concentration_pct |
|:----------------------------------|:---------------------|---------------------------:|---------------------:|--------------------------------:|
| Development - Frontend            | Malawi               |                         19 |                 1887 |                            1.01 |
| Business Intelligence             | Yemen                |                         19 |                 1934 |                            0.98 |
| Data Engineer                     | Nigeria              |                         19 |                 1951 |                            0.97 |
| Mulesoft                          | Christmas Island     |                         19 |                 1973 |                            0.96 |
| System Administration             | Saint Lucia          |                         19 |                 2014 |                            0.94 |
| Development - Backend             | Liberia              |                         18 |                 1965 |                            0.92 |
| Design                            | Netherlands Antilles |                         17 |                 1906 |                            0.89 |
| QA Manual                         | Tuvalu               |                         17 |                 1902 |                            0.89 |
| Social Media Community Management | Cuba                 |                         18 |                 2028 |                            0.89 |
| Security                          | Taiwan               |                         17 |                 1936 |                            0.88 |

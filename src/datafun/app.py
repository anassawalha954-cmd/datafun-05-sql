"""src/datafun/app.py - Project script (customized: health domain).

Author: Anas
Date: 2026-09

HOW TO RUN THIS FILE:

From the VS Code menu (with only this project open in VS Code),
click "Terminal" / New Terminal to
open an integrated Terminal in the root project folder.
Paste the following command and press ENTER or RETURN
to run this file as a script:

uv run python -m datafun.app

DOMAIN:

A small clinic network with clinics, patients, visits, and lab results.

The data is stored in four related CSV files:

- one row per clinic
- one row per patient
- one row per visit
- one row per lab result

One clinic can have many patients.
One patient can have many visits.
One visit can have many lab results.

EXPLORE:

Sometimes the information needed for an analysis
is stored in more than one related table.

SQL is especially useful when tables share keys
and we want to analyze information across them.

A simple Python and SQL process is:

1. LOAD the related tables.
2. INSPECT the grain and keys.
3. CREATE a SQLite database.
4. LOAD the tables into SQLite.
5. QUERY across related tables with SQL.
6. VISUALIZE the query result with Python.
7. SUMMARIZE what you found.
8. DISPLAY the visualization.

DESIGN:

Use this file to declare the data-specific choices
and the reasoning behind them,
then orchestrate the work.

SQLite comes from the Python Standard Library.
Pandas loads tabular data into SQLite
and returns SQL query results as DataFrames.
Reusable visualization functions come from eda-vizkit.

The SQL stays here because the query is an
analytical decision specific to this project.
"""

# === DECLARE IMPORTS (BRING IN FREE CODE) ===

import logging
from pathlib import Path
import sqlite3
from typing import Final

from datafun_toolkit.logger import get_logger, log_header, log_path
from eda_vizkit import save_chart
import matplotlib.pyplot as plt
import pandas as pd

# === CONFIGURE LOGGER ONCE FOR THE APPLICATION ===

LOG: logging.Logger = get_logger("P05", level="DEBUG")

# === LOCATE THE DATA FILES ===

DATA_DIR: Final[Path] = Path("data") / "health"

CLINIC_FILE: Final[Path] = DATA_DIR / "clinic.csv"
PATIENT_FILE: Final[Path] = DATA_DIR / "patient.csv"
VISIT_FILE: Final[Path] = DATA_DIR / "visit.csv"
LAB_RESULT_FILE: Final[Path] = DATA_DIR / "lab_result.csv"

# === LOCATE THE SQLITE DATABASE ===

DATABASE_FILE: Final[Path] = DATA_DIR / "health.sqlite"

# === LOCATE THE CHART OUTPUT ===

CHART_DIR: Final[Path] = Path("docs") / "images"
CHART_PATH: Final[Path] = CHART_DIR / "health-chart.png"

# === DETERMINE WHAT ONE ROW REPRESENTS ===

CLINIC_GRAIN: Final[str] = "one clinic"
PATIENT_GRAIN: Final[str] = "one patient"
VISIT_GRAIN: Final[str] = "one visit"
LAB_RESULT_GRAIN: Final[str] = "one lab test result from one visit"

# === DESCRIBE THE TABLE RELATIONSHIPS ===

RELATIONSHIP_DECISION: Final[str] = r"""
The data is stored in four related tables.

One clinic can have many patients.
The patients table uses clinic_id to identify each patient's clinic.

One patient can have many visits.
The visits table uses patient_id to identify each visit's patient.

One visit can have many lab results.
The lab_results table uses visit_id to identify each result's visit.

The shared keys connect information stored across all four tables.
"""

# === DEFINE THE ANALYTICAL QUESTION ===

CUSTOM_QUERY_DECISION: Final[str] = r"""
I want to compare the average Glucose lab result
across patient age groups.

The result should have one row per age_group.

The information I need requires three tables:
 - age_group is in patients,
 - visit_id links patients to visits,
 - result_value (for test_name = 'Glucose') is in lab_results.
"""

# === WRITE THE SQL QUERY ===

CUSTOM_SQL_QUERY: Final[str] = """
SELECT
    p.age_group,
    ROUND(AVG(lr.result_value), 1) AS avg_glucose,
    COUNT(lr.lab_result_id) AS test_count
FROM patients AS p
JOIN visits AS v
    ON p.patient_id = v.patient_id
JOIN lab_results AS lr
    ON v.visit_id = lr.visit_id
WHERE lr.test_name = 'Glucose'
GROUP BY
    p.age_group
ORDER BY
    p.age_group;
"""

# === CHOOSE A VISUALIZATION ===

CUSTOM_CHART_DECISION: Final[str] = r"""
The query result has one numeric value
(average glucose) for each age group.

A bar chart works for comparing
a numeric value across named categories.
"""


# === DEFINE THE MAIN FUNCTION ===


def main() -> None:
    """Entry point when running this file as a Python script.

    This is where the instructions begin.

    Arguments: None.
    Returns: None.
    """
    log_header(LOG, "P05 - PYTHON AND SQL (HEALTH DOMAIN)")

    LOG.info("===================================")
    LOG.info("START main()")
    LOG.info("===================================")

    LOG.info("-------------------------------")
    LOG.info("01. LOAD the related tables.")
    LOG.info("-------------------------------")

    log_path(LOG, "clinics file", path=CLINIC_FILE)
    log_path(LOG, "patients file", path=PATIENT_FILE)
    log_path(LOG, "visits file", path=VISIT_FILE)
    log_path(LOG, "lab results file", path=LAB_RESULT_FILE)

    clinics_df: pd.DataFrame = pd.read_csv(CLINIC_FILE)
    patients_df: pd.DataFrame = pd.read_csv(PATIENT_FILE)
    visits_df: pd.DataFrame = pd.read_csv(VISIT_FILE)
    lab_results_df: pd.DataFrame = pd.read_csv(LAB_RESULT_FILE)

    LOG.info("Related tables loaded successfully.")

    LOG.info("-------------------------------")
    LOG.info("02. INSPECT the grain and keys.")
    LOG.info("-------------------------------")

    LOG.info(f"Clinics grain: {CLINIC_GRAIN}")
    LOG.info(f"Patients grain: {PATIENT_GRAIN}")
    LOG.info(f"Visits grain: {VISIT_GRAIN}")
    LOG.info(f"Lab results grain: {LAB_RESULT_GRAIN}")

    LOG.info(f"Clinics columns: {clinics_df.columns.tolist()}")
    LOG.info(f"Patients columns: {patients_df.columns.tolist()}")
    LOG.info(f"Visits columns: {visits_df.columns.tolist()}")
    LOG.info(f"Lab results columns: {lab_results_df.columns.tolist()}")

    LOG.info(RELATIONSHIP_DECISION)

    LOG.info("-------------------------------")
    LOG.info("03. CREATE a SQLite database.")
    LOG.info("-------------------------------")

    log_path(LOG, "SQLite database", path=DATABASE_FILE)

    connection: sqlite3.Connection = sqlite3.connect(DATABASE_FILE)

    LOG.info("SQLite database connection created.")

    LOG.info("-------------------------------")
    LOG.info("04. LOAD the tables into SQLite.")
    LOG.info("-------------------------------")

    clinics_df.to_sql(
        "clinics",
        connection,
        if_exists="replace",
        index=False,
    )

    patients_df.to_sql(
        "patients",
        connection,
        if_exists="replace",
        index=False,
    )

    visits_df.to_sql(
        "visits",
        connection,
        if_exists="replace",
        index=False,
    )

    lab_results_df.to_sql(
        "lab_results",
        connection,
        if_exists="replace",
        index=False,
    )

    LOG.info("Related tables loaded into SQLite.")

    LOG.info("-------------------------------")
    LOG.info("05. QUERY across related tables with SQL.")
    LOG.info("-------------------------------")

    LOG.info(CUSTOM_QUERY_DECISION)
    LOG.info(f"\nSQL query:\n{CUSTOM_SQL_QUERY}")

    result_df: pd.DataFrame = pd.read_sql_query(
        CUSTOM_SQL_QUERY,
        connection,
    )

    LOG.info(f"\nQuery result:\n{result_df}")

    LOG.info("-------------------------------")
    LOG.info("06. VISUALIZE the query result with Python.")
    LOG.info("-------------------------------")

    LOG.info(CUSTOM_CHART_DECISION)

    glucose_ax = result_df.plot.bar(
        x="age_group",
        y="avg_glucose",
        legend=False,
    )

    # CUSTOM: The analyst can customize the returned Matplotlib Axes object.
    glucose_ax.set_title("Average Glucose Result by Patient Age Group")
    glucose_ax.set_xlabel("Age Group")
    glucose_ax.set_ylabel("Average Glucose (mg/dL)")

    CHART_DIR.mkdir(parents=True, exist_ok=True)

    save_chart(
        glucose_ax,
        CHART_PATH,
    )

    LOG.info(f"Chart saved successfully at {CHART_PATH}.")

    LOG.info("-------------------------------")
    LOG.info("07. SUMMARIZE what you found.")
    LOG.info("-------------------------------")

    # Run this app first.
    # Review the SQL result and visualization.
    # Then record your CUSTOM observations
    # in a simple multi-line raw string.

    LOG.info(r"""CUSTOM OBSERVATIONS:
    The SQL query connected information from
    the patients, visits, and lab_results tables,
    filtering for Glucose test results only.

    The result has one row per age group.

    I observed ...

    Based on this result, I would next like to explore ...
    """)

    LOG.info("-------------------------------")
    LOG.info("08. DISPLAY the visualization.")
    LOG.info("-------------------------------")

    LOG.info("In a script, call plt.show() at the end to display all charts.")
    LOG.info("Close all chart windows (with the close button) to continue.")

    plt.show()

    connection.close()

    LOG.info("===================================")
    LOG.info("END main() - Executed successfully!")
    LOG.info("===================================")


# === CONDITIONAL EXECUTION GUARD ===

if __name__ == "__main__":
    main()



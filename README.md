# DecisionLab — Universal Business Intelligence & Decision Simulator

Turn your business data into better decisions. Upload a dataset, describe what you want to know, and DecisionLab identifies relevant columns, performs analysis, generates visualizations, and lets you simulate decisions.

## Quick start

```bash
# from the P4. Webbase_Dashboard directory
.venv\Scripts\activate
cd DecisionLab
streamlit run app.py
```

## What makes it different

DecisionLab is **not** a fixed KPI dashboard. It adapts to *your* uploaded data:

```
Upload → Understand → Ask → Analyze → Simulate → Export
```

Works with retail, online services, construction/electrical estimation, consulting, HR, sales, marketing, finance, and project-based businesses — no industry selection required.

## Tech stack

| Layer | Technology |
|-------|-----------|
| App framework | Streamlit |
| Data processing | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn (Plotly optional) |
| Persistence | SQLite (sqlite3) |
| Exports | CSV, Excel (xlsxwriter) |

No AI/ML, no paid APIs — the initial version is fully rule-based.

## Project structure

```
DecisionLab/
    app.py                  # Home / welcome page
    components.py           # Shared UI (logo, footer, CSS)
    requirements.txt
    services/               # Analytics engine, question engine, etc.
        upload_service.py
        profiling_service.py
        column_mapping_service.py
        question_engine.py
        analytics_engine.py
        scenario_engine.py
        insight_engine.py
        visualization_service.py
        report_service.py
    pages/                  # Streamlit multipage
        1_📁_Upload_Data.py
        2_🔍_Understand_Data.py
        3_❓_Ask_Question.py
        4_📊_Analysis_Workspace.py
        5_🧮_Scenario_Simulator.py
        6_🧹_Data_Quality.py
        7_💾_Saved_Projects.py
    database/
        database.py         # SQLite schema + helpers
    data/                   # Sample datasets
        sample_sales.csv
        sample_employees.csv
        sample_services.csv
    static/
        logo.svg
        css/custom.css
        js/custom.js
```

## Modules

1. **Data Upload** — CSV/Excel, validation, preview, multiple files.
2. **Automatic Data Understanding** — column role inference + user confirmation.
3. **Ask a Question** — natural input + suggested questions + goal buttons.
4. **Question Interpretation** — rule-based parser (metric, grouping, operation).
5. **Automatic Column Selection** — maps question to confirmed columns.
6. **Universal Analytics Engine** — sum, mean, median, IQR, growth, correlation, outliers.
7. **Adaptive Business Analysis** — revenue/expense/performance/service-aware output.
8. **Decision Simulator** — what-if scenarios with documented financial formulas.
9. **Data Quality** — missing values, duplicates, outliers, safe cleaning.
10. **Automatic Insights** — evidence-based, only when the calculation is valid.
11. **Visualizations** — bar, line, pie, histogram, scatter, box, heatmap.
12. **Multiple Files** — (planned) join suggestion and validation.
13. **SQLite Persistence** — projects, mappings, scenarios, preferences.
14. **Exports** — CSV results, summary reports, cleaned datasets.

## Footer

Every page displays: **Developed by: Manahil Tahir**
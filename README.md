# Preventive Care Risk Pipeline

An end-to-end data engineering pipeline that ingests patient EHR data, transforms it through a medallion architecture, and scores hospitalization risk to identify candidates for preventive care interventions.

---

## Problem Statement

Preventable hospitalizations cost the US healthcare system over $30 billion annually. Patients with chronic conditions like diabetes, hypertension, and congestive heart failure are frequently hospitalized due to missed follow-ups, medication non-adherence, and undetected clinical deterioration — all of which can be identified early through data.

This pipeline ingests multi-source patient data, engineers risk features, and produces a scored patient list that care teams can use to prioritize outreach before a hospitalization occurs.

---

## Architecture

```
Raw CSVs (Bronze)
        ↓
PatientDataExtractor
        ↓
PatientDataTransformer (Silver)
        ↓
PatientRiskLoader + Risk Scoring (Gold)
        ↓
patient_risk_scores.csv
```

---

## Data Sources

Six synthetic datasets generated to mirror real EHR data structures:

| Table | Rows | Description |
|---|---|---|
| patient_demographics.csv | 1,000 | Patient demographics and social determinants |
| patient_vitals.csv | 1,000 | Clinical measurements per visit |
| patient_diagnoses.csv | 1,000 | ICD-10 diagnoses and condition flags |
| patient_medications.csv | 1,000 | Prescriptions and adherence data |
| patient_utilization.csv | 1,000 | ED visits, inpatient admits, visit history |
| patient_labs.csv | 1,000 | Lab results with LOINC codes |

---

## Risk Scoring Model

Each patient receives a risk score calculated from weighted clinical features:

| Feature | Weight |
|---|---|
| Inpatient admits (12mo) | 3x |
| CHF diagnosis | 3x |
| ED visits (12mo) | 2x |
| Diabetes diagnosis | 2x |
| Low medication adherence | 2x |
| High risk medication | 2x |
| Low oxygen saturation | 2x |
| Abnormal lab results | 1x each |
| Hypertension | 1x |
| High blood pressure vitals | 1x |
| No-show appointments | 1x each |

**Risk Tiers:**
- Low: score 0–5
- Medium: score 6–15
- High: score 16+

---

## Project Structure

```
preventive-care-risk-pipeline/
├── data/
│   ├── raw/                  # Source CSV files (bronze layer)
│   └── output/                # Risk scores output (gold layer)
├── src/
│   ├── extract/
│   │   └── extractor.py       # PatientDataExtractor
│   ├── transform/
│   │   └── transformer.py     # PatientDataTransformer
│   └── load/
│       └── loader.py          # PatientRiskLoader
├── tests/
│   ├── test_extractor.py      # 8 unit tests
│   └── test_transformer.py    # 10 unit tests
├── main.py                    # Pipeline entry point
├── requirements.txt
└── README.md
```

---

## How to Run

**1. Clone the repo**
```bash
git clone https://github.com/CharlieMalick/Preventative-Care-Risk-Pipeline.git
cd Preventative-Care-Risk-Pipeline
```

**2. Set up environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Run the pipeline**
```bash
python main.py
```

**4. Run tests**
```bash
pytest tests/ -v
```

Output is saved to `data/output/patient_risk_scores.csv`.

---

## Tech Stack

- **Python 3.11**
- **pandas** — data ingestion, transformation, feature engineering
- **SQLAlchemy** — database connectivity (PostgreSQL integration in progress)
- **pytest** — unit testing
- **Great Expectations** — data validation (planned)

---

## Roadmap

- [ ] PostgreSQL integration via AWS RDS
- [ ] Great Expectations data quality checks
- [ ] Apache Airflow DAG for pipeline orchestration
- [ ] dbt models for silver/gold transformations
- [ ] Streamlit dashboard for risk tier visualization

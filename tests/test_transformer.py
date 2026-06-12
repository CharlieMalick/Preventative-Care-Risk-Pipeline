import pytest
import pandas as pd
import sys
sys.path.append('.')
from src.extract.extractor import PatientDataExtractor
from src.transform.transformer import PatientDataTransformer

@pytest.fixture
def transformed_data():
    extractor = PatientDataExtractor(data_dir="data/raw")
    raw_data = extractor.run()
    transformer = PatientDataTransformer(data=raw_data)
    return transformer.run()

def test_all_tables_transformed(transformed_data):
    expected = ['demographics', 'vitals', 'diagnoses', 'medications', 'utilization', 'labs']
    for table in expected:
        assert table in transformed_data

def test_age_derived_correctly(transformed_data):
    df = transformed_data['demographics']
    assert 'age' in df.columns
    assert df['age'].min() >= 18
    assert df['age'].max() <= 120

def test_zip_codes_are_valid(transformed_data):
    df = transformed_data['demographics']
    valid_zips = df['zip'].dropna()
    assert valid_zips.str.match(r'^\d{5}$').all()

def test_bmi_calculated_in_vitals(transformed_data):
    df = transformed_data['vitals']
    assert 'bmi_calculated' in df.columns
    assert df['bmi_calculated'].min() > 0

def test_high_bp_flag_logic(transformed_data):
    df = transformed_data['vitals']
    high_bp = df[df['high_bp_flag'] == True]
    assert ((high_bp['systolic_bp'] >= 140) | (high_bp['diastolic_bp'] >= 90)).all()

def test_diagnosis_flags_are_boolean(transformed_data):
    df = transformed_data['diagnoses']
    for col in ['chronic_flag', 'diabetes_flag', 'hypertension_flag', 'chf_flag']:
        assert df[col].dtype == bool, f"{col} is not boolean"

def test_low_adherence_flag_logic(transformed_data):
    df = transformed_data['medications']
    low_adherence = df[df['low_adherence_flag'] == True]
    assert (low_adherence['refill_adherence_pct'] < 50).all()

def test_high_ed_use_flag_logic(transformed_data):
    df = transformed_data['utilization']
    high_ed = df[df['high_ed_use_flag'] == True]
    assert (high_ed['ed_visits_12mo'] >= 3).all()

def test_lab_flags_are_boolean(transformed_data):
    df = transformed_data['labs']
    for col in ['abnormal_flag', 'critical_flag']:
        assert df[col].dtype == bool, f"{col} is not boolean"

def test_no_tables_are_empty(transformed_data):
    for table_name, df in transformed_data.items():
        assert len(df) > 0, f"{table_name} is empty after transformation"
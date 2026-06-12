import pytest
import pandas as pd
import sys
sys.path.append('.')
from src.extract.extractor import PatientDataExtractor

@pytest.fixture
def extractor():
    return PatientDataExtractor(data_dir="data/raw")

def test_extractor_loads_all_tables(extractor):
    data = extractor.extract_all()
    assert len(data) == 6

def test_demographics_columns(extractor):
    df = extractor.extract_table('demographics')
    expected_cols = ['patient_id', 'first_name', 'last_name', 'date_of_birth',
                     'gender', 'race', 'ethnicity', 'zip', 'insurance_type',
                     'primary_language', 'smoking_status', 'alcohol_use',
                     'bmi', 'employment_status']
    for col in expected_cols:
        assert col in df.columns, f"Missing column: {col}"

def test_all_tables_have_1000_rows(extractor):
    data = extractor.extract_all()
    for table_name, df in data.items():
        assert len(df) == 1000, f"{table_name} has {len(df)} rows, expected 1000"

def test_patient_id_is_unique_in_demographics(extractor):
    df = extractor.extract_table('demographics')
    assert df['patient_id'].nunique() == len(df)

def test_patient_id_range(extractor):
    df = extractor.extract_table('demographics')
    assert df['patient_id'].min() == 1
    assert df['patient_id'].max() == 1000

def test_no_null_patient_ids(extractor):
    data = extractor.extract_all()
    for table_name, df in data.items():
        assert df['patient_id'].isnull().sum() == 0, f"{table_name} has null patient_ids"

def test_validate_table_returns_true(extractor):
    df = extractor.extract_table('demographics')
    assert extractor.validate_table(df, 'demographics') == True

def test_invalid_file_raises_error(extractor):
    with pytest.raises(KeyError):
        extractor.extract_table('nonexistent_table')
import pandas as pd
import logging
import re

logger = logging.getLogger(__name__)

class PatientDataTransformer:

    def __init__(self, data: dict):
        self.data = data

    def transform_demographics(self) -> pd.DataFrame:
        df = self.data['demographics'].copy()

        # Derive age from date_of_birth
        df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
        today = pd.Timestamp.today()
        df['age'] = ((today - df['date_of_birth']).dt.days // 365).astype(int)

        # Clean zip codes — keep only valid 5-digit US zips
        df['zip'] = df['zip'].astype(str).apply(
            lambda x: x if re.match(r'^\d{5}$', x) else None
        )

        # Standardize gender
        df['gender'] = df['gender'].str.strip().str.title()

        logger.info(f"Demographics transformed: {len(df)} rows")
        return df

    def transform_vitals(self) -> pd.DataFrame:
        df = self.data['vitals'].copy()

        df['measurement_date'] = pd.to_datetime(df['measurement_date'])

        # Flag abnormal vitals
        df['high_bp_flag'] = (df['systolic_bp'] >= 140) | (df['diastolic_bp'] >= 90)
        df['low_oxygen_flag'] = df['oxygen_saturation'] < 92

        # Calculate BMI from weight and height
        df['bmi_calculated'] = (df['weight_kg'] / ((df['height_cm'] / 100) ** 2)).round(1)
        df['high_bmi_flag'] = df['bmi_calculated'] >= 30

        logger.info(f"Vitals transformed: {len(df)} rows")
        return df

    def transform_diagnoses(self) -> pd.DataFrame:
        df = self.data['diagnoses'].copy()

        df['encounter_date'] = pd.to_datetime(df['encounter_date'])
        df['condition_onset_date'] = pd.to_datetime(df['condition_onset_date'])

        # Convert flags to boolean
        for col in ['chronic_flag', 'diabetes_flag', 'hypertension_flag', 'chf_flag']:
            df[col] = df[col].str.strip().str.upper() == 'YES'

        logger.info(f"Diagnoses transformed: {len(df)} rows")
        return df

    def transform_medications(self) -> pd.DataFrame:
        df = self.data['medications'].copy()

        df['prescribe_date'] = pd.to_datetime(df['prescribe_date'])

        # Convert flags to boolean
        df['active_flag'] = df['active_flag'].str.strip().str.upper() == 'YES'
        df['high_risk_med_flag'] = df['high_risk_med_flag'].str.strip().str.upper() == 'YES'

        # Flag low adherence
        df['low_adherence_flag'] = df['refill_adherence_pct'] < 50

        logger.info(f"Medications transformed: {len(df)} rows")
        return df

    def transform_utilization(self) -> pd.DataFrame:
        df = self.data['utilization'].copy()

        df['visit_date'] = pd.to_datetime(df['visit_date'])

        # Convert flags to boolean
        df['pcp_assigned'] = df['pcp_assigned'].str.strip().str.upper() == 'YES'
        df['readmit_30d'] = df['readmit_30d'].str.strip().str.upper() == 'YES'

        # Flag high utilization patients
        df['high_ed_use_flag'] = df['ed_visits_12mo'] >= 3
        df['high_admits_flag'] = df['inpatient_admits_12mo'] >= 2

        logger.info(f"Utilization transformed: {len(df)} rows")
        return df

    def transform_labs(self) -> pd.DataFrame:
        df = self.data['labs'].copy()

        df['lab_date'] = pd.to_datetime(df['lab_date'])

        # Convert flags to boolean
        df['abnormal_flag'] = df['abnormal_flag'].str.strip().str.upper() == 'YES'
        df['critical_flag'] = df['critical_flag'].str.strip().str.upper() == 'YES'

        logger.info(f"Labs transformed: {len(df)} rows")
        return df

    def run(self) -> dict:
        logger.info("Starting transformation pipeline")
        transformed = {
            'demographics': self.transform_demographics(),
            'vitals': self.transform_vitals(),
            'diagnoses': self.transform_diagnoses(),
            'medications': self.transform_medications(),
            'utilization': self.transform_utilization(),
            'labs': self.transform_labs()
        }
        logger.info("Transformation complete")
        return transformed


if __name__ == "__main__":
    import sys
    sys.path.append('.')
    from src.extract.extractor import PatientDataExtractor

    extractor = PatientDataExtractor(data_dir="data/raw")
    raw_data = extractor.run()

    transformer = PatientDataTransformer(data=raw_data)
    transformed_data = transformer.run()
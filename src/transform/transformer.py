import pandas as pd
import logging
import re

logger = logging.getLogger(__name__)

class PatientDataTransformer:
    """
    Cleans the raw patient tables and engineers the derived features
    (age, BMI, boolean flags, etc.) that the load layer's risk model
    depends on. This is the silver layer of the medallion architecture.
    """

    def __init__(self, data: dict):
        """
        Args:
            data: Dict of raw DataFrames keyed by table name, as returned
                by PatientDataExtractor.run().
        """
        self.data = data

    def transform_demographics(self) -> pd.DataFrame:
        """Derive age, drop minors, and clean zip/gender fields."""
        df = self.data['demographics'].copy()

        # Derive age from date_of_birth
        df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
        today = pd.Timestamp.today()
        df['age'] = ((today - df['date_of_birth']).dt.days // 365).astype(int)

        # Filter out non-adult patients
        df = df[df['age'] >= 18].reset_index(drop=True)

        # Clean zip codes — keep only valid 5-digit US zips
        df['zip'] = df['zip'].astype(str).apply(
            lambda x: x if re.match(r'^\d{5}$', x) else None
        )

        # Standardize gender
        df['gender'] = df['gender'].str.strip().str.title()

        logger.info(f"Demographics transformed: {len(df)} rows")
        return df

    def transform_vitals(self) -> pd.DataFrame:
        """Flag abnormal vitals (high BP, low oxygen) and calculate BMI."""
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
        """Parse encounter/onset dates and convert YES/NO flags to booleans."""
        df = self.data['diagnoses'].copy()

        df['encounter_date'] = pd.to_datetime(df['encounter_date'])
        df['condition_onset_date'] = pd.to_datetime(df['condition_onset_date'])

        # Convert flags to boolean
        for col in ['chronic_flag', 'diabetes_flag', 'hypertension_flag', 'chf_flag']:
            df[col] = df[col].str.strip().str.upper() == 'YES'

        logger.info(f"Diagnoses transformed: {len(df)} rows")
        return df

    def transform_medications(self) -> pd.DataFrame:
        """Convert flags to booleans and flag patients with low refill adherence."""
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
        """Convert flags to booleans and flag patients with high ED/inpatient use."""
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
        """Parse lab dates and convert abnormal/critical flags to booleans."""
        df = self.data['labs'].copy()

        df['lab_date'] = pd.to_datetime(df['lab_date'])

        # Convert flags to boolean
        df['abnormal_flag'] = df['abnormal_flag'].str.strip().str.upper() == 'YES'
        df['critical_flag'] = df['critical_flag'].str.strip().str.upper() == 'YES'

        logger.info(f"Labs transformed: {len(df)} rows")
        return df

    def run(self) -> dict:
        """Run all six per-table transforms. Entry point for the transform phase."""
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
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

class PatientRiskLoader:

    def __init__(self, transformed_data: dict, output_dir: str):
        self.data = transformed_data
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def build_patient_profile(self) -> pd.DataFrame:
        # Start with demographics as the spine
        demo = self.data['demographics'][['patient_id', 'age', 'gender', 'insurance_type', 'bmi']]

        # Aggregate vitals per patient
        vitals = self.data['vitals'].groupby('patient_id').agg(
            high_bp_flag=('high_bp_flag', 'max'),
            low_oxygen_flag=('low_oxygen_flag', 'max'),
            high_bmi_flag=('high_bmi_flag', 'max')
        ).reset_index()

        # Aggregate diagnoses per patient
        diagnoses = self.data['diagnoses'].groupby('patient_id').agg(
            diabetes_flag=('diabetes_flag', 'max'),
            hypertension_flag=('hypertension_flag', 'max'),
            chf_flag=('chf_flag', 'max'),
            chronic_flag=('chronic_flag', 'max'),
            max_comorbidities=('comorbidity_count', 'max')
        ).reset_index()

        # Aggregate medications per patient
        medications = self.data['medications'].groupby('patient_id').agg(
            low_adherence_flag=('low_adherence_flag', 'max'),
            high_risk_med_flag=('high_risk_med_flag', 'max'),
            avg_adherence=('refill_adherence_pct', 'mean')
        ).reset_index()

        # Get utilization features per patient
        utilization = self.data['utilization'].groupby('patient_id').agg(
            ed_visits_12mo=('ed_visits_12mo', 'max'),
            inpatient_admits_12mo=('inpatient_admits_12mo', 'max'),
            high_ed_use_flag=('high_ed_use_flag', 'max'),
            high_admits_flag=('high_admits_flag', 'max'),
            readmit_30d=('readmit_30d', 'max'),
            no_show_count=('no_show_count', 'max')
        ).reset_index()

        # Aggregate labs per patient
        labs = self.data['labs'].groupby('patient_id').agg(
            abnormal_lab_flag=('abnormal_flag', 'max'),
            critical_lab_flag=('critical_flag', 'max'),
            abnormal_lab_count=('abnormal_flag', 'sum')
        ).reset_index()

        # Join everything to demographics spine
        profile = demo.copy()
        for table in [vitals, diagnoses, medications, utilization, labs]:
            profile = profile.merge(table, on='patient_id', how='left')

        profile = profile.fillna(False)
        logger.info(f"Patient profile built: {len(profile)} patients, {len(profile.columns)} features")
        return profile

    def calculate_risk_score(self, profile: pd.DataFrame) -> pd.DataFrame:
        df = profile.copy()

        # Score each risk factor
        df['risk_score'] = (
            df['ed_visits_12mo'] * 2 +
            df['inpatient_admits_12mo'] * 3 +
            df['chf_flag'].astype(int) * 3 +
            df['diabetes_flag'].astype(int) * 2 +
            df['hypertension_flag'].astype(int) * 1 +
            df['low_adherence_flag'].astype(int) * 2 +
            df['high_risk_med_flag'].astype(int) * 2 +
            df['abnormal_lab_count'] * 1 +
            df['no_show_count'] * 1 +
            df['high_bp_flag'].astype(int) * 1 +
            df['low_oxygen_flag'].astype(int) * 2
        )

        # Assign risk tier
        df['risk_tier'] = pd.cut(
            df['risk_score'],
            bins=[-1, 5, 15, float('inf')],
            labels=['Low', 'Medium', 'High']
        )

        logger.info(f"Risk scores calculated")
        logger.info(f"Risk distribution:\n{df['risk_tier'].value_counts()}")
        return df

    def save_output(self, df: pd.DataFrame) -> None:
        output_cols = [
            'patient_id', 'age', 'gender', 'insurance_type',
            'diabetes_flag', 'hypertension_flag', 'chf_flag',
            'ed_visits_12mo', 'inpatient_admits_12mo',
            'low_adherence_flag', 'high_risk_med_flag',
            'abnormal_lab_count', 'risk_score', 'risk_tier'
        ]
        output = df[output_cols]
        filepath = os.path.join(self.output_dir, 'patient_risk_scores.csv')
        output.to_csv(filepath, index=False)
        logger.info(f"Risk scores saved to {filepath}")

    def run(self) -> pd.DataFrame:
        logger.info("Starting load pipeline")
        profile = self.build_patient_profile()
        scored = self.calculate_risk_score(profile)
        self.save_output(scored)
        logger.info("Load pipeline complete")
        return scored


if __name__ == "__main__":
    import sys
    sys.path.append('.')
    from src.extract.extractor import PatientDataExtractor
    from src.transform.transformer import PatientDataTransformer

    extractor = PatientDataExtractor(data_dir="data/raw")
    raw_data = extractor.run()

    transformer = PatientDataTransformer(data=raw_data)
    transformed_data = transformer.run()

    loader = PatientRiskLoader(
        transformed_data=transformed_data,
        output_dir="data/output"
    )
    results = loader.run()
    print(results[['patient_id', 'risk_score', 'risk_tier']].head(10))
import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatientDataExtractor:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.tables = {
            'demographics' : 'patient_demographics.csv',
            'vitals' : 'patient_vitals.csv',
            'diagnoses' : 'patient_diagnoses.csv',
            'medications' : 'patient_medications.csv',
            'utilization' : 'patient_utilization.csv',
            'labs' : 'patient_labs.csv'
        }
    
    def extract_table(self, table_name: str) -> pd.DataFrame:
        filename = self.tables[table_name]
        filepath = os.path.join(self.data_dir, filename)

        try:
            df = pd.read_csv(filepath)
            logger.info(f"Extracted {table_name}: {len(df)} rows, {len(df.columns)} columns")
            return df
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Error extracting {table_name}: {e}")
            raise
    
    def extract_all(self) -> dict:
        data = {}
        for table_name in self.tables:
            data[table_name] = self.extract_table(table_name)
        return data

    def validate_table(self, df: pd.DataFrame, table_name: str) -> bool:
        if df is None or df.empty:
            logger.error(f"{table_name} is empty")
            return False
        if len(df) < 100:
            logger.warning(f"{table_name} has fewer than 100 rows: {len(df)}")
        if df.duplicated().sum() > 0:
            logger.warning(f"{table_name} has {df.duplicated().sum()} duplicate rows")
        logger.info(f"{table_name} validation passed")
        return True

    def run(self) -> dict:
        logger.info("Starting extraction pipeline")
        data = self.extract_all()
        for table_name, df in data.items():
            self.validate_table(df, table_name)
        logger.info("Extraction complete")
        return data

if __name__ == "__main__":
    extractor = PatientDataExtractor(data_dir="data/raw")
    data = extractor.run()
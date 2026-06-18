import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PatientDataExtractor:
    """
    Reads raw patient EHR CSVs from disk (the bronze layer) and validates
    each table before it's passed downstream to the transform layer.
    """

    def __init__(self, data_dir: str):
        """
        Args:
            data_dir: Directory containing the six raw patient CSV files.
        """
        self.data_dir = data_dir
        # Maps a short table key to its source CSV filename, so callers can
        # refer to tables by name (e.g. 'vitals') instead of hardcoding paths.
        self.tables = {
            'demographics' : 'patient_demographics.csv',
            'vitals' : 'patient_vitals.csv',
            'diagnoses' : 'patient_diagnoses.csv',
            'medications' : 'patient_medications.csv',
            'utilization' : 'patient_utilization.csv',
            'labs' : 'patient_labs.csv'
        }

    def extract_table(self, table_name: str) -> pd.DataFrame:
        """Load a single raw table by its short name (e.g. 'demographics')."""
        filename = self.tables[table_name]
        filepath = os.path.join(self.data_dir, filename)

        try:
            df = pd.read_csv(filepath)
            logger.info(f"Extracted {table_name}: {len(df)} rows, {len(df.columns)} columns")
            return df
        except FileNotFoundError:
            # Surface a clear error pointing at the missing file rather than
            # letting pandas' generic traceback be the only signal.
            logger.error(f"File not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Error extracting {table_name}: {e}")
            raise

    def extract_all(self) -> dict:
        """Load every configured table into a dict keyed by table name."""
        data = {}
        for table_name in self.tables:
            data[table_name] = self.extract_table(table_name)
        return data

    def validate_table(self, df: pd.DataFrame, table_name: str) -> bool:
        """
        Run lightweight sanity checks on an extracted table. This is not a
        hard data-quality gate (see the Great Expectations item on the
        roadmap) — it just logs warnings/errors so issues are visible early.
        """
        if df is None or df.empty:
            logger.error(f"{table_name} is empty")
            return False
        if len(df) < 100:
            # Synthetic datasets are generated with ~1,000 rows each, so a
            # much smaller table likely indicates a partial/corrupt extract.
            logger.warning(f"{table_name} has fewer than 100 rows: {len(df)}")
        if df.duplicated().sum() > 0:
            logger.warning(f"{table_name} has {df.duplicated().sum()} duplicate rows")
        logger.info(f"{table_name} validation passed")
        return True

    def run(self) -> dict:
        """Extract and validate all tables. Entry point for the extract phase."""
        logger.info("Starting extraction pipeline")
        data = self.extract_all()
        for table_name, df in data.items():
            self.validate_table(df, table_name)
        logger.info("Extraction complete")
        return data


if __name__ == "__main__":
    extractor = PatientDataExtractor(data_dir="data/raw")
    data = extractor.run()

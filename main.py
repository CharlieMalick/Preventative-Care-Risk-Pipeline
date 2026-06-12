import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

from src.extract.extractor import PatientDataExtractor
from src.transform.transformer import PatientDataTransformer
from src.load.loader import PatientRiskLoader


def main():
    logger.info("========================================")
    logger.info("Starting Preventive Care Risk Pipeline")
    logger.info("========================================")

    # Extract
    logger.info("Phase 1: Extraction")
    extractor = PatientDataExtractor(data_dir="data/raw")
    raw_data = extractor.run()

    # Transform
    logger.info("Phase 2: Transformation")
    transformer = PatientDataTransformer(data=raw_data)
    transformed_data = transformer.run()

    # Load
    logger.info("Phase 3: Load & Risk Scoring")
    loader = PatientRiskLoader(
        transformed_data=transformed_data,
        output_dir="data/output"
    )
    results = loader.run()

    # Summary
    logger.info("========================================")
    logger.info("Pipeline Complete")
    logger.info(f"Total patients scored: {len(results)}")
    logger.info(f"Risk distribution:\n{results['risk_tier'].value_counts()}")
    logger.info("Output saved to data/output/patient_risk_scores.csv")
    logger.info("========================================")


if __name__ == "__main__":
    main()
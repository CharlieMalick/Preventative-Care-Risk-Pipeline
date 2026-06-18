"""
Preventive Care Risk Pipeline.

Top-level package for the patient risk-scoring pipeline. Contains three
sub-packages that implement a medallion (bronze/silver/gold) architecture:

- extract:   reads raw patient EHR CSVs (bronze layer)
- transform: cleans and engineers features from the raw data (silver layer)
- load:      aggregates features per patient and computes risk scores (gold layer)
"""

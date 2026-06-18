"""
Extract layer (bronze).

Provides PatientDataExtractor, which reads raw patient EHR CSVs from disk
and performs basic validation (non-empty, row-count, duplicate checks)
before handing the data off to the transform layer.
"""

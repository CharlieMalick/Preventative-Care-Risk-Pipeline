"""
Load layer (gold).

Provides PatientRiskLoader, which joins the transformed per-table data
into a single patient profile, calculates a weighted risk score and tier
for each patient, and writes the final scored output to disk.
"""

"""
Generate healthy synthetic healthcare examples.

All data is clearly synthetic. No real patient data is used or implied.
Each example pairs a source record with a correctly grounded output text.
"""

from clinaiqa.data.schemas import DocType, HealthyExample

_CMS_FACILITY_RECORDS = [
    {
        "facility_id": "SYN-001",
        "facility_name": "Greenfield Skilled Nursing Facility",
        "overall_rating": 4,
        "staffing_rating": 3,
        "quality_rating": 4,
        "rn_hours_per_resident_per_day": 0.62,
        "total_nurse_hours_per_resident_per_day": 3.85,
        "health_inspection_score": 72,
        "total_beds": 120,
        "occupancy_rate": 0.81,
        "state": "NY",
    },
    {
        "facility_id": "SYN-002",
        "facility_name": "Riverside Care Center",
        "overall_rating": 2,
        "staffing_rating": 2,
        "quality_rating": 3,
        "rn_hours_per_resident_per_day": 0.41,
        "total_nurse_hours_per_resident_per_day": 2.90,
        "health_inspection_score": 58,
        "total_beds": 85,
        "occupancy_rate": 0.73,
        "state": "OH",
    },
    {
        "facility_id": "SYN-003",
        "facility_name": "Summit Heights Rehabilitation",
        "overall_rating": 5,
        "staffing_rating": 5,
        "quality_rating": 5,
        "rn_hours_per_resident_per_day": 0.89,
        "total_nurse_hours_per_resident_per_day": 4.72,
        "health_inspection_score": 91,
        "total_beds": 200,
        "occupancy_rate": 0.94,
        "state": "CA",
    },
    {
        "facility_id": "SYN-004",
        "facility_name": "Maplewood Long-Term Care",
        "overall_rating": 3,
        "staffing_rating": 3,
        "quality_rating": 3,
        "rn_hours_per_resident_per_day": 0.55,
        "total_nurse_hours_per_resident_per_day": 3.40,
        "health_inspection_score": 65,
        "total_beds": 160,
        "occupancy_rate": 0.78,
        "state": "TX",
    },
    {
        "facility_id": "SYN-005",
        "facility_name": "Lakeside Senior Living",
        "overall_rating": 4,
        "staffing_rating": 4,
        "quality_rating": 4,
        "rn_hours_per_resident_per_day": 0.74,
        "total_nurse_hours_per_resident_per_day": 4.10,
        "health_inspection_score": 83,
        "total_beds": 140,
        "occupancy_rate": 0.88,
        "state": "FL",
    },
    {
        "facility_id": "SYN-006",
        "facility_name": "Pinecrest Nursing and Rehab",
        "overall_rating": 1,
        "staffing_rating": 1,
        "quality_rating": 2,
        "rn_hours_per_resident_per_day": 0.28,
        "total_nurse_hours_per_resident_per_day": 2.10,
        "health_inspection_score": 42,
        "total_beds": 95,
        "occupancy_rate": 0.65,
        "state": "IL",
    },
    {
        "facility_id": "SYN-007",
        "facility_name": "Valley View Skilled Care",
        "overall_rating": 3,
        "staffing_rating": 4,
        "quality_rating": 3,
        "rn_hours_per_resident_per_day": 0.68,
        "total_nurse_hours_per_resident_per_day": 3.65,
        "health_inspection_score": 70,
        "total_beds": 110,
        "occupancy_rate": 0.82,
        "state": "PA",
    },
]

_CMS_OUTPUTS = [
    "Greenfield Skilled Nursing Facility (SYN-001) holds an overall CMS rating of 4 out of 5 stars. "
    "Registered nurse hours per resident per day are 0.62, and total nurse hours reach 3.85. "
    "The facility operates 120 beds at an 81 percent occupancy rate and achieved a health inspection score of 72. "
    "This report is generated from structured CMS data and does not constitute a clinical recommendation.",

    "Riverside Care Center (SYN-002) carries an overall CMS rating of 2 out of 5 stars. "
    "Staffing levels are rated 2 stars, with RN hours per resident per day at 0.41 and total nurse hours at 2.90. "
    "The facility's health inspection score is 58, reflecting areas requiring improvement. "
    "This report is generated from structured CMS data and does not constitute a clinical recommendation.",

    "Summit Heights Rehabilitation (SYN-003) achieves the highest CMS rating of 5 stars across all categories. "
    "RN hours per resident per day stand at 0.89, and total nurse hours reach 4.72. "
    "With 200 beds at 94 percent occupancy and a health inspection score of 91, the facility demonstrates strong performance. "
    "This report is generated from structured CMS data and does not constitute a clinical recommendation.",

    "Maplewood Long-Term Care (SYN-004) holds a 3-star overall CMS rating with consistent 3-star scores across staffing and quality. "
    "RN hours per resident per day are 0.55, and total nurse hours are 3.40. "
    "Operating 160 beds at 78 percent occupancy, the facility scored 65 on health inspections. "
    "This report is generated from structured CMS data and does not constitute a clinical recommendation.",

    "Lakeside Senior Living (SYN-005) is rated 4 stars overall by CMS, with 4-star scores in both staffing and quality. "
    "RN hours per resident per day are 0.74, and total nurse hours are 4.10. "
    "The facility maintains 140 beds at 88 percent occupancy with a health inspection score of 83. "
    "This report is generated from structured CMS data and does not constitute a clinical recommendation.",

    "Pinecrest Nursing and Rehab (SYN-006) holds a 1-star overall CMS rating and a 1-star staffing rating. "
    "RN hours per resident per day are 0.28, and total nurse hours are 2.10. "
    "The health inspection score of 42 and 65 percent occupancy across 95 beds indicate significant concerns. "
    "This report is generated from structured CMS data and does not constitute a clinical recommendation.",

    "Valley View Skilled Care (SYN-007) holds a 3-star overall CMS rating with a 4-star staffing score. "
    "RN hours per resident per day are 0.68, and total nurse hours are 3.65. "
    "The facility operates 110 beds at 82 percent occupancy with a health inspection score of 70. "
    "This report is generated from structured CMS data and does not constitute a clinical recommendation.",
]

_CLINICAL_GUIDELINE_RECORDS = [
    {
        "guideline_id": "GL-HF-001",
        "condition": "Heart Failure",
        "recommendation": "Patients with HFrEF should receive ACE inhibitor or ARB therapy unless contraindicated.",
        "evidence_level": "A",
        "source": "Synthetic Clinical Guideline Repository v1.0",
    },
    {
        "guideline_id": "GL-DM-001",
        "condition": "Type 2 Diabetes",
        "recommendation": "Metformin is the preferred initial pharmacologic agent for type 2 diabetes unless contraindicated.",
        "evidence_level": "A",
        "source": "Synthetic Clinical Guideline Repository v1.0",
    },
    {
        "guideline_id": "GL-HTN-001",
        "condition": "Hypertension",
        "recommendation": "For most patients with hypertension, first-line therapy includes thiazide diuretics, ACE inhibitors, ARBs, or calcium channel blockers.",
        "evidence_level": "A",
        "source": "Synthetic Clinical Guideline Repository v1.0",
    },
    {
        "guideline_id": "GL-COPD-001",
        "condition": "COPD",
        "recommendation": "Long-acting bronchodilators are the mainstay of maintenance therapy for symptomatic COPD.",
        "evidence_level": "A",
        "source": "Synthetic Clinical Guideline Repository v1.0",
    },
    {
        "guideline_id": "GL-AF-001",
        "condition": "Atrial Fibrillation",
        "recommendation": "Anticoagulation with a DOAC is recommended for patients with AF and a CHA2DS2-VASc score of 2 or more.",
        "evidence_level": "A",
        "source": "Synthetic Clinical Guideline Repository v1.0",
    },
    {
        "guideline_id": "GL-CKD-001",
        "condition": "Chronic Kidney Disease",
        "recommendation": "Blood pressure target for CKD patients with proteinuria is less than 130/80 mmHg.",
        "evidence_level": "B",
        "source": "Synthetic Clinical Guideline Repository v1.0",
    },
    {
        "guideline_id": "GL-DEPR-001",
        "condition": "Major Depressive Disorder",
        "recommendation": "SSRIs are the preferred first-line pharmacotherapy for major depressive disorder in adults.",
        "evidence_level": "A",
        "source": "Synthetic Clinical Guideline Repository v1.0",
    },
]

_GUIDELINE_OUTPUTS = [
    "According to Synthetic Clinical Guideline GL-HF-001, patients with HFrEF should receive ACE inhibitor or ARB therapy unless contraindicated. "
    "This recommendation carries an evidence level of A. "
    "This summary is for informational purposes only and does not constitute medical advice. Consult a qualified clinician before making treatment decisions.",

    "Synthetic Clinical Guideline GL-DM-001 recommends metformin as the preferred initial pharmacologic agent for type 2 diabetes unless contraindicated. "
    "This recommendation carries an evidence level of A. "
    "This summary is for informational purposes only and does not constitute medical advice. Consult a qualified clinician before making treatment decisions.",

    "Synthetic Clinical Guideline GL-HTN-001 states that for most patients with hypertension, first-line therapy includes thiazide diuretics, ACE inhibitors, ARBs, or calcium channel blockers. "
    "Evidence level is A. "
    "This summary is for informational purposes only and does not constitute medical advice. Consult a qualified clinician before making treatment decisions.",

    "Synthetic Clinical Guideline GL-COPD-001 specifies that long-acting bronchodilators are the mainstay of maintenance therapy for symptomatic COPD. "
    "This is an evidence level A recommendation. "
    "This summary is for informational purposes only and does not constitute medical advice. Consult a qualified clinician before making treatment decisions.",

    "Synthetic Clinical Guideline GL-AF-001 recommends anticoagulation with a DOAC for patients with AF and a CHA2DS2-VASc score of 2 or more. "
    "Evidence level is A. "
    "This summary is for informational purposes only and does not constitute medical advice. Consult a qualified clinician before making treatment decisions.",

    "Synthetic Clinical Guideline GL-CKD-001 sets a blood pressure target of less than 130/80 mmHg for CKD patients with proteinuria. "
    "This recommendation carries an evidence level of B. "
    "This summary is for informational purposes only and does not constitute medical advice. Consult a qualified clinician before making treatment decisions.",

    "Synthetic Clinical Guideline GL-DEPR-001 identifies SSRIs as the preferred first-line pharmacotherapy for major depressive disorder in adults. "
    "Evidence level is A. "
    "This summary is for informational purposes only and does not constitute medical advice. Consult a qualified clinician before making treatment decisions.",
]

_PATIENT_RECORDS = [
    {
        "patient_id": "PAT-SYN-001",
        "age": 67,
        "primary_diagnosis": "Type 2 Diabetes",
        "medications": ["Metformin 1000mg twice daily", "Lisinopril 10mg once daily"],
        "last_hba1c": 7.8,
        "last_bp": "138/86",
        "note": "Synthetic patient, no real individual represented.",
    },
    {
        "patient_id": "PAT-SYN-002",
        "age": 72,
        "primary_diagnosis": "Chronic Heart Failure with reduced ejection fraction",
        "medications": ["Lisinopril 5mg once daily", "Carvedilol 6.25mg twice daily", "Furosemide 40mg once daily"],
        "last_ef": "35%",
        "last_bnp": 420,
        "note": "Synthetic patient, no real individual represented.",
    },
    {
        "patient_id": "PAT-SYN-003",
        "age": 58,
        "primary_diagnosis": "Hypertension",
        "medications": ["Amlodipine 5mg once daily"],
        "last_bp": "142/90",
        "note": "Synthetic patient, no real individual represented.",
    },
    {
        "patient_id": "PAT-SYN-004",
        "age": 80,
        "primary_diagnosis": "Atrial Fibrillation",
        "medications": ["Apixaban 5mg twice daily", "Metoprolol succinate 50mg once daily"],
        "cha2ds2_vasc": 4,
        "note": "Synthetic patient, no real individual represented.",
    },
    {
        "patient_id": "PAT-SYN-005",
        "age": 63,
        "primary_diagnosis": "COPD, moderate severity",
        "medications": ["Tiotropium 18mcg inhaled once daily", "Albuterol 90mcg PRN"],
        "last_fev1_percent": 55,
        "note": "Synthetic patient, no real individual represented.",
    },
    {
        "patient_id": "PAT-SYN-006",
        "age": 45,
        "primary_diagnosis": "Major Depressive Disorder",
        "medications": ["Sertraline 50mg once daily"],
        "phq9_score": 14,
        "note": "Synthetic patient, no real individual represented.",
    },
    {
        "patient_id": "PAT-SYN-007",
        "age": 70,
        "primary_diagnosis": "Chronic Kidney Disease stage 3",
        "medications": ["Lisinopril 20mg once daily", "Amlodipine 10mg once daily"],
        "last_egfr": 38,
        "last_bp": "128/78",
        "note": "Synthetic patient, no real individual represented.",
    },
]

_PATIENT_OUTPUTS = [
    "Synthetic patient PAT-SYN-001 is a 67-year-old with a primary diagnosis of Type 2 Diabetes. "
    "Current medications include Metformin 1000mg twice daily and Lisinopril 10mg once daily. "
    "The most recent HbA1c is 7.8 percent and blood pressure is 138/86. "
    "This summary is derived from synthetic structured records and does not constitute medical advice. Consult a qualified clinician before making any treatment decisions.",

    "Synthetic patient PAT-SYN-002 is a 72-year-old with chronic heart failure with reduced ejection fraction. "
    "Current medications include Lisinopril 5mg once daily, Carvedilol 6.25mg twice daily, and Furosemide 40mg once daily. "
    "Last recorded ejection fraction is 35 percent and BNP is 420. "
    "This summary is derived from synthetic structured records and does not constitute medical advice. Consult a qualified clinician before making any treatment decisions.",

    "Synthetic patient PAT-SYN-003 is a 58-year-old with hypertension managed with Amlodipine 5mg once daily. "
    "Last recorded blood pressure is 142/90. "
    "This summary is derived from synthetic structured records and does not constitute medical advice. Consult a qualified clinician before making any treatment decisions.",

    "Synthetic patient PAT-SYN-004 is an 80-year-old with atrial fibrillation and a CHA2DS2-VASc score of 4. "
    "Current medications include Apixaban 5mg twice daily and Metoprolol succinate 50mg once daily. "
    "This summary is derived from synthetic structured records and does not constitute medical advice. Consult a qualified clinician before making any treatment decisions.",

    "Synthetic patient PAT-SYN-005 is a 63-year-old with moderate-severity COPD. "
    "Current medications include Tiotropium 18mcg inhaled once daily and Albuterol 90mcg as needed. "
    "Last FEV1 is 55 percent of predicted. "
    "This summary is derived from synthetic structured records and does not constitute medical advice. Consult a qualified clinician before making any treatment decisions.",

    "Synthetic patient PAT-SYN-006 is a 45-year-old with major depressive disorder currently taking Sertraline 50mg once daily. "
    "Most recent PHQ-9 score is 14, indicating moderate depression. "
    "This summary is derived from synthetic structured records and does not constitute medical advice. Consult a qualified clinician before making any treatment decisions.",

    "Synthetic patient PAT-SYN-007 is a 70-year-old with chronic kidney disease stage 3, with a last eGFR of 38. "
    "Current medications include Lisinopril 20mg once daily and Amlodipine 10mg once daily. "
    "Last recorded blood pressure is 128/78. "
    "This summary is derived from synthetic structured records and does not constitute medical advice. Consult a qualified clinician before making any treatment decisions.",
]


def generate_healthy_examples() -> list[HealthyExample]:
    """Return all healthy synthetic examples. Safe to call multiple times."""
    examples: list[HealthyExample] = []

    for record, output in zip(_CMS_FACILITY_RECORDS, _CMS_OUTPUTS):
        examples.append(
            HealthyExample(
                doc_type=DocType.CMS_FACILITY,
                source_record=record,
                output_text=output,
            )
        )

    for record, output in zip(_CLINICAL_GUIDELINE_RECORDS, _GUIDELINE_OUTPUTS):
        examples.append(
            HealthyExample(
                doc_type=DocType.CLINICAL_GUIDELINE,
                source_record=record,
                output_text=output,
            )
        )

    for record, output in zip(_PATIENT_RECORDS, _PATIENT_OUTPUTS):
        examples.append(
            HealthyExample(
                doc_type=DocType.PATIENT_RECORD,
                source_record=record,
                output_text=output,
            )
        )

    return examples

from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class DrugTestItem(BaseModel):
    id: Optional[int] = None
    test_date: str
    result: Optional[str] = None
    notes: Optional[str] = None


class MedicationLogItem(BaseModel):
    id: Optional[int] = None
    treatment_type: Optional[str] = None
    medication_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    prescribed_by: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    notes: Optional[str] = None


class MedicalRecordOut(BaseModel):
    id: Optional[int] = None
    admission_id: int
    social_security_validated: bool = False
    iafa_icd_notes: Optional[str] = None
    completion_status: str = "pending"
    drug_tests: List[DrugTestItem] = []
    medication_logs: List[MedicationLogItem] = []
    model_config = ConfigDict(from_attributes=False)


class MedicalRecordUpsert(BaseModel):
    social_security_validated: bool = False
    iafa_icd_notes: Optional[str] = None
    completion_status: str = "pending"
    drug_tests: List[DrugTestItem] = []
    medication_logs: List[MedicationLogItem] = []

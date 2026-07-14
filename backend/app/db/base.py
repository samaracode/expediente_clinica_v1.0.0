from app.db.base_class import Base  # noqa: F401

# Import all models so Alembic can detect them during autogenerate
from app.models.file import File  # noqa: F401
from app.models.user import User, TreatmentArea, Professional, UserModulePermission, Module  # noqa: F401
from app.models.resident import Resident, FamilyMember, EducationRecord, Relative, PatientRelative  # noqa: F401
from app.models.admission import Admission, EconomicSituation, HouseholdMember, ConsumptionSnapshot  # noqa: F401
from app.models.consent import ConsentRecord, PersonalItemsInventory  # noqa: F401
from app.models.medical import MedicalRecord, DrugTest, MedicationLog  # noqa: F401
from app.models.assessment import TherapeuticAssessment, SocialWorkAssessment, PsychologyAssessment, OccupationalTherapyAssessment  # noqa: F401
from app.models.treatment import TreatmentPlan, TreatmentStage  # noqa: F401
from app.models.follow_up import ExitPass, DailyLog, FamilyTherapySession, Consultation  # noqa: F401
from app.models.audit import AuditLog, ProgramAbandonment, Complaint  # noqa: F401
from app.models.medication import (  # noqa: F401
    Medication,
    MedicationOrder,
    MedicationAdministration,
    MedTimeSlot,
    ResidentAllergy,
)
from app.models.attendance import AttendanceRollCall, AttendanceEntry  # noqa: F401
from app.models.occupancy import ClinicSetting, WaitlistEntry  # noqa: F401
from app.models.handover import ShiftHandover, ShiftIncident, ShiftTask  # noqa: F401
from app.models.finance import PaymentAgreement, Charge, Payment  # noqa: F401
from app.models.assistant import AssistantUsage  # noqa: F401

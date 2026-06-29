export type UserRole =
  | "admin"
  | "counselor"
  | "medical"
  | "social_worker"
  | "psychologist"
  | "occupational_therapist"
  | "receptionist";

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export type AdmissionStatus =
  | "intake_pending"
  | "consents_pending"
  | "assessment_in_progress"
  | "treatment_active"
  | "discharged"
  | "abandoned";

export type AdmissionType = "first" | "readmission";

export type Sex = "male" | "female" | "other";
export type MaritalStatus = "single" | "married" | "divorced" | "widowed" | "common_law";

export interface ResidentList {
  id: number;
  code: string;
  first_name: string;
  last_name: string;
  id_number: string | null;
  phone_mobile: string | null;
  is_deleted: boolean;
  created_at: string;
}

export interface ResidentOut extends ResidentList {
  birthdate: string | null;
  sex: Sex | null;
  marital_status: MaritalStatus | null;
  nationality: string | null;
  province: string | null;
  canton: string | null;
  district: string | null;
  emergency_contact_name: string | null;
  emergency_contact_phone: string | null;
  is_insured: boolean;
}

export interface ResidentCreate {
  first_name: string;
  last_name: string;
  id_number?: string;
  birthdate?: string;
  sex?: Sex;
  marital_status?: MaritalStatus;
  nationality?: string;
  province?: string;
  canton?: string;
  district?: string;
  neighborhood?: string;
  address_other?: string;
  phone_home?: string;
  phone_mobile?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  is_insured?: boolean;
  insurance_type?: string;
}

export interface AdmissionOut {
  id: number;
  admission_number: string;
  resident_id: number;
  admission_type: AdmissionType;
  admission_date: string;
  discharge_date: string | null;
  status: AdmissionStatus;
  referral_source: string | null;
  initial_diagnosis: string | null;
  sponsor_name: string | null;
  has_support_network: boolean;
  assigned_counselor_id: number | null;
  is_deleted: boolean;
  created_at: string;
}

export type ConsentType =
  | "INTERNMENT_SERVICE"
  | "INTERNMENT"
  | "SEARCH"
  | "DRUG_TEST"
  | "CCTV"
  | "INFO_RELEASE"
  | "WEAPONS"
  | "IAFA_ACTIONS"
  | "INDIVIDUAL_APPROACH"
  | "REFERRAL"
  | "RECORD_ACCESS"
  | "RIGHTS_FOCUS"
  | "LABOR"
  | "NON_DISCRIMINATION"
  | "SPONSOR"
  | "MANUAL"
  | "LABOR_PROVISION";

export interface ConsentItem {
  consent_type: ConsentType;
  is_signed: boolean;
  signed_at: string | null;
  verified_by_user_id: number | null;
  notes: string | null;
}

export interface PersonalItem {
  description: string;
  quantity: number;
  condition: string | null;
}

export interface PersonalItemsInventoryOut {
  id: number | null;
  admission_id: number;
  recorded_at: string | null;
  recorded_by_user_id: number | null;
  items: PersonalItem[];
  notes: string | null;
}

export interface EconomicSituationOut {
  id: number | null;
  admission_id: number;
  has_worked: boolean | null;
  current_job: string | null;
  work_phone: string | null;
  workplace: string | null;
  job_title: string | null;
  tenure_months: number | null;
  monthly_income_colones: number | null;
  house_type: string | null;
  rent_amount: number | null;
  family_income_notes: string | null;
  financial_assistance_notes: string | null;
  household_members: string[];
}

export interface DrugTestItem {
  id: number | null;
  test_date: string;
  result: string | null;
  notes: string | null;
}

export interface MedicationLogItem {
  id: number | null;
  treatment_type: string | null;
  medication_name: string;
  dosage: string | null;
  frequency: string | null;
  prescribed_by: string | null;
  start_date: string | null;
  end_date: string | null;
  notes: string | null;
}

export interface MedicalRecordOut {
  id: number | null;
  admission_id: number;
  social_security_validated: boolean;
  iafa_icd_notes: string | null;
  completion_status: string;
  drug_tests: DrugTestItem[];
  medication_logs: MedicationLogItem[];
}

export interface TherapeuticAssessmentOut {
  id: number | null;
  admission_id: number;
  assessor_id: number | null;
  assessment_date: string | null;
  initial_summary: string | null;
  clinical_history_summary: string | null;
  europal_si_notes: string | null;
  socrates_notes: string | null;
  urica_notes: string | null;
  afc_analysis_notes: string | null;
  relapse_prevention_interview: string | null;
  relapse_prevention_plan: string | null;
  completion_status: string;
}

export interface SocialWorkAssessmentOut {
  id: number | null;
  admission_id: number;
  social_worker_id: number | null;
  assessment_date: string | null;
  diagnostic_impression: string | null;
  initial_assessment: string | null;
  completion_status: string;
}

export interface PsychologyAssessmentOut {
  id: number | null;
  admission_id: number;
  psychologist_id: number | null;
  assessment_date: string | null;
  initial_diagnostic_impression: string | null;
  observable_assessment: string | null;
  diagnostic_tests_notes: string | null;
  completion_status: string;
}

export interface OccupationalTherapyAssessmentOut {
  id: number | null;
  admission_id: number;
  therapist_id: number | null;
  assessment_date: string | null;
  initial_diagnostic_impression: string | null;
  occupational_profile: string | null;
  completion_status: string;
}

export interface UserAdminOut {
  id: number;
  full_name: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string | null;
}

export interface TreatmentAreaOut {
  id: number;
  name: string;
  description: string | null;
}

export interface ProfessionalOut {
  id: number;
  user_id: number;
  area_id: number;
  first_name: string;
  last_name: string;
  specialty: string | null;
  is_active: boolean;
  area_name: string | null;
  user_email: string | null;
}

export interface AdmissionReportRow {
  id: number;
  admission_number: string;
  resident_name: string;
  admission_date: string;
  discharge_date: string | null;
  status: string;
  admission_type: string;
}

export interface ConsultationReportRow {
  id: number;
  consultation_date: string;
  professional_name: string;
  area_name: string | null;
  consultation_type: string | null;
  resident_name: string;
}

export interface TreatmentProgressRow {
  admission_id: number;
  admission_number: string;
  resident_name: string;
  status: string;
  stages_completed: number;
  stages_total: number;
  current_stage: string | null;
}

export interface ExitPassOut {
  id: number;
  admission_id: number;
  requested_at: string | null;
  approved_by_id: number | null;
  departure_date: string | null;
  return_date_expected: string | null;
  return_date_actual: string | null;
  reason: string | null;
  narrative: string | null;
  companion: string | null;
  pass_type: string;
  status: string;
}

export interface DailyLogOut {
  id: number;
  admission_id: number;
  logged_by_id: number | null;
  log_date: string;
  intervention_type: string | null;
  notes: string | null;
  recommendations: string | null;
}

export interface TreatmentStageOut {
  id: number | null;
  stage_name: string;
  stage_order: number;
  start_date: string | null;
  end_date: string | null;
  progress_notes: string | null;
  extension_consent_signed: boolean;
  advancement_criteria: string | null;
  status: string;
}

export interface TreatmentPlanOut {
  id: number | null;
  admission_id: number;
  recommendations: string | null;
  plan_details: string | null;
  life_project: string | null;
  created_at: string | null;
  updated_at: string | null;
  stages: TreatmentStageOut[];
}

export interface ConsultationOut {
  id: number;
  admission_id: number;
  professional_id: number | null;
  area_id: number | null;
  consultation_type: string | null;
  description: string | null;
  observations: string | null;
  consultation_date: string;
  next_appointment_date: string | null;
  professional_name: string | null;
  area_name: string | null;
}

export interface RelativeOut {
  id: number;
  patient_relative_id: number;
  relation_type: string;
  id_number: string | null;
  first_name: string;
  last_name: string;
  birthdate: string | null;
  marital_status: string | null;
  address: string | null;
  judicial_situation: string | null;
  phone: string | null;
  education_level: string | null;
}

export interface ResidentPage {
  items: ResidentList[];
  total: number;
  page: number;
  pages: number;
}

export interface NotificationItem {
  type: "upcoming_appointment" | "overdue_exit_pass" | "upcoming_stage_end";
  message: string;
  entity_id: number;
  entity_type: string;
  due_date: string | null;
}

export interface AdmissionCreate {
  resident_id: number;
  admission_type?: AdmissionType;
  admission_date: string;
  assigned_counselor_id?: number;
  referral_source?: string;
  admission_condition?: string;
  initial_diagnosis?: string;
  sponsor_name?: string;
  sponsor_relationship?: string;
  sponsor_phone?: string;
  sponsor_address?: string;
  judicial_status?: string;
  has_support_network?: boolean;
}

// ---------------------------------------------------------------------------
// MAR — Módulo de Administración de Medicamentos
// ---------------------------------------------------------------------------

export type MedicationRoute = "oral" | "IM" | "SC" | "otra";
export type ScheduleType = "scheduled" | "prn";
export type OrderStatus = "active" | "suspended" | "finished";
export type AdministrationStatus = "pending" | "taken" | "refused" | "omitted";
export type AllergySeverity = "leve" | "moderada" | "severa";

export interface MedicationOut {
  id: number;
  name: string;
  form: string | null;
  strength: string | null;
  is_controlled: boolean;
  notes: string | null;
}

export interface MedicationCreate {
  name: string;
  form?: string;
  strength?: string;
  is_controlled?: boolean;
  notes?: string;
}

export interface MedicationOrderOut {
  id: number;
  admission_id: number;
  medication_id: number;
  dose: string;
  route: MedicationRoute;
  schedule_type: ScheduleType;
  times: string[] | null;
  frequency_text: string | null;
  prn_reason: string | null;
  start_date: string;
  end_date: string | null;
  prescribed_by_external: string | null;
  prescriber_institution: string | null;
  transcribed_by_user_id: number | null;
  receta_file_id: number | null;
  is_controlled: boolean;
  status: OrderStatus;
  notes: string | null;
  created_at: string | null;
}

export interface MedicationOrderCreate {
  admission_id: number;
  medication_id: number;
  dose: string;
  route: MedicationRoute;
  schedule_type: ScheduleType;
  times?: string[];
  frequency_text?: string;
  prn_reason?: string;
  start_date: string;
  end_date?: string;
  prescribed_by_external?: string;
  prescriber_institution?: string;
  transcribed_by_user_id?: number;
  receta_file_id?: number;
  is_controlled?: boolean;
  notes?: string;
}

export interface MedicationOrderPatch {
  dose?: string;
  route?: MedicationRoute;
  schedule_type?: ScheduleType;
  times?: string[];
  frequency_text?: string;
  prn_reason?: string;
  start_date?: string;
  end_date?: string;
  prescribed_by_external?: string;
  prescriber_institution?: string;
  transcribed_by_user_id?: number;
  receta_file_id?: number;
  is_controlled?: boolean;
  status?: OrderStatus;
  notes?: string;
}

export interface AdministrationRecord {
  status: AdministrationStatus;
  administered_at?: string;
  witness_user_id?: number;
  reason?: string;
  notes?: string;
}

export interface PRNRecord {
  reason: string;
  administered_at?: string;
  witness_user_id?: number;
  notes?: string;
}

export interface MedicationAdministrationOut {
  id: number;
  order_id: number;
  admission_id: number;
  scheduled_at: string | null;
  status: AdministrationStatus;
  administered_at: string | null;
  administered_by_user_id: number | null;
  witness_user_id: number | null;
  reason: string | null;
  notes: string | null;
  created_at: string | null;
  is_overdue: boolean;
}

export interface AllergyBrief {
  id: number;
  substance: string;
  severity: AllergySeverity | null;
}

export interface PassEntryOut {
  administration_id: number;
  order_id: number;
  admission_id: number;
  resident_id: number;
  resident_name: string;
  medication_name: string;
  dose: string;
  route: MedicationRoute;
  is_controlled: boolean;
  scheduled_at: string | null;
  slot_label: string | null;
  status: AdministrationStatus;
  administered_at: string | null;
  administered_by_user_id: number | null;
  witness_user_id: number | null;
  reason: string | null;
  notes: string | null;
  is_overdue: boolean;
  allergies: AllergyBrief[];
}

export interface DailyPassOut {
  date: string;
  entries: PassEntryOut[];
}

export interface MedTimeSlotOut {
  id: number;
  label: string;
  time: string;
  sort_order: number;
}

export interface ResidentAllergyOut {
  id: number;
  resident_id: number;
  substance: string;
  reaction: string | null;
  severity: AllergySeverity | null;
}

export interface ResidentAllergyCreate {
  substance: string;
  reaction?: string;
  severity?: AllergySeverity;
}

export interface FileUploadOut {
  id: number;
  file_name: string;
  mime_type: string | null;
  url: string;
}

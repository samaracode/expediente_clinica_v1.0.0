export type UserRole =
  | "admin"
  | "counselor"
  | "medical"
  | "social_worker"
  | "psychologist"
  | "occupational_therapist"
  | "receptionist";

// Módulos configurables de acceso por usuario (ADR 0003). `admin` no
// necesita módulos: tiene acceso total implícito. `dashboard` no es
// configurable: siempre visible.
export type Module =
  | "residents"
  | "operations"
  | "finance"
  | "reports"
  | "medical"
  | "psychology"
  | "therapeutic"
  | "social_work"
  | "occupational_therapy";

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  modules: Module[];
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
  modules: Module[];
}

export interface UserCreate {
  full_name: string;
  email: string;
  role: string;
  password: string;
  modules: Module[];
}

export interface UserUpdate {
  full_name?: string;
  role?: string;
  is_active?: boolean;
  modules?: Module[];
}

export interface PasswordResetIn {
  new_password: string;
}

export interface PasswordChangeIn {
  current_password: string;
  new_password: string;
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
  type:
    | "upcoming_appointment"
    | "overdue_exit_pass"
    | "upcoming_stage_end"
    | "overdue_medication"
    | "absent_without_leave"
    | "overdue_balance";
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
export type AllergySeverity = "mild" | "moderate" | "severe";

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

export interface MedicationUpdate {
  name?: string;
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

// ---------------------------------------------------------------------------
// Ocupación + Lista de espera
// ---------------------------------------------------------------------------

export interface OccupancyOut {
  capacity: number;
  occupied: number;
  available: number;
  by_status: Record<string, number>;
}

export interface CapacityOut {
  capacity: number;
}

export type WaitlistStatus = "waiting" | "admitted" | "declined" | "cancelled";

export interface WaitlistEntryOut {
  id: number;
  full_name: string;
  contact_phone: string | null;
  contact_email: string | null;
  requested_at: string | null;
  referred_by: string | null;
  status: WaitlistStatus;
  notes: string | null;
  created_by_user_id: number | null;
  created_at: string | null;
}

export interface WaitlistEntryCreate {
  full_name: string;
  contact_phone?: string;
  contact_email?: string;
  requested_at?: string;
  referred_by?: string;
  notes?: string;
}

export interface WaitlistEntryPatch {
  full_name?: string;
  contact_phone?: string;
  contact_email?: string;
  requested_at?: string;
  referred_by?: string;
  status?: WaitlistStatus;
  notes?: string;
}

// ---------------------------------------------------------------------------
// Asistencia — Módulo de presencia física (a nivel centro)
// ---------------------------------------------------------------------------

export type PresenceStatus =
  | "present"
  | "on_pass"
  | "external_appointment"
  | "hospitalized"
  | "absent_without_leave"
  | "discharged";

export type Shift = "morning" | "afternoon" | "night";

export interface RosterEntryOut {
  admission_id: number;
  resident_id: number;
  resident_name: string;
  expected_status: PresenceStatus;
  actual_status: PresenceStatus | null;
  note: string | null;
  entry_id: number | null;
}

export interface RosterOut {
  date: string;
  shift: Shift;
  roll_call_id: number | null;
  conducted_by_user_id: number | null;
  conducted_at: string | null;
  notes: string | null;
  entries: RosterEntryOut[];
}

export interface AttendanceEntryIn {
  admission_id: number;
  expected_status: PresenceStatus;
  actual_status: PresenceStatus;
  note?: string;
}

export interface RollCallCreate {
  date: string;
  shift: Shift;
  notes?: string;
  entries: AttendanceEntryIn[];
}

export interface AttendanceEntryOut {
  id: number;
  roll_call_id: number;
  admission_id: number;
  expected_status: PresenceStatus;
  actual_status: PresenceStatus;
  note: string | null;
}

export interface RollCallOut {
  id: number;
  date: string;
  shift: Shift;
  conducted_by_user_id: number | null;
  conducted_at: string | null;
  notes: string | null;
  entries: AttendanceEntryOut[];
}

export interface AttendanceSummaryOut {
  date: string;
  source: "roll_call" | "expected";
  total: number;
  present: number;
  on_pass: number;
  external_appointment: number;
  hospitalized: number;
  absent_without_leave: number;
  discharged: number;
}

// ─── Entrega de turno (Shift Handover) ───────────────────────────────────────

export type HandoverStatus = "open" | "closed" | "received";
export type IncidentSeverity = "low" | "medium" | "high";

export interface HandoverAutoSummary {
  medications: {
    administration_id: number;
    order_id: number;
    admission_id: number;
    status: string;
    scheduled_at: string | null;
    reason: string | null;
  }[];
  attendance: {
    entry_id: number;
    admission_id: number;
    expected_status: string;
    actual_status: string;
    note: string | null;
  }[];
  exit_passes: {
    exit_pass_id: number;
    admission_id: number;
    status: string;
    departure_date: string | null;
    return_date_actual: string | null;
    events: ("departure" | "return")[];
  }[];
  admissions: {
    admission_id: number;
    resident_id: number;
    admission_number: string;
    status: string;
  }[];
  note: string;
}

export interface ShiftHandoverOut {
  id: number;
  date: string;
  shift: Shift;
  auto_summary: HandoverAutoSummary | null;
  notes: string | null;
  closed_by_user_id: number | null;
  closed_at: string | null;
  received_by_user_id: number | null;
  received_at: string | null;
  status: HandoverStatus;
  created_at: string;
}

export interface ShiftIncidentOut {
  id: number;
  handover_id: number;
  admission_id: number | null;
  type: string;
  severity: IncidentSeverity;
  description: string;
  action_taken: string | null;
  reported_by_user_id: number | null;
  created_at: string;
}

export interface ShiftIncidentCreate {
  admission_id?: number | null;
  type: string;
  severity: IncidentSeverity;
  description: string;
  action_taken?: string | null;
}

export interface ShiftTaskOut {
  id: number;
  handover_id: number;
  related_admission_id: number | null;
  description: string;
  due_at: string | null;
  is_done: boolean;
  done_by_user_id: number | null;
  created_at: string;
}

export interface ShiftTaskCreate {
  related_admission_id?: number | null;
  description: string;
  due_at?: string | null;
}

export interface ShiftTaskPatch {
  description?: string;
  due_at?: string | null;
  is_done?: boolean;
}

// ---------------------------------------------------------------------------
// Control Financiero (cuentas por cobrar)
// ---------------------------------------------------------------------------

export type AgreementType = "monthly" | "fixed_total" | "scholarship_full" | "scholarship_partial";
export type PaymentMethod = "cash" | "sinpe" | "transfer" | "check" | "other";
export type PayerType = "family" | "iafa" | "imas" | "church" | "donor" | "other";

export interface PaymentAgreementOut {
  id: number;
  admission_id: number;
  agreement_type: AgreementType;
  amount: number;
  billing_day: number | null;
  notes: string | null;
  is_active: boolean;
  created_at: string | null;
}

export interface PaymentAgreementUpsert {
  agreement_type: AgreementType;
  amount: number;
  billing_day?: number | null;
  notes?: string | null;
  is_active?: boolean;
}

export interface ChargeOut {
  id: number;
  admission_id: number;
  concept: string;
  amount: number;
  charge_date: string;
  period: string | null;
  is_auto: boolean;
  created_by_user_id: number | null;
  notes: string | null;
  created_at: string | null;
}

export interface ChargeCreate {
  concept: string;
  amount: number;
  charge_date: string;
  period?: string | null;
  notes?: string | null;
}

export interface PaymentOut {
  id: number;
  admission_id: number;
  amount: number;
  payment_date: string;
  method: PaymentMethod;
  payer_type: PayerType;
  payer_name: string | null;
  reference: string | null;
  receipt_number: number;
  received_by_user_id: number | null;
  notes: string | null;
  created_at: string | null;
}

export interface PaymentCreate {
  amount: number;
  payment_date: string;
  method: PaymentMethod;
  payer_type: PayerType;
  payer_name?: string | null;
  reference?: string | null;
  received_by_user_id?: number | null;
  notes?: string | null;
}

export interface AccountOut {
  charges: ChargeOut[];
  payments: PaymentOut[];
  balance: number;
}

export interface OverdueEntryOut {
  admission_id: number;
  resident_name: string;
  balance: number;
  oldest_charge_date: string;
  days_overdue: number;
}

export interface FinanceOverviewOut {
  period: string;
  total_received: number;
  by_payer_type: Record<string, number>;
  overdue_count: number;
  overdue_total: number;
}

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

export interface MonthlyFlowItem {
  month: string;       // "YYYY-MM"
  admissions: number;
  discharges: number;
}

export interface StatusCountItem {
  status: string;
  count: number;
}

export interface DashboardSummary {
  active_residents: number;
  capacity: number;
  occupancy_pct: number;
  waitlist_count: number;
  admissions_this_month: number;
  discharges_this_month: number;
  outstanding_balance?: number | null;
  monthly_flow: MonthlyFlowItem[];
  admissions_by_status: StatusCountItem[];
}

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

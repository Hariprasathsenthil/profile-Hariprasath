export enum UserRole {
  STUDENT = "Student",
  STAFF = "Staff",
  OFFICER = "Officer",
  MANAGER = "Manager",
  ADMIN = "Admin"
}

export enum Department {
  MAINTENANCE = "Maintenance",
  IT = "IT",
  ADMINISTRATION = "Administration"
}

export enum ComplaintStatus {
  PENDING = "Pending",
  IN_PROGRESS = "In-Progress",
  RESOLVED = "Resolved",
  ESCALATED = "Escalated"
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  created_at?: string;
  is_active?: boolean;
}

export interface Complaint {
  id: string;
  complaint_id: string;
  user_id: string;
  user_email: string;
  title: string;
  description: string;
  department: Department;
  status: ComplaintStatus;
  submission_date: string;
  last_updated: string;
  assigned_officer_id?: string;
  assigned_officer_email?: string;
  resolution_notes?: string;
  escalation_count: number;
}

export interface Notification {
  id: string;
  user_id: string;
  complaint_id: string;
  type: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface Statistics {
  total_complaints: number;
  by_status: {
    pending: number;
    in_progress: number;
    resolved: number;
    escalated: number;
  };
  by_department: {
    maintenance: number;
    it: number;
    administration: number;
  };
  recent_complaints: Array<{
    id: string;
    complaint_id: string;
    title: string;
    status: string;
    department: string;
    submission_date: string;
  }>;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

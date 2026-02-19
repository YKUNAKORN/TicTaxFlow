export interface UserProfile {
  id: string;
  email: string;
  username?: string;
  full_name?: string;
  phone?: string;
  annual_income?: number;
  created_at?: string;
}

export interface ProfileResponse {
  success: boolean;
  data: UserProfile;
}

export interface ProfileUpdate {
  full_name?: string;
  phone?: string;
  annual_income?: number;
}

export interface ProfileUpdateResponse {
  success: boolean;
  message: string;
  data: any;
}

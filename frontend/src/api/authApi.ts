import axiosClient from './axiosClient';

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface ForgotPasswordPayload {
  email: string;
}

export interface ResetPasswordPayload {
  token: string;
  new_password: string;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const registerUser = async (data: RegisterPayload): Promise<UserResponse> => {
  const response = await axiosClient.post<UserResponse>('/auth/register', data);
  return response.data;
};

export const loginUser = async (data: LoginPayload): Promise<TokenResponse> => {
  const response = await axiosClient.post<TokenResponse>('/auth/login', data);
  return response.data;
};

export const getCurrentUser = async (): Promise<UserResponse> => {
  const response = await axiosClient.get<UserResponse>('/auth/me');
  return response.data;
};

export const forgotPassword = async (data: ForgotPasswordPayload): Promise<void> => {
  await axiosClient.post('/auth/forgot-password', data);
};

export const resetPassword = async (data: ResetPasswordPayload): Promise<void> => {
  await axiosClient.post('/auth/reset-password', data);
};
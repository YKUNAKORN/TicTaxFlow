import { apiClient } from './client';
import { storage } from '../lib/storage';
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  LogoutResponse,
} from '../types/auth';

export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>(
      '/auth/login',
      credentials
    );

    console.log('Login response:', response);
    console.log('User ID:', response.user.id);

    storage.setToken(response.access_token);
    storage.setRefreshToken(response.refresh_token);
    storage.setUserId(response.user.id);

    console.log('Stored user ID:', storage.getUserId());

    return response;
  },

  register: async (data: RegisterRequest): Promise<RegisterResponse> => {
    const response = await apiClient.post<RegisterResponse>(
      '/auth/register',
      data
    );

    return response;
  },

  logout: async (): Promise<LogoutResponse> => {
    const response = await apiClient.post<LogoutResponse>('/auth/logout', undefined, {
      requiresAuth: true,
    });

    storage.clearTokens();

    return response;
  },
};

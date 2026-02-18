import { apiClient } from './client';
import type { ProfileResponse } from '../types/profile';

export const profileApi = {
  getMe: async (): Promise<ProfileResponse> => {
    return apiClient.get<ProfileResponse>('/profile/me', {
      requiresAuth: true,
    });
  },
};

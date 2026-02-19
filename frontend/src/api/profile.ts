import { apiClient } from './client';
import type { ProfileResponse, ProfileUpdate, ProfileUpdateResponse } from '../types/profile';

export const profileApi = {
  getMe: async (): Promise<ProfileResponse> => {
    return apiClient.get<ProfileResponse>('/profile/me', {
      requiresAuth: true,
    });
  },

  updateMe: async (updates: ProfileUpdate): Promise<ProfileUpdateResponse> => {
    return apiClient.put<ProfileUpdateResponse>('/profile/me', updates, {
      requiresAuth: true,
    });
  },
};

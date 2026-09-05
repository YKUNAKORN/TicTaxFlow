import { apiClient } from './client';
import type { IncomeSyncResponse } from '../types/dashboard';

export const incomeApi = {
  sync: async (period?: string): Promise<IncomeSyncResponse> => {
    return apiClient.post<IncomeSyncResponse>(
      '/income/sync',
      { period },
      { requiresAuth: true }
    );
  },
};

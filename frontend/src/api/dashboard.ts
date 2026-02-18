import { apiClient } from './client';
import type {
  DashboardStatsResponse,
  DashboardSummaryResponse,
} from '../types/dashboard';

export const dashboardApi = {
  getStats: async (userId: string): Promise<DashboardStatsResponse> => {
    return apiClient.get<DashboardStatsResponse>(
      `/dashboard/stats/${userId}`,
      { requiresAuth: true }
    );
  },

  getSummary: async (userId: string): Promise<DashboardSummaryResponse> => {
    return apiClient.get<DashboardSummaryResponse>(
      `/dashboard/summary/${userId}`,
      { requiresAuth: true }
    );
  },
};

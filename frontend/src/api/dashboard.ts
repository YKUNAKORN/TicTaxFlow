import { apiClient } from './client';
import type {
  DashboardStatsResponse,
  DashboardSummaryResponse,
} from '../types/dashboard';

export const dashboardApi = {
  getStats: async (): Promise<DashboardStatsResponse> => {
    return apiClient.get<DashboardStatsResponse>(
      `/dashboard/stats`,
      { requiresAuth: true }
    );
  },

  getSummary: async (): Promise<DashboardSummaryResponse> => {
    return apiClient.get<DashboardSummaryResponse>(
      `/dashboard/summary`,
      { requiresAuth: true }
    );
  },
};

import { apiClient } from './client';

export const transactionsApi = {
    // Get all transactions for the current user, optionally filtered by status
    getUserTransactions: async (status?: string): Promise<any> => {
        const query = status ? `?status=${status}` : '';
        return apiClient.get(`/transactions/user${query}`, {
            requiresAuth: true,
        });
    },

    // Get transaction summary stats for the current user
    getSummary: async (): Promise<any> => {
        return apiClient.get(`/transactions/summary`, {
            requiresAuth: true,
        });
    },

    // Delete a transaction by ID
    deleteTransaction: async (transactionId: string): Promise<any> => {
        return apiClient.delete(`/transactions/${transactionId}`, {
            requiresAuth: true,
        });
    },
};

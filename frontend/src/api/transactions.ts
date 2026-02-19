import { apiClient } from './client';

export const transactionsApi = {
    // Get all transactions for a user, optionally filtered by status
    getUserTransactions: async (userId: string, status?: string): Promise<any> => {
        const query = status ? `?status=${status}` : '';
        return apiClient.get(`/transactions/user/${userId}${query}`, {
            requiresAuth: true,
        });
    },

    // Get transaction summary stats for a user
    getSummary: async (userId: string): Promise<any> => {
        return apiClient.get(`/transactions/summary/${userId}`, {
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

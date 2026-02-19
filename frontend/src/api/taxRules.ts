import { apiClient } from './client';

export const taxRulesApi = {
    // Get all tax rules, optionally filtered by year
    getAllTaxRules: async (year?: number): Promise<any> => {
        const query = year ? `?tax_year=${year}` : '';
        return apiClient.get(`/tax-rules/${query}`, {
            requiresAuth: true,
        });
    },

    // Get a specific tax rule by ID
    getTaxRuleById: async (id: string): Promise<any> => {
        return apiClient.get(`/tax-rules/${id}`, {
            requiresAuth: true,
        });
    },
};

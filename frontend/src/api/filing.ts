import { apiClient } from './client';
import type { FormType, FilingPackResponse, FilingFormsResponse } from '../types/filing';

export const filingApi = {
  getForms: (taxYear?: number) =>
    apiClient.get<FilingFormsResponse>(
      taxYear ? `/filing/forms?tax_year=${taxYear}` : '/filing/forms',
      { requiresAuth: true }
    ),

  preview: (formType: FormType, taxYear: number) =>
    apiClient.get<FilingPackResponse>(
      `/filing/preview?form_type=${formType}&tax_year=${taxYear}`,
      { requiresAuth: true }
    ),
};

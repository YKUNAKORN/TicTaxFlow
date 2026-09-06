import { storage } from '../lib/storage';

// Base URL for the API. Set VITE_API_BASE_URL at build time for any
// non-localhost deployment (see .env.example / Dockerfile build arg).
// The localhost value is only a dev fallback for `npm run dev`.
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Same host without the `/api/v1` suffix — used for static files the
// backend serves outside the API prefix (e.g. /receipts/<file>).
export const API_ORIGIN = API_BASE_URL.replace(/\/api\/v1\/?$/, '');

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

interface RequestConfig extends RequestInit {
  requiresAuth?: boolean;
}

async function request<T>(
  endpoint: string,
  config: RequestConfig = {}
): Promise<T> {
  const { requiresAuth = false, headers = {}, ...restConfig } = config;

  const requestHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    ...headers,
  };

  if (requiresAuth) {
    const token = storage.getToken();
    if (token) {
      requestHeaders['Authorization'] = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...restConfig,
    headers: requestHeaders,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));

    // An authenticated call that comes back 401 means the token is missing,
    // expired, or rejected. Drop it and bounce to sign-in so the user isn't
    // left staring at a broken page. (Login/register don't set requiresAuth,
    // so their own 401s — bad credentials — are left for the page to show.)
    if (response.status === 401 && requiresAuth) {
      storage.clearTokens();
      if (typeof window !== 'undefined' && window.location.pathname !== '/signin') {
        window.location.assign('/signin');
      }
    }

    throw new ApiError(
      response.status,
      errorData.detail || 'An error occurred',
      errorData
    );
  }

  return response.json();
}

export const apiClient = {
  get: <T>(endpoint: string, config?: RequestConfig) =>
    request<T>(endpoint, { ...config, method: 'GET' }),

  post: <T>(endpoint: string, data?: any, config?: RequestConfig) =>
    request<T>(endpoint, {
      ...config,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }),

  put: <T>(endpoint: string, data?: any, config?: RequestConfig) =>
    request<T>(endpoint, {
      ...config,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }),

  delete: <T>(endpoint: string, config?: RequestConfig) =>
    request<T>(endpoint, { ...config, method: 'DELETE' }),
};

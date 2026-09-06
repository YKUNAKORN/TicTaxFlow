const TOKEN_KEY = 'tictaxflow_token';
const REFRESH_TOKEN_KEY = 'tictaxflow_refresh_token';
const USER_ID_KEY = 'tictaxflow_user_id';
const REMEMBERED_EMAIL_KEY = 'tictaxflow_remembered_email';

// "Remember me" persists the email only. An earlier build also stored the
// plaintext password under this key — purge it on load so returning users
// are not left with a credential sitting in localStorage.
const LEGACY_REMEMBERED_PASSWORD_KEY = 'tictaxflow_remembered_password';
try {
  localStorage.removeItem(LEGACY_REMEMBERED_PASSWORD_KEY);
} catch {
  /* localStorage unavailable (private mode / disabled) — nothing to purge */
}

export const storage = {
  getToken: (): string | null => localStorage.getItem(TOKEN_KEY),
  setToken: (token: string): void => localStorage.setItem(TOKEN_KEY, token),

  getRefreshToken: (): string | null => localStorage.getItem(REFRESH_TOKEN_KEY),
  setRefreshToken: (token: string): void => localStorage.setItem(REFRESH_TOKEN_KEY, token),

  getUserId: (): string | null => localStorage.getItem(USER_ID_KEY),
  setUserId: (id: string): void => localStorage.setItem(USER_ID_KEY, id),

  clearTokens: (): void => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_ID_KEY);
  },

  getRememberedEmail: (): string | null => localStorage.getItem(REMEMBERED_EMAIL_KEY),
  setRememberedEmail: (email: string): void => localStorage.setItem(REMEMBERED_EMAIL_KEY, email),

  clearRememberedCredentials: (): void => {
    localStorage.removeItem(REMEMBERED_EMAIL_KEY);
  },
};

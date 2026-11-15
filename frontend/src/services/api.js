
const BASE_URL =
  (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  });

  if (!response.ok) {
    const detail = await response.text();
    const error = new Error(`API ${response.status}: ${detail}`);
    error.status = response.status;
    throw error;
  }

  if (response.status === 204) return null;

  return response.json();
}

export const USER_ID = Number(import.meta.env.VITE_USER_ID || 1);

export function checkBackend() {
  return apiRequest('/');
}

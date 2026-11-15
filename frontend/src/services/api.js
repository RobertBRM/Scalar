
const BASE_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
    throw new Error(`API ${response.status}: ${detail}`);
  }

  if (response.status === 204) return null;

  return response.json();
}

export function checkBackend() {
  return apiRequest('/');
}

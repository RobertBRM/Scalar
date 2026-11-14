// Central place for future backend requests.
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export async function apiRequest(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {headers:{'Content-Type':'application/json',...options.headers},...options});
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  return response.json();
}

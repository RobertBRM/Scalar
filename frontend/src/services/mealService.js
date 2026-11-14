import { apiRequest } from './api';
export const getMeals = () => apiRequest('/meals');
export const createMeal = meal => apiRequest('/meals',{method:'POST',body:JSON.stringify(meal)});
// Example API adapters; the dashboard currently uses local sample data.


import { apiRequest } from './api';

export const getUserMeals = (userId) =>
  apiRequest(`/meals/user/${userId}`);

export const getMeal = (mealId) =>
  apiRequest(`/meals/${mealId}`);

export const createMeal = (meal) =>
  apiRequest('/meals/', {
    method: 'POST',
    body: JSON.stringify(meal)
  });

export const updateMeal = (mealId, changes) =>
  apiRequest(`/meals/${mealId}`, {
    method: 'PATCH',
    body: JSON.stringify(changes)
  });

export const deleteMeal = (mealId) =>
  apiRequest(`/meals/${mealId}`, {
    method: 'DELETE'
  });

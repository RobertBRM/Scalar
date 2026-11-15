
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

export const getMealNutrition = mealId =>
  apiRequest(`/meal-items/meal/${mealId}/nutrition`);

export const deleteMealItem = itemId => apiRequest(`/meal-items/${itemId}`, { method: 'DELETE' });
export const getMealFoods = mealId => apiRequest(`/meal-items/meal/${mealId}/foods`);

export async function loadDiary(userId) {
  const meals = await getUserMeals(userId);
  const results = await Promise.allSettled(meals.map(async meal => {
    const nutrition = await getMealNutrition(meal.id);
    for (const key of ['calories', 'protein_g', 'carbs_g', 'fat_g']) {
      if (nutrition?.[key] == null || !Number.isFinite(Number(nutrition[key]))) {
        throw new Error(`Invalid nutrition for meal ${meal.id}`);
      }
    }
    return { meal, nutrition };
  }));
  return results.map((result, index) => result.status === 'fulfilled'
    ? result.value
    : { meal: meals[index], error: result.reason });
}

// Nutrition belongs to a food linked to the meal, rather than the meal row.
export async function logMeal(entry, userId) {
  const food = await apiRequest('/foods/', {
    method: 'POST',
    body: JSON.stringify({
      name: entry.food, serving_size: 1, serving_unit: 'serving',
      calories: entry.cal, protein_g: entry.protein,
      carbs_g: entry.carbs, fat_g: entry.fat
    })
  });
  const meal = await createMeal({
    user_id: userId, meal_type: entry.name.toLowerCase(),
    logged_at: new Date().toISOString(), notes: entry.food
  });
  try {
    await apiRequest('/meal-items/', {
      method: 'POST',
      body: JSON.stringify({ meal_id: meal.id, food_id: food.id, quantity: 1 })
    });
  } catch (error) {
    try { await deleteMeal(meal.id); } catch (cleanupError) {
      throw new Error(`${error.message}. Incomplete meal ${meal.id} could not be removed: ${cleanupError.message}`);
    }
    throw error;
  }
  return meal;
}

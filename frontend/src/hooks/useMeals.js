
import { useState, useEffect } from 'react';
import { createMeal, getUserMeals } from '../services/mealService';

const USER_ID = 1; // Replace with authenticated user ID later

function toFrontendMeal(meal) {
  return {
    id: meal.id,
    name: meal.meal_type.charAt(0).toUpperCase() +
          meal.meal_type.slice(1),
    time: new Date(meal.logged_at).toLocaleTimeString(
      'en-US',
      { hour: '2-digit', minute: '2-digit' }
    ),
    food: meal.notes || '',
    cal: 0,
    protein: 0,
    carbs: 0,
    fat: 0,
    icon: '🍽️'
  };
}

export function useMeals() {
  const [meals, setMeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;

    getUserMeals(USER_ID)
      .then(data => {
        if (active) {
          setMeals(data.map(toFrontendMeal));
        }
      })
      .catch(err => {
        if (active) setError(err.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  async function addMeal(entry) {
    setError(null);

    const payload = {
      user_id: USER_ID,
      meal_type: entry.name.toLowerCase(),
      logged_at: new Date().toISOString(),
      notes: entry.food
    };

    try {
      const created = await createMeal(payload);

      const newMeal = {
        ...toFrontendMeal(created),
        cal: entry.cal,
        protein: entry.protein,
        carbs: entry.carbs,
        fat: entry.fat
      };

      setMeals(old => [...old, newMeal]);
      return newMeal;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }

  return { meals, addMeal, loading, error };
}

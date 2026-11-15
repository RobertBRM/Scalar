
import { useState, useEffect, useRef } from 'react';
import { logMeal, loadDiary, deleteMeal, deleteMealItem, getMealNutrition } from '../services/mealService';
import { USER_ID } from '../services/api';
import { useStoredState } from './usePreferences';


function toFrontendMeal(meal, nutrition = {}) {
  return {
    id: meal.id,
    name: meal.meal_type.charAt(0).toUpperCase() +
          meal.meal_type.slice(1),
    time: new Date(meal.logged_at).toLocaleTimeString(
      'en-US',
      { hour: '2-digit', minute: '2-digit' }
    ),
    food: meal.notes || '',
    cal: Number(nutrition.calories || 0),
    protein: Number(nutrition.protein_g || 0),
    carbs: Number(nutrition.carbs_g || 0),
    fat: Number(nutrition.fat_g || 0),
    icon: '🍽️'
  };
}

export function useMeals() {
  const [meals, setMeals] = useStoredState('meals', []);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const revision = useRef(0);
  const saving = useRef(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    let active = true;
    let refreshing = false;

    function refresh() {
      if (saving.current || refreshing) return;
      refreshing = true;
      const request = ++revision.current;
      loadDiary(USER_ID)
      .then(data => {
        if (active && request === revision.current) {
          setMeals(previous => data.flatMap(({meal, nutrition, error}) => {
            if (!error) return [toFrontendMeal(meal, nutrition)];
            const cached = previous.find(row => row.id === meal.id);
            return cached ? [cached] : [];
          }));
          setError(data.some(row => row.error)
            ? 'Some nutrition values could not refresh. Previously loaded values are still shown; retrying automatically.'
            : null);
        }
      })
      .catch(err => {
        if (active && request === revision.current) setError(err.message);
      })
      .finally(() => {
        refreshing = false;
        if (active) setLoading(false);
      });
    }
    refresh();
    const interval = setInterval(refresh, 10000);
    window.addEventListener('focus', refresh);

    return () => {
      active = false;
      clearInterval(interval);
      window.removeEventListener('focus', refresh);
    };
  }, []);

  async function addMeal(entry) {
    saving.current = true;
    revision.current++;
    setError(null);

    try {
      const created = await logMeal(entry, USER_ID);

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
    } finally {
      saving.current = false;
    }
  }

  async function removeEntry(mealId, itemId) {
    if (saving.current) return false;
    saving.current = true;
    revision.current++;
    setDeleting(true);
    setError(null);
    try {
      if (itemId == null) {
        await deleteMeal(mealId);
        setMeals(old => old.filter(meal => meal.id !== mealId));
      } else {
        await deleteMealItem(itemId);
        const nutrition = await getMealNutrition(mealId);
        setMeals(old => old.map(meal => meal.id === mealId ? {
          ...meal, cal: Number(nutrition.calories), protein: Number(nutrition.protein_g),
          carbs: Number(nutrition.carbs_g), fat: Number(nutrition.fat_g)
        } : meal));
      }
      return true;
    } catch (err) {
      setError(`Could not finish deleting: ${err.message}`);
      return false;
    } finally {
      saving.current = false;
      setDeleting(false);
    }
  }

  return { meals, addMeal, loading, error, removeEntry, deleting };
}

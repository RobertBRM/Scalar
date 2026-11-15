
import React, { useState, useEffect } from 'react';
import { CalendarDays } from 'lucide-react';

import Sidebar from './components/Sidebar';
import Header from './components/Header';
import MealModal from './components/MealModal';
import InfoModal from './components/InfoModal';

import Overview from './pages/Overview';
import FoodDiaryPage from './pages/FoodDiaryPage';
import Recipes from './pages/Recipes';
import Insights from './pages/Insights';
import Goals from './pages/Goals';
import Settings from './pages/Settings';

import { useMeals } from './hooks/useMeals';
import { useNutrition } from './hooks/useNutrition';
import { checkBackend } from './services/api';
import { useGoals, useStoredState } from './hooks/usePreferences';

export default function App() {
  const [page, setPage] = useState('Overview');
  const [menu, setMenu] = useState(false);
  const [search, setSearch] = useState('');
  const [water, setWater] = useStoredState(`water:${new Date().toLocaleDateString('en-CA')}`, 0);
  const [saved, setSaved] = useStoredState('saved-recipes', []);
  const [modal, setModal] = useState(null);

  const { goals, saveGoals, loading: goalsLoading, error: goalsError } = useGoals();

  // Check backend connection when application loads
  useEffect(() => {
    checkBackend()
      .then(data => {
        console.log('Backend connected:', data);
      })
      .catch(error => {
        console.error('Backend connection failed:', error);
      });
  }, []);

  // Meal data and functionality
  const { meals, addMeal, loading, error, removeEntry, deleting } = useMeals();

  // Calculate nutrition totals
  const { totals, remaining } = useNutrition(meals, goals);

  // Navigate between pages
  const navigate = p => {
    setPage(p);
    setMenu(false);
  };

  // Open meal logging modal
  const logMeal = (name = 'Dinner') => {
    setModal({
      type: 'meal',
      initial: { name }
    });
  };

  // Save or unsave recipes
  const toggleSave = name => {
    setSaved(s =>
      s.includes(name)
        ? s.filter(x => x !== name)
        : [...s, name]
    );
  };

  // Handle recipe search
  const handleSearch = value => {
    setSearch(value);

    if (value) {
      navigate('Recipes');
    }
  };

  // Save meal to backend
  const handleSaveMeal = async entry => {
    try {
      await addMeal(entry);

      // Close modal only after successful save
      setModal(null);

      console.log('Meal saved successfully');
    } catch (error) {
      console.error('Failed to save meal:', error);

      alert('Could not save meal: ' + error.message);
    }
  };

  // Shared properties passed to pages
  const shared = {
    onDelete: removeEntry,
    deleting,
    meals,
    totals,
    remaining,
    goals,
    water,
    setWater,
    search,
    saved,
    loading,
    error,
    onLogMeal: logMeal,
    onToggleSave: toggleSave,
    onView: recipe => setModal({
      type: 'recipe',
      recipe
    }),
    onExplore: () => navigate('Recipes')
  };

  return (
    <div className="app">
      <Sidebar
        page={page}
        onNavigate={navigate}
        open={menu}
      />

      <div className="workspace">
        <Header
          search={search}
          onSearch={handleSearch}
          onNotify={() =>
            setModal({ type: 'notifications' })
          }
          menu={menu}
          onToggleMenu={() =>
            setMenu(v => !v)
          }
        />

        <main>
          {(error || goalsError) && <p role="alert">Could not sync with the backend: {error || goalsError}</p>}
          {loading && <p role="status">Loading your meals…</p>}
          <div className="hero">
            <div>
              <div className="eyebrow">
                LET'S MAKE TODAY A GOOD ONE
              </div>

              <h1>
                {page === 'Overview'
                  ? 'A fresh day, a healthier you.'
                  : page}
              </h1>

              <p>
                {page === 'Overview'
                  ? 'A little mindfulness. A lot of nourishment.'
                  : 'Small choices make a meaningful difference.'}
              </p>
            </div>

            <div className="date">
              <CalendarDays size={18} />

              {new Date().toLocaleDateString('en-US', {
                weekday: 'long',
                month: 'long',
                day: 'numeric'
              })}
            </div>
          </div>

          {page === 'Overview' && (
            <Overview {...shared} />
          )}

          {page === 'Food diary' && (
            <FoodDiaryPage {...shared} />
          )}

          {page === 'Recipes' && (
            <Recipes {...shared} />
          )}

          {page === 'Insights' && (
            <Insights {...shared} />
          )}

          {page === 'My goals' && (
            <Goals
              goals={goals}
              onSave={saveGoals}
              loading={goalsLoading}
            />
          )}

          {page === 'Settings' && (
            <Settings onNavigate={navigate} />
          )}
        </main>
      </div>

      {/* Meal logging modal */}
      {modal?.type === 'meal' && (
        <MealModal
          initial={modal.initial}
          onClose={() => setModal(null)}
          onSave={handleSaveMeal}
        />
      )}

      {/* Other modals */}
      {modal && modal.type !== 'meal' && (
        <InfoModal
          modal={modal}
          onClose={() => setModal(null)}
          onLogRecipe={recipe =>
            setModal({
              type: 'meal',
              initial: {
                name: 'Dinner',
                food: recipe.name,
                cal: String(recipe.cal),
                protein: String(recipe.protein)
              }
            })
          }
        />
      )}
    </div>
  );
}

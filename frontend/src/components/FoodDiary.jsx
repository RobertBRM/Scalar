import React, { useState } from 'react';
import { Plus, Trash2, ChevronDown } from 'lucide-react';
import { getMealFoods } from '../services/mealService';

function DiaryRow({ meal, onLogMeal, onDelete, deleting }) {
  const [foods, setFoods] = useState(null);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  async function showFoods() {
    if (open) { setOpen(false); return; }
    setOpen(true); setLoading(true); setError('');
    try { setFoods(await getMealFoods(meal.id)); }
    catch (err) { setError(err.message); }
    finally { setLoading(false); }
  }
  async function removeFood(item) {
    if (await onDelete(meal.id, item.id)) setFoods(old => old.filter(food => food.id !== item.id));
  }
  return <>
    <div className="meal-row">
      <div className="meal-label"><span className="meal-icon">{meal.icon}</span><div><strong>{meal.name}</strong><small>{meal.time}</small></div></div>
      <div><span>{meal.food}</span><button className="food-details-button" onClick={showFoods} aria-expanded={open}><ChevronDown size={14}/> {open ? 'Hide foods' : 'Manage foods'}</button></div>
      <strong>{meal.cal} kcal</strong><span>{meal.protein} g</span><span>{meal.carbs} g</span><span>{meal.fat} g</span>
      <div className="diary-actions"><button className="row-plus" title={`Log ${meal.name}`} onClick={() => onLogMeal(meal.name)}><Plus size={17}/></button><button className="delete-entry" disabled={deleting} onClick={() => onDelete(meal.id)} title={`Delete ${meal.name} meal`} aria-label={`Delete ${meal.name} meal`}><Trash2 size={17}/></button></div>
    </div>
    {open && <div className="meal-food-details">
      {loading && <p role="status">Loading foods...</p>}
      {error && <p role="alert">Could not load foods: {error}</p>}
      {!loading && !error && foods?.length === 0 && <p>No food items in this meal.</p>}
      {!loading && !error && foods?.map(item => <div className="food-item-row" key={item.id}><span><strong>{item.name}</strong> · {item.quantity} serving(s) · {Number(item.calories) * Number(item.quantity)} kcal</span><button className="delete-entry" disabled={deleting} onClick={() => removeFood(item)}><Trash2 size={15}/> Delete food</button></div>)}
    </div>}
  </>;
}

export default function FoodDiary({meals,onLogMeal,onDelete,deleting}) {
  return <section className="diary-section"><div className="section-heading"><div className="inline-title"><h2>Your food diary</h2><p>A little of everything, logged with care.</p></div><button className="primary" onClick={() => onLogMeal('Dinner')}><Plus size={18}/> Log a meal</button></div><div className="diary-table"><div className="table-head"><span>MEAL</span><span>FOOD</span><span>CALORIES</span><span>PROTEIN</span><span>CARBS</span><span>FAT</span><span></span></div>{meals.map(meal => <DiaryRow key={meal.id} meal={meal} onLogMeal={onLogMeal} onDelete={onDelete} deleting={deleting}/>)}</div></section>;
}

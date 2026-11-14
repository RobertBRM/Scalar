import React from 'react';

import CalorieCard from '../components/CalorieCard';import MacroCard from '../components/MacroCard';import HydrationCard from '../components/HydrationCard';import FoodDiary from '../components/FoodDiary';import RecipeSection from '../components/RecipeSection';
export default function Overview(props){return <><section className="summary"><CalorieCard {...props}/><MacroCard {...props}/><HydrationCard {...props} onSetWater={props.setWater}/></section><FoodDiary meals={props.meals} onLogMeal={props.onLogMeal}/><RecipeSection {...props}/></>}

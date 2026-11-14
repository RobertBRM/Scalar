import {ArrowRight} from 'lucide-react';
import RecipeCard from './RecipeCard';
import {recipes} from '../data/mockRecipes';
import React from 'react';

export default function RecipeSection({remaining,search,saved,onToggleSave,onView,onExplore}){const filtered=recipes.filter(r=>r.name.toLowerCase().includes(search.toLowerCase()));return <section className="recipes-section"><div className="section-heading"><div><h2>Made for your next meal</h2><p>Fresh ideas that fit your goals — all under your {remaining} kcal remaining.</p></div><button className="text-link" onClick={onExplore}>Explore recipes <ArrowRight size={17}/></button></div><div className="recipe-grid">{filtered.map(r=><RecipeCard key={r.name} recipe={r} saved={saved.includes(r.name)} onToggleSave={()=>onToggleSave(r.name)} onView={()=>onView(r)}/>)}</div>{filtered.length===0&&<p>No matching recipes. Try another search.</p>}</section>}

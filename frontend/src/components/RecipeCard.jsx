import {Bookmark,Clock,ChevronRight} from 'lucide-react';
import React from 'react';

export default function RecipeCard({recipe,saved,onToggleSave,onView}){return <article className="recipe-card"><div className="recipe-image"><img src={recipe.img} alt={recipe.name}/><span className="recipe-tag">{recipe.tag}</span><button className={'bookmark '+(saved?'is-saved':'')} onClick={onToggleSave} aria-label="Save recipe"><Bookmark size={19} fill={saved?'#315a42':'none'}/></button></div><div className="recipe-body"><h3>{recipe.name}</h3><p>{recipe.cal} kcal <span>·</span> {recipe.protein}g protein</p><div className="recipe-footer"><span><Clock size={15}/> {recipe.time} min</span><button onClick={onView}>View recipe <ChevronRight size={18}/></button></div></div></article>}

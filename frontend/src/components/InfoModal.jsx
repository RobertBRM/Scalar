import React from 'react';

import {X} from 'lucide-react';
export default function InfoModal({modal,onClose,onLogRecipe}){return <div className="modal-backdrop" onMouseDown={e=>{if(e.target===e.currentTarget)onClose()}}><div className="modal"><button className="modal-close" onClick={onClose}><X size={20}/></button>{modal.type==='recipe'?<><h2>{modal.recipe.name}</h2><img className="modal-recipe-image" src={modal.recipe.img} alt={modal.recipe.name}/><p>{modal.recipe.description}</p><p><b>{modal.recipe.cal} kcal</b> · {modal.recipe.protein}g protein · {modal.recipe.time} min</p><button className="primary" onClick={()=>onLogRecipe(modal.recipe)}>Log this recipe</button></>:<><h2>Notifications</h2><p>You're all caught up. Keep up the good habits!</p></>}</div></div>}

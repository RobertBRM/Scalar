import { useState } from 'react';
import { initialMeals } from '../data/mockMeals';
export function useMeals(){
 const [meals,setMeals]=useState(initialMeals);
 function addMeal(entry){setMeals(old=>{const i=old.findIndex(m=>m.name===entry.name&&m.cal===0);return i<0?[...old,entry]:old.map((m,j)=>j===i?entry:m)});}
 return {meals,addMeal};
}

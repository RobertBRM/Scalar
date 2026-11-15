import {useState,useEffect} from 'react';
import {apiRequest,USER_ID} from '../services/api';
export function useStoredState(key,initial){
 const storageKey=`daily-plate:${USER_ID}:${key}`;
 const [value,setValue]=useState(()=>{try{return JSON.parse(localStorage.getItem(storageKey))??initial;}catch{return initial;}});
 useEffect(()=>{try{localStorage.setItem(storageKey,JSON.stringify(value));}catch{}},[storageKey,value]);
 return [value,setValue];
}
const defaults={cal:2200,protein:140,carbs:250,fat:71};
const fromApi=g=>({cal:Number(g.calorie_goal??defaults.cal),protein:Number(g.protein_goal_g??defaults.protein),carbs:Number(g.carb_goal_g??defaults.carbs),fat:Number(g.fat_goal_g??defaults.fat)});
export function useGoals(){
 const [goals,setGoals]=useState(defaults),[loading,setLoading]=useState(true),[error,setError]=useState(null);
 useEffect(()=>{let active=true;apiRequest(`/nutrition-goals/${USER_ID}`).then(g=>{if(active)setGoals(fromApi(g));}).catch(e=>{if(active&&e.status!==404)setError(e.message);}).finally(()=>{if(active)setLoading(false);});return()=>{active=false;};},[]);
 async function saveGoals(next){
  setError(null);
  const data={calorie_goal:next.cal,protein_goal_g:next.protein,carb_goal_g:next.carbs,fat_goal_g:next.fat};
  try{let result;try{result=await apiRequest(`/nutrition-goals/${USER_ID}`,{method:'PATCH',body:JSON.stringify(data)});}catch(e){if(e.status!==404)throw e;result=await apiRequest('/nutrition-goals/',{method:'POST',body:JSON.stringify({...data,user_id:USER_ID})});}setGoals(fromApi(result));}catch(e){setError(e.message);throw e;}
 }
 return {goals,saveGoals,loading,error};
}

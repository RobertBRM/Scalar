import { useMemo } from 'react';
export function useNutrition(meals,goals){
 const totals=useMemo(()=>meals.reduce((a,m)=>({cal:a.cal+m.cal,protein:a.protein+m.protein,carbs:a.carbs+m.carbs,fat:a.fat+m.fat}),{cal:0,protein:0,carbs:0,fat:0}),[meals]);
 return {totals,remaining:Math.max(0,goals.cal-totals.cal)};
}

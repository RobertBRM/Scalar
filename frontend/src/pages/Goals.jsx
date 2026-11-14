import React from 'react';

export default function Goals({goals,setGoals}){return <section className="panel settings-panel"><h2>Your nutrition goals</h2><p>Adjust your daily targets.</p>{Object.entries(goals).map(([k,v])=><label key={k} className="goal-field">{k==='cal'?'Calories (kcal)':k[0].toUpperCase()+k.slice(1)+' (g)'}<input type="number" min="1" value={v} onChange={e=>setGoals(g=>({...g,[k]:Math.max(1,Number(e.target.value)||1)}))}/></label>)}</section>}

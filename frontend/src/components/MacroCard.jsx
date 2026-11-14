import React from 'react';

export default function MacroCard({totals,goals}){return <article className="panel macros"><div className="panel-heading"><b>Your macros</b><span>Consumed / goal</span></div>{[['Protein','protein','#315a42'],['Carbs','carbs','#d08a58'],['Fat','fat','#8aa1bf']].map(([label,key,color])=><div className="macro" key={key}><div><span>{label}</span><span>{totals[key]} / {goals[key]} g</span></div><div className="track"><div style={{width:`${Math.min(100,totals[key]/goals[key]*100)}%`,background:color}}/></div></div>)}</article>}

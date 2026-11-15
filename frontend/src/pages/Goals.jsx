import React, { useEffect, useState } from 'react';
export default function Goals({goals,onSave,loading}) {
 const [draft,setDraft]=useState(goals), [saving,setSaving]=useState(false), [message,setMessage]=useState('');
 useEffect(()=>setDraft(goals),[goals]);
 async function submit(e){e.preventDefault();setSaving(true);setMessage('');try{await onSave(draft);setMessage('Goals saved.');}catch(err){setMessage('Could not save goals: '+err.message);}finally{setSaving(false);}}
 return <section className="panel settings-panel"><h2>Your nutrition goals</h2><p>Adjust your daily targets.</p><form onSubmit={submit}>{Object.entries(draft).map(([k,v])=><label key={k} className="goal-field">{k==='cal'?'Calories (kcal)':k[0].toUpperCase()+k.slice(1)+' (g)'}<input type="number" min="1" required disabled={loading||saving} value={v} onChange={e=>{setMessage('');setDraft(g=>({...g,[k]:Number(e.target.value)}));}}/></label>)}<button className="primary" disabled={loading||saving}>{saving?'Saving…':'Save goals'}</button><p role="status">{message}</p></form></section>;
}

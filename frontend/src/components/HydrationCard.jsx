
import React from 'react';
import {Droplets,Plus} from 'lucide-react';
export default function HydrationCard({water,onSetWater}){return <article className="panel hydration"><div className="panel-heading"><b><Droplets size={19} color="#87a0c3"/> Stay hydrated</b></div><div className="water-count"><strong>{(water*.25).toFixed(2).replace(/0$/,'').replace(/\.$/,'')}</strong><span>/ 2.5 L</span></div><div className="glasses">{Array.from({length:10},(_,i)=><button title={`Set to ${i+1} glasses`} key={i} onClick={()=>onSetWater(i+1)} className={i<water?'filled':''}/>)}</div><div className="water-footer"><span>{water} of 10 glasses</span><button onClick={()=>onSetWater(Math.min(10,water+1))} aria-label="Add a glass of water"><Plus size={20}/></button></div></article>}

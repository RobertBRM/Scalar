import React from 'react';

import CalorieCard from '../components/CalorieCard';import MacroCard from '../components/MacroCard';import HydrationCard from '../components/HydrationCard';
export default function Insights(props){return <section className="summary"><CalorieCard {...props}/><MacroCard {...props}/><HydrationCard {...props} onSetWater={props.setWater}/></section>}

import {LayoutGrid,BookOpen,Utensils,ChartNoAxesCombined,Target,Sun,ChevronDown} from 'lucide-react';
import React from 'react';

const nav=[['Overview',LayoutGrid],['Food diary',BookOpen],['Recipes',Utensils],['Insights',ChartNoAxesCombined],['My goals',Target]];
export default function Sidebar(
    {page,onNavigate,open}
){
    return (
        <aside 
        className={'sidebar '+(open?'show':'')}>
            <div className="brand">
            <strong>daily plate</strong>
            <small>GOOD FOOD. GOOD HABITS.</small>
            </div>
            <nav>
                {nav.map(([name,Icon])=><button key={name} className={'navitem '+(page===name?'selected':'')} onClick={()=>onNavigate(name)}><Icon size={19}/>{name}</button>)}
                </nav><div className="sidebar-bottom"><div className="motivation"><strong>A little better,<br/>every day.</strong><p>Small choices add up.<br/>You're building something<br/>good for you.</p></div><button className="navitem" onClick={()=>onNavigate('Settings')}><Sun size={19}/>Settings</button><div className="account">Personal account <ChevronDown size={14}/><small>Free plan</small></div></div></aside>
    );
}

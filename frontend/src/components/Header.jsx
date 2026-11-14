
import React from 'react';
import {Search,Bell,Menu,X} from 'lucide-react';
export default function Header({search,onSearch,onNotify,menu,onToggleMenu}){return <header className="topbar"><button className="mobile-menu" onClick={onToggleMenu} aria-label="Toggle navigation">{menu?<X/>:<Menu/>}</button><span>Your daily space for feeling good.</span><div className="top-actions"><label className="search"><Search size={18}/><input placeholder="Search foods or recipes" value={search} onChange={e=>onSearch(e.target.value)}/></label><button className="iconbutton" title="Notifications" onClick={onNotify}><Bell size={19}/></button></div></header>}

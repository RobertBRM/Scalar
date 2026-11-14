import React from 'react';

export default function Settings({onNavigate}){return <section className="panel settings-panel"><h2>Settings</h2><p>Your Daily Plate is ready to personalize. Change your targets in My goals.</p><button className="primary" onClick={()=>onNavigate('My goals')}>Edit goals</button></section>}

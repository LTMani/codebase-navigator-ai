import React from 'react';

export default function Sidebar() {
    const navItems = ['Dashboard', 'Projects', 'Analytics', 'Billing', 'Settings'];

    return (
        <aside className="sidebar-container w-64 bg-slate-900 text-white p-4">
            <div className="brand-logo text-lg font-bold mb-6">SaaS Analytics</div>
            <nav className="flex flex-col gap-2">
                {navItems.map(item => (
                    <a key={item} href={`#/${item.toLowerCase()}`} className="nav-link p-2 rounded hover:bg-slate-800">
                        {item}
                    </a>
                ))}
            </nav>
        </aside>
    );
}

import React from 'react';

export default function Header({ title }) {
    return (
        <header className="header-bar flex items-center justify-between p-4 border-b">
            <h1 className="text-xl font-bold">{title}</h1>
            <div className="user-profile flex items-center gap-2">
                <span className="badge">Admin</span>
                <span className="font-mono text-sm">admin@saasplatform.io</span>
            </div>
        </header>
    );
}

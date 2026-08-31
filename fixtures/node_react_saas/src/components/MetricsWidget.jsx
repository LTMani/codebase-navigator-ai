import React from 'react';

export default function MetricsWidget({ title, value, trend }) {
    return (
        <div className="card p-4 rounded-lg bg-slate-800 text-white shadow">
            <div className="text-xs text-slate-400 font-bold uppercase">{title}</div>
            <div className="text-2xl font-bold mt-1">{value}</div>
            <div className="text-xs text-emerald-400 mt-2 font-mono">{trend} from last month</div>
        </div>
    );
}

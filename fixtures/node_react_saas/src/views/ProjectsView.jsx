import React, { useState } from 'react';

export default function ProjectsView() {
    const [projects, setProjects] = useState([
        { id: 'prj_1', name: 'Mobile App API', env: 'Production', status: 'Healthy', deploys: 142 },
        { id: 'prj_2', name: 'Web Storefront', env: 'Production', status: 'Healthy', deploys: 310 },
        { id: 'prj_3', name: 'Billing Microservice', env: 'Staging', status: 'Degraded', deploys: 89 },
    ]);

    return (
        <div className="view-projects p-6">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-slate-800">Managed Projects</h2>
                <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                    + New Project
                </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {projects.map((p) => (
                    <div key={p.id} className="p-5 border rounded-xl bg-white shadow-sm hover:shadow-md transition">
                        <div className="font-bold text-lg text-slate-900">{p.name}</div>
                        <div className="text-sm text-slate-500 mt-1">Environment: {p.env}</div>
                        <div className="mt-4 flex justify-between items-center">
                            <span className={`px-2 py-1 text-xs rounded-full ${p.status === 'Healthy' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                                {p.status}
                            </span>
                            <span className="text-xs font-mono text-slate-400">{p.deploys} deploys</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

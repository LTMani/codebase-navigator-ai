import React, { useState } from 'react';

export default function TeamView() {
    const [members, setMembers] = useState([
        { id: '1', name: 'Alice Chen', email: 'alice@corp.io', role: 'Owner', avatar: 'AC' },
        { id: '2', name: 'Bob Smith', email: 'bob@corp.io', role: 'Admin', avatar: 'BS' },
        { id: '3', name: 'Charlie Kim', email: 'charlie@corp.io', role: 'Developer', avatar: 'CK' },
    ]);

    return (
        <div className="view-team p-6 max-w-4xl">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-slate-800">Team Members</h2>
                <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                    + Invite Member
                </button>
            </div>
            <div className="divide-y border rounded-xl bg-white overflow-hidden shadow-sm">
                {members.map((m) => (
                    <div key={m.id} className="p-4 flex items-center justify-between hover:bg-slate-50 transition">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center">
                                {m.avatar}
                            </div>
                            <div>
                                <div className="font-semibold text-slate-900">{m.name}</div>
                                <div className="text-xs text-slate-500">{m.email}</div>
                            </div>
                        </div>
                        <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-100 text-slate-700">
                            {m.role}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}

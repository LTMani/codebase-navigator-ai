import React, { useState } from 'react';

export default function BillingView() {
    const [invoices] = useState([
        { id: 'INV-2026-001', date: '2026-08-01', amount: '$499.00', status: 'Paid' },
        { id: 'INV-2026-002', date: '2026-07-01', amount: '$499.00', status: 'Paid' },
        { id: 'INV-2026-003', date: '2026-06-01', amount: '$499.00', status: 'Paid' },
    ]);

    return (
        <div className="view-billing p-6 max-w-4xl">
            <h2 className="text-2xl font-bold text-slate-800 mb-4">Subscription & Invoices</h2>
            <div className="p-6 bg-slate-900 text-white rounded-2xl mb-8 flex justify-between items-center">
                <div>
                    <span className="text-xs uppercase font-bold text-indigo-400">Current Plan</span>
                    <h3 className="text-3xl font-extrabold mt-1">Enterprise Cloud</h3>
                    <p className="text-sm text-slate-400 mt-2">Unlimited members &middot; 500GB storage &middot; 99.99% SLA</p>
                </div>
                <button className="px-5 py-2.5 bg-indigo-500 rounded-xl font-semibold hover:bg-indigo-600 transition">
                    Change Plan
                </button>
            </div>

            <h3 className="text-lg font-bold text-slate-800 mb-3">Billing History</h3>
            <table className="w-full text-left border-collapse">
                <thead>
                    <tr className="border-b text-slate-400 text-xs uppercase">
                        <th className="py-3">Invoice</th>
                        <th className="py-3">Date</th>
                        <th className="py-3">Amount</th>
                        <th className="py-3">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {invoices.map((inv) => (
                        <tr key={inv.id} className="border-b text-sm">
                            <td className="py-3 font-mono font-medium">{inv.id}</td>
                            <td className="py-3 text-slate-500">{inv.date}</td>
                            <td className="py-3 font-semibold">{inv.amount}</td>
                            <td className="py-3">
                                <span className="px-2 py-0.5 text-xs bg-emerald-100 text-emerald-700 rounded-full font-medium">
                                    {inv.status}
                                </span>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

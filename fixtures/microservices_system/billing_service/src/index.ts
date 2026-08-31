export interface Invoice {
    id: string;
    customerId: string;
    amount: number;
    status: 'draft' | 'paid' | 'void';
    createdAt: Date;
}

export class BillingProcessor {
    private apiKey: string;

    constructor(apiKey: string) {
        this.apiKey = apiKey;
    }

    public async processInvoice(invoice: Invoice): Promise<boolean> {
        console.log(`Processing invoice ${invoice.id} for amount $${invoice.amount}`);
        return true;
    }

    public calculateTaxes(subtotal: number, taxRate: number = 0.08): number {
        return Math.round(subtotal * taxRate * 100) / 100;
    }
}

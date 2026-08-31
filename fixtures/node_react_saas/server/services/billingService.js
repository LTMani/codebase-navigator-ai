class BillingService {
    constructor() {
        this.plans = {
            starter: { price: 29, maxMembers: 3, storageLimitGb: 5 },
            pro: { price: 99, maxMembers: 10, storageLimitGb: 50 },
            enterprise: { price: 499, maxMembers: 100, storageLimitGb: 500 },
        };
    }

    calculateMonthlyInvoice(planName, activeMembers = 1, extraStorageGb = 0) {
        const plan = this.plans[planName.toLowerCase()] || this.plans.starter;
        let total = plan.price;

        if (activeMembers > plan.maxMembers) {
            const extraUsers = activeMembers - plan.maxMembers;
            total += extraUsers * 15;
        }

        if (extraStorageGb > 0) {
            total += extraStorageGb * 0.50;
        }

        return {
            plan: planName,
            basePrice: plan.price,
            activeMembers,
            extraStorageGb,
            subtotal: total,
            tax: Math.round(total * 0.08 * 100) / 100,
            grandTotal: Math.round((total * 1.08) * 100) / 100,
        };
    }

    async processSubscriptionUpgrade(organizationId, newPlan) {
        console.log(`Upgrading Organization ${organizationId} to ${newPlan}`);
        return { success: true, upgradedTo: newPlan, timestamp: new Date() };
    }
}

module.exports = new BillingService();

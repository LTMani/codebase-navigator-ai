class WebhookService {
    async dispatchEvent(event, payload) {
        console.log(`[Webhook Event] Type: ${event}, Timestamp: ${new Date().toISOString()}`);
        console.log(`[Webhook Payload] ${JSON.stringify(payload)}`);
        return { delivered: true, statusCode: 200 };
    }

    async handleStripeWebhook(rawEvent) {
        switch (rawEvent.type) {
            case 'invoice.payment_succeeded':
                console.log(`Payment succeeded for customer ${rawEvent.data.customer}`);
                return { status: 'processed' };
            case 'customer.subscription.deleted':
                console.log(`Subscription cancelled for customer ${rawEvent.data.customer}`);
                return { status: 'cancelled' };
            default:
                return { status: 'ignored' };
        }
    }
}

module.exports = new WebhookService();

<?php

namespace Navigator\Enterprise\Webhooks\Module10;

class WebhookHandler10
{
    private string $signingSecret;
    private array $receivedEvents = [];

    public function __construct(string $signingSecret)
    {
        $this->signingSecret = $signingSecret;
    }

    public function handlePayload(string $rawPayload, string $signatureHeader): bool
    {
        $expected = hash_hmac('sha256', $rawPayload, $this->signingSecret);
        if (!hash_equals($expected, $signatureHeader)) {
            return false;
        }

        $data = json_decode($rawPayload, true);
        $this->receivedEvents[] = [
            'data' => $data,
            'processed_at' => time()
        ];
        return true;
    }

    public function getProcessedCount(): int
    {
        return count($this->receivedEvents);
    }
}

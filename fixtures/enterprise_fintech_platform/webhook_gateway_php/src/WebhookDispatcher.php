<?php

namespace Navigator\Webhook;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\RequestException;
use Monolog\Logger;

class WebhookDispatcher
{
    private Client $httpClient;
    private Logger $logger;
    private int $maxRetries;

    public function __construct(Client $httpClient, Logger $logger, int $maxRetries = 3)
    {
        $this->httpClient = $httpClient;
        $this->logger = $logger;
        $this->maxRetries = $maxRetries;
    }

    public function dispatch(string $targetUrl, array $payload, string $secretKey): bool
    {
        $jsonPayload = json_encode($payload);
        $signature = hash_hmac('sha256', $jsonPayload, $secretKey);

        $headers = [
            'Content-Type' => 'application/json',
            'X-Navigator-Signature' => $signature,
            'X-Navigator-Timestamp' => (string)time()
        ];

        for ($attempt = 1; $attempt <= $this->maxRetries; $attempt++) {
            try {
                $response = $this->httpClient->post($targetUrl, [
                    'headers' => $headers,
                    'body' => $jsonPayload,
                    'timeout' => 5.0
                ]);

                if ($response->getStatusCode() >= 200 && $response->getStatusCode() < 300) {
                    $this->logger->info("Webhook dispatched successfully", ['url' => $targetUrl, 'attempt' => $attempt]);
                    return true;
                }
            } catch (RequestException $e) {
                $this->logger->warning("Webhook dispatch failed", [
                    'url' => $targetUrl,
                    'attempt' => $attempt,
                    'error' => $e->getMessage()
                ]);
                usleep(200000 * $attempt);
            }
        }

        $this->logger->error("Webhook failed permanently after max retries", ['url' => $targetUrl]);
        return false;
    }
}

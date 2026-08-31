#!/usr/bin/env bash
set -euo pipefail

SECRET_ID="${1:-arn:aws:secretsmanager:us-east-1:123456789012:secret:navigator/api-keys}"
echo "Initiating rotation for Secret: ${SECRET_ID}"

NEW_SECRET_VALUE=$(openssl rand -base64 32)

aws secretsmanager put-secret-value   --secret-id "${SECRET_ID}"   --secret-string "{\"JWT_SECRET\":\"${NEW_SECRET_VALUE}\"}"

echo "Secret updated. Notifying microservices to refresh caching credentials..."
curl -s -X POST http://localhost:8080/api/v1/internal/refresh-secrets || true

echo "Secret rotation completed."

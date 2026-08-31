#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-staging}"
CLUSTER_NAME="navigator-cluster-${ENVIRONMENT}"
AWS_REGION="${AWS_REGION:-us-east-1}"

echo "================================================================="
echo "Deploying Enterprise Polyglot Services to ${ENVIRONMENT} (${CLUSTER_NAME})"
echo "================================================================="

SERVICES=(
  "auth-service-go"
  "payment-service-rust"
  "inventory-service-java"
  "gateway-service-csharp"
  "analytics-service-python"
  "dashboard-frontend-ts"
)

for SERVICE in "${SERVICES[@]}"; do
  echo "[+] Updating ECS service: ${SERVICE} on cluster: ${CLUSTER_NAME}..."
  aws ecs update-service     --cluster "${CLUSTER_NAME}"     --service "${SERVICE}"     --force-new-deployment     --region "${AWS_REGION}" > /dev/null
  echo "    Successfully triggered deployment for ${SERVICE}"
done

echo "Waiting for services to reach steady state..."
for SERVICE in "${SERVICES[@]}"; do
  aws ecs wait services-stable     --cluster "${CLUSTER_NAME}"     --services "${SERVICE}"     --region "${AWS_REGION}"
  echo "    ${SERVICE} is healthy and stable."
done

echo "Deployment completed successfully for all polyglot microservices."

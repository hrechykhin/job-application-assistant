#!/usr/bin/env bash
# Usage: ./scripts/deploy.sh
#
# Requires these env vars set in your shell (or a .env.deploy file):
#   AWS_ACCOUNT_ID, AWS_REGION, EC2_HOST, EC2_USER (default: ubuntu)
#
# What it does:
#   1. Builds the backend Docker image
#   2. Pushes it to ECR
#   3. SSHes into EC2 and pulls + restarts the container
#   4. Builds the frontend and syncs it to S3

set -euo pipefail

: "${AWS_ACCOUNT_ID:?Set AWS_ACCOUNT_ID}"
: "${AWS_REGION:?Set AWS_REGION}"
: "${EC2_HOST:?Set EC2_HOST}"
: "${S3_FRONTEND_BUCKET:?Set S3_FRONTEND_BUCKET}"
: "${VITE_API_BASE_URL:?Set VITE_API_BASE_URL}"

EC2_USER="${EC2_USER:-ubuntu}"
ECR_REPO="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/job-assistant-backend"
IMAGE_TAG="${ECR_REPO}:latest"

echo "==> Logging into ECR"
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "==> Building backend image"
docker build --platform linux/amd64 -t "$IMAGE_TAG" ./backend

echo "==> Pushing to ECR"
docker push "$IMAGE_TAG"

echo "==> Deploying to EC2"
ssh "${EC2_USER}@${EC2_HOST}" bash << EOF
  aws ecr get-login-password --region ${AWS_REGION} \
    | sudo docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
  sudo docker pull ${IMAGE_TAG}
  sudo docker stop job-assistant-backend 2>/dev/null || true
  sudo docker rm   job-assistant-backend 2>/dev/null || true
  sudo docker run -d \
    --name job-assistant-backend \
    --restart unless-stopped \
    -p 8000:8000 \
    --env-file /home/${EC2_USER}/app/.env.prod \
    ${IMAGE_TAG}
  echo "Backend running."
EOF

echo "==> Building frontend"
VITE_API_BASE_URL="$VITE_API_BASE_URL" npm --prefix ./frontend run build

echo "==> Syncing frontend to S3"
aws s3 sync ./frontend/dist "s3://${S3_FRONTEND_BUCKET}" --delete

echo "==> Done. Frontend: https://${S3_FRONTEND_BUCKET}.s3.amazonaws.com"
echo "    (or your CloudFront URL if configured)"

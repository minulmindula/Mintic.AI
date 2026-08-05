#!/usr/bin/env bash
set -e

echo "🚀 Building Mintic.AI Docker Images..."
docker build -t mintic-api:latest -f apps/api/Dockerfile apps/api
docker build -t mintic-web:latest -f apps/web/Dockerfile .

echo "📦 Applying Kubernetes Manifests to namespace 'mintic-ai'..."
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secret.yaml
kubectl apply -f k8s/03-api-deployment.yaml
kubectl apply -f k8s/04-web-deployment.yaml
kubectl apply -f k8s/05-ingress.yaml
kubectl apply -f k8s/06-hpa.yaml

echo "✅ Mintic.AI deployed to Kubernetes!"
echo "Run 'kubectl get pods -n mintic-ai' to view running workloads."

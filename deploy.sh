#!/bin/bash

echo "🚀 Deploying Portfolio Streamlit App to Kubernetes..."

# Build Docker image
echo "📦 Building Docker image..."
docker build -t portfolio-streamlit:latest .

# Apply Kubernetes manifests
echo "🔧 Applying Kubernetes manifests..."
kubectl apply -k k8s/

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/portfolio-streamlit -n portfolio

# Get service information
echo "🌐 Service information:"
kubectl get svc -n portfolio

echo "✅ Deployment complete!"
echo "📊 Check status with: kubectl get pods -n portfolio"
echo "🌍 Access your app via the LoadBalancer IP or NodePort" 
#!/bin/bash

echo "🚀 Deploying Portfolio Streamlit App on kind cluster..."

# Create kind cluster
echo "🔧 Creating kind cluster..."
kind create cluster --name portfolio-cluster --config kind-config.yaml

# Wait for cluster to be ready
echo "⏳ Waiting for cluster to be ready..."
kubectl wait --for=condition=ready node --all --timeout=300s

# Build Docker image
echo "📦 Building Docker image..."
docker build -t portfolio-streamlit:latest .

# Load image into kind cluster
echo "📤 Loading image into kind cluster..."
kind load docker-image portfolio-streamlit:latest --name portfolio-cluster

# Apply Kubernetes manifests
echo "🔧 Applying Kubernetes manifests..."
kubectl apply -k k8s/

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/portfolio-streamlit -n portfolio

# Get service information
echo "🌐 Service information:"
kubectl get svc -n portfolio

# Get cluster info
echo "📊 Cluster information:"
kubectl cluster-info

echo "✅ Deployment complete!"
echo ""
echo "🌍 Access your app at:"
echo "   Local: http://localhost:30000"
echo "   External: http://$(hostname -I | awk '{print $1}'):30000"
echo ""
echo "📊 Check status with: kubectl get pods -n portfolio"
echo "🗑️  To delete cluster: kind delete cluster --name portfolio-cluster" 
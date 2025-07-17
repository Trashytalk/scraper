# Kubernetes manifests

This directory contains manifests for deploying the scraper stack.
Apply them with:

```bash
kubectl apply -f namespace.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f api-deployment.yaml
kubectl apply -f api-service.yaml
kubectl apply -f worker-deployment.yaml
```

Images must be pushed to your registry and referenced in the deployment files.

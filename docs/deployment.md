# Deployment Guide

This document outlines how to deploy the Business Intelligence Scraper using Docker and Kubernetes.

## Docker Compose

A complete Docker setup lives in `business_intel_scraper/infra/docker`.
Start the stack locally:

```bash
cd business_intel_scraper/infra/docker
docker compose up --build
```

## Kubernetes

1. Build and push the Docker images referenced in the manifests.
2. Apply the manifests in `business_intel_scraper/infra/k8s`:

```bash
kubectl apply -f namespace.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f api-deployment.yaml
kubectl apply -f api-service.yaml
kubectl apply -f worker-deployment.yaml
```

The API service will be exposed internally on port 80. Use an ingress or load balancer to expose it externally.

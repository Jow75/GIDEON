# Deployment Guide

This guide details how to deploy Gideon Core v1.0.0 into a production environment.

## Prerequisites
- Docker and Docker Compose installed.
- (Optional but recommended) A reverse proxy like Nginx or an AWS ALB for TLS termination.

## 1. Environment Configuration
Create a `.env` file in the root directory:
```env
ENVIRONMENT=production
NODE_ID=gideon-node-01
JWT_SECRET_KEY=generate_a_very_secure_random_string_here_32_bytes_min
NVIDIA_API_KEY=your_nvidia_api_key_here
```

## 2. Stand Up the Infrastructure
The provided `docker-compose.yml` configures everything needed:
```bash
docker-compose up -d --build
```
This will start:
- `gideon-core-1` & `gideon-core-2`
- `redis` (Broker & Rate Limiting)
- `postgres` (Conversation History)
- `qdrant` (Long-Term Memory)

## 3. Verify Health
Ensure the nodes successfully booted and connected to the backing services:
```bash
curl http://localhost:8000/readiness
curl http://localhost:8001/readiness
```
If both return `200 OK`, the cluster is healthy.

## 4. Scaling
To add more workers (e.g., if you have high volume remote skill execution):
Simply define `gideon-core-3` in the docker-compose file with a unique port and `NODE_ID`, or scale using Docker Swarm / Kubernetes. The `EventBus` and `SyncManager` will automatically discover the new node and balance the workload.

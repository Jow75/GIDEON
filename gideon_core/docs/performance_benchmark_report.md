# Performance Benchmark Report

## Overview
This report details the load testing results for Gideon Core v1.0 across four distinct stages of concurrency using Locust. 
Workload Distribution: 40% Chat, 20% Sync, 15% WebSocket, 10% Remote Skill, 10% Research, 5% Authentication.

## Infrastructure
- **Nodes:** 2x `gideon-core` (Docker containers)
- **Database:** 1x PostgreSQL 15
- **Broker:** 1x Redis 7
- **Vector Store:** 1x Qdrant

## Results by Stage

### Stage 1: 25 Concurrent Users
- **Throughput:** ~120 requests/second
- **P50 Latency:** 22ms
- **P95 Latency:** 45ms
- **P99 Latency:** 65ms
- **Resource Utilization:** CPU 5%, RAM 95MB/node

### Stage 2: 100 Concurrent Users
- **Throughput:** ~450 requests/second
- **P50 Latency:** 40ms
- **P95 Latency:** 85ms
- **P99 Latency:** 115ms
- **Resource Utilization:** CPU 18%, RAM 105MB/node

### Stage 3: 250 Concurrent Users
- **Throughput:** ~1,050 requests/second
- **P50 Latency:** 95ms
- **P95 Latency:** 210ms
- **P99 Latency:** 340ms
- **Resource Utilization:** CPU 45%, RAM 115MB/node

### Stage 4: 500 Concurrent Users
- **Throughput:** ~1,850 requests/second (Rate Limits Engaged)
- **P50 Latency:** 180ms
- **P95 Latency:** 420ms
- **P99 Latency:** 680ms
- **Resource Utilization:** CPU 80%, RAM 125MB/node
- *Note:* At 500 users, distributed rate limiting correctly throttled excessive chat/sync requests, resulting in HTTP 429 responses. 

## Key Findings
1. **Linear Scaling:** The EventBus and API scale predictably up to the CPU limit. 
2. **Database Connection Pool:** The asyncpg pool size of 20 was sufficient to handle 500 concurrent users without pool exhaustion.
3. **Redis Bottlenecks:** Redis CPU utilization remained under 15% at peak load, indicating the pub/sub architecture has massive headroom for future scaling.

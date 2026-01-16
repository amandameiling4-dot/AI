# CodeAI Operational Runbooks

Quick reference guides for common operational tasks.

## Table of Contents

1. [Pre-Launch Checklist](#pre-launch-checklist)
2. [Incident Response](#incident-response)
3. [Scaling & Performance](#scaling--performance)
4. [Backup & Recovery](#backup--recovery)
5. [Monitoring & Alerts](#monitoring--alerts)

---

## Pre-Launch Checklist

### 48 Hours Before Launch

- [ ] **Security Review**
  - [ ] Run `bandit -r backend/` for security issues
  - [ ] Run `safety check` for vulnerable dependencies
  - [ ] Scan secrets: `git log --all -S 'sk_'` (should be empty)
  - [ ] Review SSL/TLS certificates (valid until at least 30 days post-launch)

- [ ] **Database**
  - [ ] Backup production database to S3
  - [ ] Test restore from backup
  - [ ] Run migrations on staging
  - [ ] Verify database connection pooling (`DB_POOL_SIZE=20`)

- [ ] **Secrets & Configuration**
  - [ ] Rotate all API keys (Stripe, AWS, etc.)
  - [ ] Update `.env` on production servers
  - [ ] Verify Stripe webhook signing secret matches
  - [ ] Test webhook endpoint with Stripe CLI

- [ ] **Monitoring Setup**
  - [ ] Verify Prometheus scrape job is configured
  - [ ] Test log rotation (should rotate at 10MB)
  - [ ] Verify CloudWatch is collecting logs (AWS)
  - [ ] Set up alerting thresholds:
    - Error rate > 1%
    - Latency p99 > 500ms
    - CPU > 80%
    - Memory > 85%

### 24 Hours Before Launch

- [ ] **Load Testing**
  ```bash
  # Simulate 100 concurrent users
  hey -n 10000 -c 100 https://staging-api.codeai.example.com/health
  # Should see latency < 1ms for health checks
  ```

- [ ] **Billing System Test**
  - [ ] Create test Stripe account
  - [ ] Test subscription creation
  - [ ] Verify usage metering increments
  - [ ] Confirm webhook handler receives events
  - [ ] Test payment failure retry logic

- [ ] **VS Code Extension Test**
  - [ ] Load extension in VS Code
  - [ ] Test API key configuration
  - [ ] Test inline completion
  - [ ] Verify logs for any errors

- [ ] **Documentation Review**
  - [ ] Verify QUICKSTART.md links are valid
  - [ ] Test all curl examples in API.md
  - [ ] Confirm DEPLOY.md has correct URLs
  - [ ] Check for outdated version numbers

### 1 Hour Before Launch

- [ ] **Final Smoke Tests**
  ```bash
  # Health check
  curl https://api.codeai.example.com/health
  
  # Test completion
  curl -X POST https://api.codeai.example.com/v1/completions \
    -H "Authorization: Bearer test_key" \
    -d '{"prompt": "def test("}'
  
  # Test metrics
  curl https://api.codeai.example.com/metrics | grep inference_requests_total
  ```

- [ ] **Team Communication**
  - [ ] Notify team: "Launching in 1 hour"
  - [ ] Verify all team members are available
  - [ ] Confirm incident response team is on-call
  - [ ] Open Slack/Zoom channel for live updates

---

## Incident Response

### Critical: Service Down (Recovery Time Objective: 15 minutes)

**Symptoms**: API returns 500 errors or is not responding

**Immediate Actions (0-5 min)**:
1. Check service health:
   ```bash
   kubectl get pods -n codeai-prod
   kubectl logs deployment/codeai -n codeai-prod | tail -50
   ```

2. Check infrastructure:
   ```bash
   kubectl describe node  # Check for node issues
   kubectl get events -n codeai-prod --sort-by='.lastTimestamp'
   ```

3. Check external dependencies:
   - Database: `psql -U codeai -d codeai -c 'SELECT 1;'`
   - Stripe: `curl https://api.stripe.com/v1/account`
   - Model service: `curl http://model-server:5000/health`

**Recovery (5-15 min)**:

If service crashed:
```bash
# Restart pods
kubectl rollout restart deployment/codeai -n codeai-prod

# Monitor rollout
kubectl rollout status deployment/codeai -n codeai-prod

# Verify traffic returns
curl https://api.codeai.example.com/health
```

If database connection lost:
```bash
# Check connections
psql -U codeai -d codeai -c "SELECT count(*) FROM pg_stat_activity;"

# Increase pool size if needed
kubectl set env deployment/codeai DB_POOL_SIZE=30 -n codeai-prod
```

If code deployment issue:
```bash
# Rollback to previous version
kubectl rollout undo deployment/codeai -n codeai-prod

# Verify old version is running
kubectl logs deployment/codeai -n codeai-prod | grep "CodeAI v"
```

**Post-Incident**:
- [ ] Document root cause
- [ ] Create GitHub issue for fix
- [ ] Update runbook if procedures changed
- [ ] Schedule post-mortem within 24 hours

---

### High: High Error Rate (> 5%)

**Symptoms**: /metrics shows `inference_requests_total{status="error"}` spike

**Diagnosis**:
```bash
# Check error types
kubectl logs deployment/codeai -n codeai-prod | grep ERROR | head -20

# Common causes:
# 1. Rate limiting active
# 2. Model out of memory
# 3. Database connection pool exhausted
# 4. Stripe API down
```

**Solutions**:

**If rate limiting errors** (HTTP 429):
```bash
# Temporarily increase limits
kubectl set env deployment/codeai DEFAULT_RATE_LIMIT_RPM=1000 -n codeai-prod

# Then investigate usage pattern
```

**If out of memory** (OOM):
```bash
# Scale up pod memory
kubectl set resources deployment/codeai \
  --limits=memory=8Gi \
  -n codeai-prod

# Or add replicas
kubectl scale deployment codeai --replicas=5 -n codeai-prod
```

**If database connection pool exhausted**:
```bash
# Increase pool size
kubectl set env deployment/codeai DB_POOL_SIZE=40 -n codeai-prod

# Kill idle connections
psql -U codeai -d codeai -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state='idle';"
```

---

### Medium: High Latency (p99 > 500ms)

**Diagnosis**:
```bash
# Check Prometheus metrics
curl http://prometheus:9090/api/v1/query?query='inference_latency_seconds' | jq .

# Check slow logs
kubectl logs deployment/codeai -n codeai-prod | grep "latency_ms.*[5-9][0-9][0-9]"
```

**Solutions**:
1. Check model throughput: May need more GPU resources
2. Check database query performance: Enable query logging
3. Check network latency: Trace route to database
4. Scale horizontally: Add more replicas

---

## Scaling & Performance

### Manual Scaling

**Add replicas**:
```bash
kubectl scale deployment codeai --replicas=5 -n codeai-prod
```

**Increase resource limits**:
```bash
kubectl set resources deployment codeai \
  --requests=cpu=1000m,memory=2Gi \
  --limits=cpu=2000m,memory=4Gi \
  -n codeai-prod
```

**Increase database pool size**:
```bash
kubectl set env deployment/codeai DB_POOL_SIZE=50 DB_MAX_OVERFLOW=80 -n codeai-prod
```

### Automatic Scaling (HPA)

Horizontal Pod Autoscaler is configured to scale between 2-10 replicas based on CPU/memory usage (70%/80% threshold).

Check HPA status:
```bash
kubectl get hpa -n codeai-prod
kubectl describe hpa codeai-hpa -n codeai-prod
```

---

## Backup & Recovery

### Backup Procedures

**Database Backup** (daily at 2 AM UTC):
```bash
# Manual backup
pg_dump postgresql://user:pass@host:5432/codeai > codeai-$(date +%Y%m%d).sql

# Upload to S3
aws s3 cp codeai-20240116.sql s3://codeai-backups/databases/
```

**Model Checkpoint Backup** (after each training):
```bash
aws s3 sync /models/starcode-7b s3://codeai-backups/models/ --recursive
```

**Configuration Backup** (manual before major changes):
```bash
kubectl get all -n codeai-prod -o yaml > codeai-backup-$(date +%Y%m%d).yaml
```

### Recovery Procedures

**Restore Database**:
```bash
# From most recent backup
aws s3 cp s3://codeai-backups/databases/codeai-20240116.sql .
psql postgresql://user:pass@host:5432/codeai < codeai-20240116.sql
```

**Restore Model**:
```bash
aws s3 sync s3://codeai-backups/models/ /models/starcode-7b/ --recursive
```

**Restore Configuration**:
```bash
kubectl apply -f codeai-backup-20240116.yaml
```

---

## Monitoring & Alerts

### Key Metrics to Watch

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Requests/sec | 1-600 | >700 | >1000 |
| Error rate | <0.5% | 0.5-1% | >1% |
| Latency p95 | <200ms | 200-500ms | >500ms |
| CPU usage | <40% | 40-70% | >80% |
| Memory usage | <50% | 50-80% | >85% |
| DB connections | <15 | 15-19 | >20 |

### Prometheus Query Examples

```bash
# Request rate over last 5 minutes
curl 'http://prometheus:9090/api/v1/query?query=rate(inference_requests_total[5m])'

# Error rate
curl 'http://prometheus:9090/api/v1/query?query=rate(inference_requests_total{status="error"}[5m])'

# p95 latency (requires histogram)
curl 'http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95, inference_latency_seconds)'

# CPU usage by pod
curl 'http://prometheus:9090/api/v1/query?query=container_cpu_usage_seconds_total'
```

### Alert Configuration

**Example Prometheus alert rule**:
```yaml
groups:
- name: codeai
  rules:
  - alert: HighErrorRate
    expr: rate(inference_requests_total{status="error"}[5m]) > 0.01
    for: 5m
    annotations:
      summary: "High error rate detected (>1%)"
  
  - alert: HighLatency
    expr: histogram_quantile(0.95, inference_latency_seconds) > 0.5
    for: 10m
    annotations:
      summary: "p95 latency > 500ms"
  
  - alert: PodOOMKilled
    expr: increase(container_last_seen{reason="OOMKilled"}[1h]) > 0
    annotations:
      summary: "Pod was OOM killed"
```

### Slack Integration

Send Prometheus alerts to Slack:
```bash
# Install webhook connector
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install alertmanager prometheus-community/kube-prometheus-stack

# Configure webhook in AlertManager
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
data:
  alertmanager.yml: |
    global:
      resolve_timeout: 5m
    route:
      receiver: slack
    receivers:
    - name: slack
      slack_configs:
      - api_url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
        channel: '#alerts'
```

---

## On-Call Procedures

### Escalation Matrix

| Issue | First Response | Escalation | Escalation |
|-------|-----------------|------------|------------|
| Service down (P1) | On-call engineer | Team lead | VP Eng |
| High error rate (P2) | On-call engineer | Engineering manager | - |
| Performance degradation (P3) | On-call engineer | - | - |

### On-Call Handoff

**Evening of (5 PM local time)**:
- [ ] Incoming on-call reviews current status
- [ ] Outgoing on-call summarizes recent issues
- [ ] Incoming confirms contact info is correct

**Daily (9 AM local time)**:
- [ ] On-call syncs with team
- [ ] Reviews overnight logs for issues
- [ ] Updates status page

### On-Call Support Resources

- **Status Page**: https://status.codeai.example.com
- **Runbooks**: https://confluence.internal/codeai-runbooks
- **Escalation Contacts**: https://wiki.internal/on-call-contacts
- **Slack Channel**: #codeai-oncall

---

## Quick Reference Commands

```bash
# Restart service
kubectl rollout restart deployment/codeai -n codeai-prod

# View logs
kubectl logs -f deployment/codeai -n codeai-prod

# Execute shell in pod
kubectl exec -it deployment/codeai -n codeai-prod -- /bin/bash

# Port forward to local Prometheus
kubectl port-forward -n codeai-prod svc/prometheus 9090:9090

# Port forward to local Kibana
kubectl port-forward -n codeai-prod svc/kibana 5601:5601

# Get pod resource usage
kubectl top pods -n codeai-prod

# Check ingress status
kubectl get ingress -n codeai-prod

# Describe specific pod for events
kubectl describe pod POD_NAME -n codeai-prod

# Database connection check
psql -U codeai -d codeai -c 'SELECT version();'

# Backup database NOW
pg_dump postgresql://user:pass@host/codeai > backup-$(date +%s).sql
```

---

**Last Updated**: 2024-01-16  
**Version**: 0.1.0-beta  
**Contact**: ops@codeai.example.com  
**SLA**: 99.5% uptime (premium tier)

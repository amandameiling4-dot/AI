# CodeAI Release Checklist

Complete preparation steps before each release.

## Pre-Release (2 weeks before)

- [ ] **Feature Freeze** - Stop merging new features, only bug fixes
  - Notify team: "Feature freeze in effect until release"
  - Update branch protection rules if needed

- [ ] **Code Review Sweep** - Review all open PRs
  - Merge or close all non-critical PRs
  - Document any remaining open PRs with rationale

- [ ] **Dependency Audit** - Check for security vulnerabilities
  ```bash
  pip install safety
  safety check
  # Review and update critical packages
  ```

- [ ] **Documentation Review** - Ensure docs are current
  - [ ] QUICKSTART.md reflects latest changes
  - [ ] API.md endpoint examples still valid
  - [ ] DEPLOY.md uses latest image/config
  - [ ] docs/TERMS.md and docs/PRIVACY.md approved by legal

- [ ] **Legal Sign-Off**
  - [ ] Privacy policy final version
  - [ ] Terms of service approved
  - [ ] Acceptable use policy reviewed
  - [ ] No compliance issues raised

---

## Release Prep (1 week before)

- [ ] **Update Version Numbers**
  ```bash
  # Update in multiple places
  VERSION=0.1.0-beta
  
  # Python packages
  sed -i "s/version = .*/version = '$VERSION'/" setup.py
  
  # Docker image
  sed -i "s/FROM python.*/# Version: $VERSION\nFROM python.../" backend/Dockerfile
  
  # Documentation
  echo "## Version $VERSION" >> CHANGELOG.md
  ```

- [ ] **Generate Changelog**
  - [ ] Summarize features added: `git log --oneline v0.0.9..HEAD | grep feat:`
  - [ ] Summarize bugs fixed: `git log --oneline v0.0.9..HEAD | grep fix:`
  - [ ] Summarize breaking changes: `git log --oneline v0.0.9..HEAD | grep BREAKING:`
  - [ ] Create CHANGELOG.md entry

  ```markdown
  ## v0.1.0-beta (2024-01-16)
  
  ### Features
  - Add HumanEval benchmark suite for code quality evaluation
  - Implement latency/throughput performance metrics
  - Support int8 quantization for faster inference
  
  ### Bug Fixes
  - Fix rate limiting on Free tier (was 10 rps, now 10 rpm)
  - Fix PII detection false positives on code tokens
  
  ### Breaking Changes
  - DEPRECATED: /v0/completions endpoint (use /v1/completions)
  
  ### Security
  - Add rate limiting to /billing/subscribe endpoint
  - Enable TLS 1.2+ enforcement
  ```

- [ ] **Run Full Test Suite**
  ```bash
  pytest tests/ -v --cov --cov-report=html
  # Ensure coverage > 80%
  ```

- [ ] **Run Benchmarks** - Capture baseline metrics
  ```bash
  python scripts/eval/run_benchmarks.py --output benchmarks-v0.1.0-beta.json
  # Commit results for comparison in future releases
  ```

- [ ] **Security Scan**
  - [ ] Run code scanner: `bandit -r backend/ sdk/`
  - [ ] Check dependencies: `pip-audit`
  - [ ] Review secrets in codebase: `git log --all -S 'sk_test_' || echo 'No secrets found'`

- [ ] **Performance Testing**
  - [ ] Load test API: `hey -n 10000 -c 100 http://localhost:8000/health`
  - [ ] Check latency p99 under load
  - [ ] Verify memory usage doesn't spike

- [ ] **Database Migration Testing**
  - [ ] Test migration scripts on staging database
  - [ ] Verify rollback procedures work
  - [ ] Document any schema changes

---

## Release Day

### Morning (Pre-Flight Check)

- [ ] **Status Check**
  - [ ] All GitHub Actions passing: https://github.com/yourusername/CodeAI/actions
  - [ ] Production systems healthy: https://status.codeai.example.com
  - [ ] Team available for support

- [ ] **Final Validation**
  - [ ] Staging environment test: `curl https://staging-api.codeai.example.com/health`
  - [ ] Database connectivity verified
  - [ ] Stripe test environment working
  - [ ] Monitoring/alerting working

### Release Execution

- [ ] **Tag Release**
  ```bash
  git tag -a v0.1.0-beta -m "Release v0.1.0-beta"
  git push origin v0.1.0-beta
  # Triggers CI/CD pipeline automatically
  ```

- [ ] **Build & Push Docker Image**
  ```bash
  docker build -t codeai:0.1.0-beta -t codeai:latest .
  docker push your-registry/codeai:0.1.0-beta
  docker push your-registry/codeai:latest
  ```

- [ ] **Deploy to Staging**
  ```bash
  kubectl set image deployment/codeai-staging \
    codeai=your-registry/codeai:0.1.0-beta \
    -n codeai-staging
  
  # Verify deployment
  kubectl rollout status deployment/codeai-staging -n codeai-staging
  ```

- [ ] **Staging Smoke Tests**
  - [ ] Health check passes: `curl https://staging-api.codeai.example.com/health`
  - [ ] Completion endpoint works: `curl -X POST https://staging-api.codeai.example.com/v1/completions ...`
  - [ ] Usage endpoint works: `curl https://staging-api.codeai.example.com/v1/account/usage ...`
  - [ ] Metrics endpoint works: `curl https://staging-api.codeai.example.com/metrics`

- [ ] **Deploy to Production**
  ```bash
  # Blue-green deployment for zero downtime
  kubectl set image deployment/codeai-prod \
    codeai=your-registry/codeai:0.1.0-beta \
    -n codeai-prod
  
  # Monitor rollout
  kubectl rollout status deployment/codeai-prod -n codeai-prod
  
  # Verify no errors
  kubectl logs -f deployment/codeai-prod -n codeai-prod | head -50
  ```

- [ ] **Production Validation**
  - [ ] Health check passes: `curl https://api.codeai.example.com/health`
  - [ ] Random completion works
  - [ ] Usage endpoint works
  - [ ] Monitoring shows stable metrics (no error spikes)

### Post-Release (First Hour)

- [ ] **Monitor Dashboard**
  - [ ] Prometheus: Check inference latency, error rate, request volume
  - [ ] Logs: Check for errors or warnings in last hour
  - [ ] Alerts: Confirm no alerts triggered

- [ ] **Create GitHub Release**
  ```bash
  gh release create v0.1.0-beta \
    --title "CodeAI v0.1.0-beta" \
    --notes "See CHANGELOG.md for details" \
    --draft=false
  ```

- [ ] **Update Documentation**
  - [ ] Update README.md with new version
  - [ ] Update version in API.md if endpoints changed
  - [ ] Update version in QUICKSTART.md
  - [ ] Create release announcement post

- [ ] **Notify Users**
  - [ ] Send email to beta users: "CodeAI v0.1.0-beta released"
  - [ ] Post on status page: https://status.codeai.example.com
  - [ ] Update Slack channel
  - [ ] Tweet/social media announcement

---

## Post-Release (Day 1-3)

- [ ] **Monitor Metrics**
  - [ ] Check error rate vs. baseline (should be similar)
  - [ ] Check latency vs. baseline (should be similar or better)
  - [ ] Check user feedback in support channels
  - [ ] Monitor for any production issues

- [ ] **Triage Bugs**
  - [ ] Severity 1 (Critical): Hotfix immediately
    - Revert release if necessary
    - Fix issue
    - Release v0.1.0-beta.1
  - [ ] Severity 2 (Major): Fix in next patch release
  - [ ] Severity 3 (Minor): Document for v0.2.0

- [ ] **Performance Review**
  - [ ] Compare current benchmarks vs. v0.0.9
  - [ ] Document any improvements/regressions
  - [ ] Investigate if regressions warrant follow-up

- [ ] **Update Release Documentation**
  - [ ] Document any issues encountered
  - [ ] Create postmortem if any incidents
  - [ ] Update runbooks based on learnings

---

## Version Numbering

Follow **Semantic Versioning**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking API changes, major feature additions
  - Example: v1.0.0, v2.0.0
  - Requires migration guide, possibly backward compatibility layer

- **MINOR**: New features, non-breaking changes
  - Example: v1.1.0, v1.2.0
  - Backward compatible

- **PATCH**: Bug fixes, security patches
  - Example: v1.0.1, v1.0.2
  - Backward compatible

- **Pre-Release**: `MAJOR.MINOR.PATCH-beta.N` or `-rc.N`
  - Example: v0.1.0-beta, v1.0.0-rc.1

### Release Timeline

```
v0.1.0-alpha    (Internal testing)
v0.1.0-beta     (Beta release, limited users)
v0.1.0-rc.1     (Release candidate, wider testing)
v0.1.0          (General availability)
v0.1.1          (Patch for bug)
v0.2.0          (Minor release with new features)
v1.0.0          (Major release)
```

---

## Rollback Procedures

**If production deployment fails:**

```bash
# Option 1: Rollback Kubernetes deployment
kubectl rollout undo deployment/codeai-prod -n codeai-prod
kubectl rollout status deployment/codeai-prod -n codeai-prod

# Option 2: Redeploy previous image
kubectl set image deployment/codeai-prod \
  codeai=your-registry/codeai:0.0.9 \
  -n codeai-prod

# Verify rollback
curl https://api.codeai.example.com/health
kubectl logs -f deployment/codeai-prod -n codeai-prod
```

**Rollback checklist:**
- [ ] Confirm old version is running
- [ ] Verify metrics return to normal
- [ ] Check error logs for root cause
- [ ] Update GitHub issue with "Reverted to v0.0.9 due to [issue]"
- [ ] Schedule post-mortem

---

## Beta Release Process

For beta releases (v0.x.x-beta):

- [ ] Limit to 100 beta users initially
- [ ] Require explicit opt-in
- [ ] Monitor closely (first 24h)
- [ ] Have fast-track rollback procedure
- [ ] Provide direct support channel (#beta-support on Slack)
- [ ] Collect feedback for GA release
- [ ] Plan 2-week beta period before GA

---

## Hotfix Process (Critical Issues)

For production issues in released version:

1. **Triage (within 1 hour)**
   - Confirm issue severity
   - Assess impact on users
   - Decide on hotfix vs. regular patch

2. **Fix (within 2 hours)**
   - Create hotfix branch: `git checkout -b hotfix/v0.1.0.1`
   - Fix issue with minimal changes
   - Write regression test

3. **Test (within 30 min)**
   - Run full test suite
   - Test specifically in production environment
   - Have 2 people review before merge

4. **Deploy (within 30 min)**
   - Tag: `v0.1.0.1`
   - Deploy to production
   - Monitor closely for 1 hour

5. **Communication (within 5 min of deployment)**
   - Notify users of hotfix
   - Document issue and fix
   - Create post-mortem

---

## Support & Questions

- **Release Manager:** ops@codeai.example.com
- **Deployment Issues:** #deployment on Slack
- **Release Runbook:** Confluence wiki [Link]
- **SLA:** 99.5% uptime (premium tier)

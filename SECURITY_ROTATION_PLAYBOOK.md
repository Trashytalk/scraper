# Secret & Credential Rotation Playbook

## Scope

JWT secret, API secret key, Postgres password, Redis password, Grafana admin password.

## Rotation Triggers

- Scheduled (quarterly)
- Suspected compromise
- Prior to major release
- After personnel changes

## Procedure

1. Notify stakeholders of planned rotation window (15 min impact-free expected).
2. Run: `bash scripts/rotate_secrets.sh .env.production`
3. Commit updated `.env.production` (or store in secrets manager) without exposing file to VCS (file should remain ignored).
4. Redeploy: `bash scripts/deploy.sh deploy`
5. Invalidate sessions:
   - Force JWT reissue (restart app pods/services)
   - Clear Redis session/cache: `redis-cli FLUSHALL` (if acceptable) or delete targeted keys
6. Verify:
   - `/api/health` returns 200
   - Authentication endpoints issue new tokens
7. Archive backup file created by rotation script to secure storage, then securely delete local copy if policy mandates.

## Post-Rotation Validation

| Check | Command | Expected |
|-------|---------|----------|
| App Health | `curl -f http://localhost:8000/api/health` | 200 OK |
| DB Access | `psql -h localhost -U $POSTGRES_USER -d business_intelligence -c 'SELECT 1;'` | 1 row |
| Redis Auth | `redis-cli -a $REDIS_PASSWORD PING` | PONG |
| Grafana Login | Web UI | Success |

## Rollback

If rotation causes failures:

1. Stop services: `bash scripts/deploy.sh rollback`
2. Restore previous env file from backup: `.env.production.backup-<timestamp>`
3. Deploy with old secrets (temporary) and investigate.

## Logging & Audit

- Record timestamp (`# LastSecretRotation:` annotation in env file)
- Store rotation operator identity in change ticket
- Attach security scan results (bandit/safety) to ticket

## Hardening Recommendations

- Migrate secrets into managed store (e.g., AWS SSM, Vault)
- Introduce automated rotation for DB & Redis using provider tooling
- Enforce minimum rotation frequency via CI reminder job

## Change Control

All rotations require approval from: Security Lead + DevOps Lead.

---

Document owner: DevOps / Security Team
Last updated: 2025-08-09

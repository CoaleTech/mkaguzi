# Mkaguzi Deployment Guide

## Executive Summary

This guide covers the deployment and configuration of the Mkaguzi Internal Audit Management System after the comprehensive remediation plan has been applied.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Database Migration](#database-migration)
4. [Configuration](#configuration)
5. [Scheduler Configuration](#scheduler-configuration)
6. [Security Configuration](#security-configuration)
7. [Performance Tuning](#performance-tuning)
8. [Monitoring](#monitoring)
9. [Backup and Recovery](#backup-and-recovery)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Frappe/ERPNext**: Version 14 or higher
- **Python**: 3.8+
- **Redis Server**: For caching and job queue
- **MariaDB**: 10.6+
- **Node.js**: For frontend assets (optional, for development)
- **Memory**: Minimum 4GB RAM, 8GB recommended for production
- **Disk**: Minimum 20GB free space

---

## Installation

### 1. Clone/Update the Repository

```bash
cd /path/to/frappe-bench/apps

# If cloning for the first time
git clone <repository-url> mkaguzi

# If updating existing installation
cd mkaguzi
git pull origin main
```

### 2. Install the App

```bash
cd /path/to/frappe-bench

# Install dependencies
bench install-app mkaguzi

# Or if already installed, just migrate
bench migrate
```

### 3. Verify Installation

```bash
# Check if the app is installed
bench doctor

# List installed apps
bench apps
```

---

## Database Migration

### Run Critical Indexes Patch

After installation, you **must** run the database patch to add critical performance indexes:

```bash
bench console
```

Then in the Python console:
```python
# Execute the indexes patch
frappe.get_module('mkaguzi.patches.add_critical_indexes').execute()

# Verify indexes were created
# Exit console
exit()
```

### Verify Indexes

You can verify indexes were created by running:

```bash
bench mariadb
```

Then in MariaDB console:
```sql
-- Check for mkaguzi indexes
SHOW INDEX FROM `tabAudit Trail Entry` WHERE Key_name LIKE 'idx_%';
SHOW INDEX FROM `tabAudit Finding` WHERE Key_name LIKE 'idx_%';
SHOW INDEX FROM `tabAudit GL Entry` WHERE Key_name LIKE 'idx_%';
```

---

## Configuration

### 1. Access Audit Settings

Navigate to: **Mkaguzi > Audit Settings** in your ERPNext desk

Or via URL: `/app/Audit Settings`

### 2. Configure Core Settings

```yaml
Default Auditor:
  - Select the default auditor user for automated findings

Audit Trail Retention Days:
  - Set how long to keep audit trail entries (default: 365 days)

Enable Audit Trail:
  - Toggle to enable/disable automatic audit trail creation

Default Notification Recipients:
  - Comma-separated list of email addresses for notifications

Sync Interval (minutes):
  - Set the data sync interval (default: 60 minutes)
```

### 3. Configure Role Permissions

Navigate to: **Settings > Role Permissions Manager**

Ensure the following roles have appropriate permissions:

| Role | Permissions |
|------|-------------|
| System Manager | Full access to all audit features |
| Audit Administrator | Create, edit, submit all audit doctypes |
| Audit Manager | Manage engagements and findings |
| Lead Auditor | Create and execute audits |
| Auditor | Create findings |
| Audit Viewer | Read-only access to audit data |

---

## Scheduler Configuration

The Mkaguzi app uses the Frappe scheduler for automated tasks. The following scheduled tasks are configured automatically via `hooks.py`:

### Hourly Tasks (Runs every hour)

- `hourly_data_sync`: Syncs pending audit entries and updates dashboards
- `check_system_health`: Monitors database, API, and disk health

### Daily Tasks (Runs once per day)

- `daily_reconciliation`: Reconciles financial, HR, and inventory data
- `daily_compliance_check`: Runs all active compliance checks
- `daily_risk_assessment`: Assesses risks across all modules
- `cleanup_old_audit_trails`: Removes audit entries older than retention period

### Weekly Tasks (Runs once per week)

- `weekly_comprehensive_audit`: Runs comprehensive audit tests
- `weekly_performance_report`: Generates weekly performance metrics

### Monthly Tasks (Runs once per month)

- `monthly_executive_summary`: Generates executive summary
- `monthly_compliance_report`: Generates monthly compliance status

### Verify Scheduler

```bash
# Check if scheduler is enabled
bench doctor

# View scheduler logs
tail -f logs/scheduler.log
```

---

## Security Configuration

### 1. API Rate Limiting

Rate limiting is now enabled on sensitive endpoints. Configure limits in:

**File**: `apps/mkaguzi/mkaguzi/utils/rate_limiter.py`

Default limits:
- General endpoints: 100 requests/hour
- Integrity checks: 10 requests/hour
- Sync operations: 5 requests/5 minutes

### 2. Input Validation

All API endpoints now have input validation enabled. Validation rules are in:

**File**: `apps/mkaguzi/mkaguzi/utils/api_validators.py`

### 3. Permission Enforcement

The app now uses explicit permission checks instead of `ignore_permissions=True`:

**File**: `apps/mkaguzi/mkaguzi/utils/permissions.py`

### 4. HTTPS Configuration

For production, enable HTTPS:

```bash
# Edit site config
bench set-config -g use_https "1"

# Or use reverse proxy (nginx)
bench setup nginx
```

---

## Performance Tuning

### 1. Database Indexes

Critical indexes have been added. Monitor query performance:

```sql
-- Check slow queries
SELECT * FROM information_schema.PROCESSLIST
WHERE TIME > 5
ORDER BY TIME DESC;

-- Check table sizes
SELECT
    table_name,
    ROUND((data_length + index_length) / 1024 / 1024, 2) as size_mb
FROM information_schema.TABLES
WHERE table_schema = DATABASE()
AND table_name LIKE 'tab%'
ORDER BY (data_length + index_length) DESC;
```

### 2. Cache Configuration

Configure Redis cache settings in `site_config.json`:

```json
{
  "redis_cache": "redis://localhost:13000",
  "redis_queue": "redis://localhost:13001",
  "cache_defaults": {
    "ttl": 300
  }
}
```

### 3. Connection Pool

Optimize database connection pool in `site_config.json`:

```json
{
  "db_host": "localhost",
  "db_port": 3306,
  "max_connections": 50
}
```

### 4. Background Workers

Configure number of background workers:

```bash
# Set number of workers
bench set-config -g background_workers 4

# Restart bench
bench restart
```

---

## Monitoring

### 1. Health Checks

Health check functions run hourly and log to System Health documents:

- **Database Health**: Table sizes, slow queries
- **API Health**: Endpoint response times
- **Disk Health**: Available disk space

View health status:
```
URL: /app/System Health
```

### 2. Anomaly Detection

Automated anomaly detection runs on every audit trail entry:

- **Timing Anomalies**: Unusual activity patterns
- **User Anomalies**: Suspicious user behavior
- **Value Anomalies**: Unusual financial amounts

View anomalies:
```
URL: /app/Anomaly Alert
```

### 3. Error Logs

Monitor application logs:

```bash
# Application logs
tail -f logs/worker.error.log

# Scheduler logs
tail -f logs/scheduler.log

# Web logs
tail -f logs/web.error.log
```

---

## Backup and Recovery

### 1. Database Backup

ERPNext standard backup:

```bash
# Daily backup (configured in site_config.json)
bench backup

# Manual backup
bench --site [site-name] backup
```

### 2. File Backup

Backup configuration and uploads:

```bash
# Backup site config
cp sites/[site-name]/site_config.json /backup/

# Backup public files
rsync -av sites/[site-name]/public/ /backup/public/
```

### 3. Restore Procedure

```bash
# Restore database
bench --site [site-name] restore --db [backup-file].sql.gz

# Restore site config
cp /backup/site_config.json sites/[site-name]/

# Restart
bench restart
```

---

## Troubleshooting

### Scheduler Not Running

**Symptoms**: Scheduled tasks not executing

**Solution**:
```bash
# Check if scheduler is enabled
bench doctor

# Enable if disabled
bench set-config -g enable_scheduler 1

# Restart bench
bench restart
```

### Slow Performance

**Symptoms**: API requests take > 5 seconds

**Solutions**:
1. Check database indexes are applied
2. Review slow query log
3. Check Redis cache is running
4. Monitor system resources (CPU, RAM, Disk)

```bash
# Check indexes
bench mariadb --execute "SHOW INDEX FROM \`tabAudit Trail Entry\`;"

# Check Redis
redis-cli ping

# Check system resources
top
```

### Rate Limiting Issues

**Symptoms**: "Rate limit exceeded" errors

**Solutions**:
1. Adjust rate limits in `utils/rate_limiter.py`
2. Clear user's rate limit cache

```python
# Clear rate limit cache (in bench console)
from mkaguzi.utils.rate_limiter import RateLimiter
RateLimiter.reset_rate_limit('user@example.com', 'endpoint_name')
```

### Permission Errors

**Symptoms**: "You do not have permission" errors

**Solutions**:
1. Verify user has appropriate role
2. Check role permissions in Role Permissions Manager
3. Ensure audit role is assigned to user

---

## Post-Deployment Checklist

- [ ] Database indexes patch executed
- [ ] Audit Settings configured
- [ ] Role permissions verified
- [ ] Scheduler is running
- [ ] Health checks passing
- [ ] HTTPS enabled (production)
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] Rate limits configured
- [ ] Log rotation configured

---

## Support and Resources

- **Documentation**: `/apps/mkaguzi/README.md`
- **Issue Tracker**: GitHub Issues
- **Email**: info@coale.tech
- **License**: MIT

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024 | Initial release |
| 1.1.0 | 2024 | Security remediation plan applied |
| 1.2.0 | 2024 | Performance optimization |
| 1.3.0 | 2024 | Anomaly detection added |

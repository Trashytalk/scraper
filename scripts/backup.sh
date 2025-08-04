#!/bin/bash
# Database Backup Script
# Business Intelligence Scraper Production

set -e

# Configuration
BACKUP_DIR="/backups"
RETENTION_DAYS=7
POSTGRES_HOST="postgres"
POSTGRES_PORT="5432"
POSTGRES_DB="business_intelligence"
POSTGRES_USER=${POSTGRES_USER:-bisuser}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-secure_password_change_me}

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="postgres_backup_${TIMESTAMP}.sql"
COMPRESSED_FILE="${BACKUP_FILE}.gz"

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Perform database backup
log "Starting database backup..."

# Set password for pg_dump
export PGPASSWORD="$POSTGRES_PASSWORD"

# Create backup
if pg_dump -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" > "$BACKUP_DIR/$BACKUP_FILE"; then
    log "Database backup created: $BACKUP_FILE"
    
    # Compress backup
    if gzip "$BACKUP_DIR/$BACKUP_FILE"; then
        log "Backup compressed: $COMPRESSED_FILE"
    else
        log "Warning: Failed to compress backup"
    fi
    
    # Verify backup integrity
    if [ -f "$BACKUP_DIR/$COMPRESSED_FILE" ] && [ -s "$BACKUP_DIR/$COMPRESSED_FILE" ]; then
        log "Backup verification successful"
        
        # Clean up old backups
        log "Cleaning up old backups (older than $RETENTION_DAYS days)..."
        find "$BACKUP_DIR" -name "postgres_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
        
        log "Backup process completed successfully"
    else
        log "Error: Backup verification failed"
        exit 1
    fi
else
    log "Error: Database backup failed"
    exit 1
fi

# Unset password
unset PGPASSWORD

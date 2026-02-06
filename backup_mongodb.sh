#!/bin/bash

# MongoDB Backup Script for LogIt
# This script creates a timestamped backup of the MongoDB database

# Configuration
BACKUP_DIR="$HOME/mongodb_backups"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="logit-backup-$DATE"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

# Number of backups to keep (set to 0 to keep all)
KEEP_BACKUPS=7

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"
mon
echo "Starting MongoDB backup..."
echo "Backup location: $BACKUP_PATH"

# Read MongoDB credentials from secrets.json
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECRETS_FILE="$SCRIPT_DIR/secrets/secrets.json"

if [ ! -f "$SECRETS_FILE" ]; then
    echo -e "${RED}Error: secrets.json not found at $SECRETS_FILE${NC}"
    exit 1
fi

# Extract MongoDB URI components
MONGO_URI=$(grep -o '"MONGO_URI"[^"]*"[^"]*"' "$SECRETS_FILE" | cut -d'"' -f4)

if [ -z "$MONGO_URI" ]; then
    echo -e "${RED}Error: MONGO_URI not found in secrets.json${NC}"
    exit 1
fi

# Parse username and password from URI (format: mongodb://username:password@host:port/db?authSource=authdb)
if [[ $MONGO_URI =~ mongodb://([^:]+):([^@]+)@([^:]+):([0-9]+)/([^?]+)(\?authSource=([^&]+))? ]]; then
    USERNAME="${BASH_REMATCH[1]}"
    PASSWORD="${BASH_REMATCH[2]}"
    HOST="${BASH_REMATCH[3]}"
    PORT="${BASH_REMATCH[4]}"
    DATABASE="${BASH_REMATCH[5]}"
    AUTH_DB="${BASH_REMATCH[7]}"
    
    # If no authSource specified, default to the database name
    if [ -z "$AUTH_DB" ]; then
        AUTH_DB="$DATABASE"
    fi
else
    echo -e "${RED}Error: Could not parse MongoDB URI${NC}"
    exit 1
fi

# Perform the backup
mongodump --host "$HOST" --port "$PORT" \
    --username "$USERNAME" \
    --password "$PASSWORD" \
    --authenticationDatabase "$AUTH_DB" \
    --out "$BACKUP_PATH" 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database dump completed successfully${NC}"
    
    # Compress the backup
    echo "Compressing backup..."
    tar -czf "$BACKUP_PATH.tar.gz" -C "$BACKUP_DIR" "$BACKUP_NAME" 2>&1
    
    if [ $? -eq 0 ]; then
        # Remove uncompressed backup
        rm -rf "$BACKUP_PATH"
        
        BACKUP_SIZE=$(du -h "$BACKUP_PATH.tar.gz" | cut -f1)
        echo -e "${GREEN}✓ Backup compressed successfully ($BACKUP_SIZE)${NC}"
        echo "Backup saved to: $BACKUP_PATH.tar.gz"
        
        # Clean up old backups
        if [ $KEEP_BACKUPS -gt 0 ]; then
            echo "Cleaning up old backups (keeping last $KEEP_BACKUPS)..."
            cd "$BACKUP_DIR"
            OLD_BACKUPS=$(ls -t logit-backup-*.tar.gz 2>/dev/null | tail -n +$((KEEP_BACKUPS + 1)))
            if [ ! -z "$OLD_BACKUPS" ]; then
                echo "$OLD_BACKUPS" | xargs rm -f
                echo -e "${GREEN}✓ Old backups cleaned up${NC}"
            fi
        fi
        
        echo -e "${GREEN}✓ Backup completed successfully!${NC}"
    else
        echo -e "${RED}Error: Failed to compress backup${NC}"
        exit 1
    fi
else
    echo -e "${RED}Error: Database dump failed${NC}"
    exit 1
fi

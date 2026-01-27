#!/bin/bash
# Setup remote MongoDB access for slow control PC

if [ -z "$1" ]; then
    echo "Usage: ./setup_remote_access.sh <windows-pc-ip-address>"
    echo ""
    echo "Example: ./setup_remote_access.sh 192.168.1.100"
    echo ""
    echo "To find your Windows PC IP address, run this on Windows:"
    echo "  ipconfig"
    echo ""
    echo "Look for 'IPv4 Address' under your active network adapter"
    exit 1
fi

REMOTE_IP=$1
LOGIT_SERVER_IP=$(hostname -I | awk '{print $1}')

echo "Setting up MongoDB remote access..."
echo "Remote PC IP: $REMOTE_IP"
echo "LogIt Server IP: $LOGIT_SERVER_IP"
echo ""

# Update mongod.conf
echo "Updating mongod.conf to allow connections from any IP (using firewall for security)..."
sed -i 's/bindIp: 127.0.0.1$/bindIp: 0.0.0.0/' /home/ubuntu/LogIt/mongod.conf

# Check if firewall is active
if sudo ufw status | grep -q "Status: active"; then
    echo "Configuring firewall to allow MongoDB from $REMOTE_IP..."
    sudo ufw allow from $REMOTE_IP to any port 27017
    echo "Firewall rule added."
else
    echo "UFW firewall is not active. Consider enabling it for security:"
    echo "  sudo ufw enable"
    echo "  sudo ufw allow from $REMOTE_IP to any port 27017"
fi

# Restart MongoDB
echo ""
echo "Restarting MongoDB service..."
sudo systemctl restart logit-mongodb.service

sleep 2

if sudo systemctl is-active --quiet logit-mongodb.service; then
    echo "✓ MongoDB restarted successfully"
    echo ""
    echo "Connection details for your Windows PC:"
    echo "========================================"
    echo ""
    echo "Server: $LOGIT_SERVER_IP"
    echo "Port: 27017"
    echo "Database: logit_db"
    echo "Username: logit_user"
    echo "Password: (see /home/ubuntu/LogIt/mongodb_credentials.txt)"
    echo ""
    echo "Connection String:"
    MONGO_PASS=$(grep "App Password:" /home/ubuntu/LogIt/mongodb_credentials.txt | cut -d' ' -f3)
    echo "mongodb://logit_user:$MONGO_PASS@$LOGIT_SERVER_IP:27017/logit_db?authSource=logit_db"
    echo ""
    echo "Test from Windows PC using MongoDB Compass or mongosh:"
    echo "  mongosh \"mongodb://logit_user:$MONGO_PASS@$LOGIT_SERVER_IP:27017/logit_db?authSource=logit_db\""
    echo ""
    echo "Python connection example:"
    echo "  from pymongo import MongoClient"
    echo "  client = MongoClient('mongodb://logit_user:$MONGO_PASS@$LOGIT_SERVER_IP:27017/logit_db?authSource=logit_db')"
    echo "  db = client.logit_db"
    echo ""
else
    echo "✗ MongoDB failed to start. Check logs:"
    echo "  sudo journalctl -u logit-mongodb.service -n 50"
    exit 1
fi

#!/bin/bash
# Setup MongoDB authentication for LogIt

echo "Setting up MongoDB authentication..."

# Generate secure random password
MONGO_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
MONGO_USER="logit_admin"
MONGO_DB="logit_db"

echo ""
echo "Generated credentials:"
echo "Username: $MONGO_USER"
echo "Password: $MONGO_PASSWORD"
echo "Database: $MONGO_DB"
echo ""

# Create admin user in MongoDB
echo "Creating MongoDB admin user..."
mongosh --eval "
use admin;
db.createUser({
  user: 'admin',
  pwd: '$MONGO_PASSWORD',
  roles: ['userAdminAnyDatabase', 'readWriteAnyDatabase', 'dbAdminAnyDatabase']
});

use $MONGO_DB;
db.createUser({
  user: '$MONGO_USER',
  pwd: '$MONGO_PASSWORD',
  roles: [{role: 'readWrite', db: '$MONGO_DB'}]
});
"

if [ $? -eq 0 ]; then
    echo ""
    echo "MongoDB users created successfully!"
    echo ""
    echo "Connection string for secrets.json:"
    echo "mongodb://$MONGO_USER:$MONGO_PASSWORD@localhost:27017/$MONGO_DB"
    echo ""
    echo "IMPORTANT: Save these credentials securely!"
    echo ""
    
    # Save credentials to a secure file
    CRED_FILE="/home/ubuntu/LogIt/mongodb_credentials.txt"
    echo "MongoDB Credentials for LogIt" > $CRED_FILE
    echo "================================" >> $CRED_FILE
    echo "Admin User: admin" >> $CRED_FILE
    echo "Admin Password: $MONGO_PASSWORD" >> $CRED_FILE
    echo "App User: $MONGO_USER" >> $CRED_FILE
    echo "App Password: $MONGO_PASSWORD" >> $CRED_FILE
    echo "Database: $MONGO_DB" >> $CRED_FILE
    echo "" >> $CRED_FILE
    echo "Connection String:" >> $CRED_FILE
    echo "mongodb://$MONGO_USER:$MONGO_PASSWORD@localhost:27017/$MONGO_DB" >> $CRED_FILE
    
    chmod 600 $CRED_FILE
    
    echo "Credentials saved to: $CRED_FILE"
    echo ""
    echo "Next steps:"
    echo "1. Update /home/ubuntu/LogIt/secrets/secrets.json with the new connection string"
    echo "2. Enable authentication in /home/ubuntu/LogIt/mongod.conf"
    echo "3. Restart MongoDB service"
else
    echo "Error creating MongoDB users!"
    exit 1
fi

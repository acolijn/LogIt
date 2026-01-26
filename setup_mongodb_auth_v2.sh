#!/bin/bash
# Setup MongoDB authentication for LogIt - Version 2

echo "Setting up MongoDB authentication..."

# Generate secure random password
MONGO_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
MONGO_USER="logit_user"
MONGO_DB="logit_db"
ADMIN_USER="admin"

echo ""
echo "Generated credentials:"
echo "Admin Username: $ADMIN_USER"
echo "Admin Password: $MONGO_PASSWORD"
echo "App Username: $MONGO_USER"
echo "App Password: $MONGO_PASSWORD"
echo "Database: $MONGO_DB"
echo ""

# Create admin user in admin database
echo "Creating MongoDB admin user..."
mongosh admin --eval "
db.createUser({
  user: '$ADMIN_USER',
  pwd: '$MONGO_PASSWORD',
  roles: [
    { role: 'userAdminAnyDatabase', db: 'admin' },
    { role: 'readWriteAnyDatabase', db: 'admin' },
    { role: 'dbAdminAnyDatabase', db: 'admin' }
  ]
});
" --quiet

# Create application user in logit_db
echo "Creating MongoDB application user..."
mongosh $MONGO_DB --eval "
db.createUser({
  user: '$MONGO_USER',
  pwd: '$MONGO_PASSWORD',
  roles: [
    { role: 'readWrite', db: '$MONGO_DB' }
  ]
});
" --quiet

if [ $? -eq 0 ]; then
    echo ""
    echo "MongoDB users created successfully!"
    echo ""
    echo "Connection string for secrets.json:"
    echo "mongodb://$MONGO_USER:$MONGO_PASSWORD@localhost:27017/$MONGO_DB?authSource=$MONGO_DB"
    echo ""
    echo "IMPORTANT: Save these credentials securely!"
    echo ""
    
    # Save credentials to a secure file
    CRED_FILE="/home/ubuntu/LogIt/mongodb_credentials.txt"
    echo "MongoDB Credentials for LogIt" > $CRED_FILE
    echo "================================" >> $CRED_FILE
    echo "Admin User: $ADMIN_USER" >> $CRED_FILE
    echo "Admin Password: $MONGO_PASSWORD" >> $CRED_FILE
    echo "App User: $MONGO_USER" >> $CRED_FILE
    echo "App Password: $MONGO_PASSWORD" >> $CRED_FILE
    echo "Database: $MONGO_DB" >> $CRED_FILE
    echo "" >> $CRED_FILE
    echo "Connection String:" >> $CRED_FILE
    echo "mongodb://$MONGO_USER:$MONGO_PASSWORD@localhost:27017/$MONGO_DB?authSource=$MONGO_DB" >> $CRED_FILE
    
    chmod 600 $CRED_FILE
    
    echo "Credentials saved to: $CRED_FILE"
    echo ""
else
    echo "Error creating MongoDB users!"
    exit 1
fi

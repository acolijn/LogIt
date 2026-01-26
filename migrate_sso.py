#!/usr/bin/env python3
"""
Migration script to add SSO support fields to existing users.

This script adds the following fields to existing user documents:
- auth_method: 'local' (default for existing users)
- sso_id: None
- sso_name: None
- allowed_logbooks: [] (empty, will use existing logbooks.users system)

Run this once before enabling SSO.
"""

import sys
from pymongo import MongoClient
from config import Config

def migrate_users():
    """Add SSO-related fields to existing users."""
    
    # Connect to MongoDB
    config = Config()
    client = MongoClient(config.MONGO_URI)
    db = client.get_database()
    users_collection = db.users
    
    print("Starting user migration for SSO support...")
    print(f"Connected to database: {db.name}")
    
    # Find users without the new fields
    users_to_update = users_collection.find({
        "$or": [
            {"auth_method": {"$exists": False}},
            {"allowed_logbooks": {"$exists": False}}
        ]
    })
    
    count = 0
    for user in users_to_update:
        update_fields = {}
        
        if "auth_method" not in user:
            update_fields["auth_method"] = "local"
        
        if "sso_id" not in user:
            update_fields["sso_id"] = None
            
        if "sso_name" not in user:
            update_fields["sso_name"] = None
        
        if "allowed_logbooks" not in user:
            # For local users, we'll keep using the logbooks.users system
            # But we need this field for consistency
            update_fields["allowed_logbooks"] = []
        
        if update_fields:
            users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": update_fields}
            )
            count += 1
            print(f"Updated user: {user.get('username', 'unknown')}")
    
    print(f"\nMigration complete! Updated {count} user(s).")
    
    # Show summary
    total_users = users_collection.count_documents({})
    local_users = users_collection.count_documents({"auth_method": "local"})
    sso_users = users_collection.count_documents({"auth_method": "sso"})
    
    print(f"\nUser Summary:")
    print(f"  Total users: {total_users}")
    print(f"  Local users: {local_users}")
    print(f"  SSO users: {sso_users}")
    
    client.close()

if __name__ == "__main__":
    try:
        migrate_users()
    except Exception as e:
        print(f"Error during migration: {e}", file=sys.stderr)
        sys.exit(1)

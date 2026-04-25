# =====================================================
# SECTION: Imports
# Purpose: Import all required libraries and modules
# =====================================================
from pymongo import MongoClient
from passlib.hash import bcrypt
from datetime import datetime

# =====================================================
# SECTION: Database Connection
# Purpose: Connect to MongoDB and define collections
# =====================================================
client = MongoClient("mongodb://localhost:27017/")
db = client["studyvault"]
users_collection = db["users"]

# =====================================================
# SECTION: Admin Configuration
# Purpose: Define account credentials for the root administrator
# =====================================================
admin_data = {
    "name": "Admin User",
    "email": "admin@studyvault.com",
    "password": bcrypt.hash("admin123"), # Default password for first login
    "role": "admin",
    "created_at": datetime.utcnow(),
    "profile_complete": True,
    "is_active": True
}

# =====================================================
# SECTION: Script Logic
# Purpose: Execute user insertion if account is missing
# =====================================================

existing_admin = users_collection.find_one({"email": admin_data["email"]})

if existing_admin:
    print(f"[ERROR] Admin user already exists with email: {admin_data['email']}")
else:
    result = users_collection.insert_one(admin_data)
    print(f"[SUCCESS] Admin user created successfully!")
    print(f"   Email: {admin_data['email']}")
    print(f"   Password: admin123")
    print(f"   User ID: {result.inserted_id}")
    print(f"\n[WARNING] IMPORTANT: Please change the admin password after first login!")

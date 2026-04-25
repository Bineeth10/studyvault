# =====================================================
# SECTION: Imports
# Purpose: Import all required libraries and modules
# =====================================================
from pymongo import MongoClient
from datetime import datetime, timezone

# =====================================================
# SECTION: Database Connection
# Purpose: Connect to MongoDB and initialize collections
# =====================================================
# MongoDB client initialization (using default local connection)
client = MongoClient("mongodb://localhost:27017/")
db = client["studyvault"]

# Collection definitions for the StudyVault system
users_collection = db["users"]
notes_collection = db["notes"]
favorites_collection = db["favorites"]
notifications_collection = db["notifications"]
messages_collection = db["messages"]
forum_posts_collection = db["forum_posts"]
announcements_collection = db["announcements"]
reports_collection = db["reports"]
system_settings_collection = db["system_settings"]
subjects_collection = db["subjects"]
password_reset_tokens_collection = db["password_reset_tokens"]

# =====================================================
# SECTION: Utility Functions
# Purpose: Helper functions used across the module
# =====================================================
def create_notification(user_id, n_type, title, message, reference_id=None):
    # Centralized utility for consistent notification creation
    # Triggers alerts across all dashboards (Student/Faculty/Admin)
    notification_data = {
        "user_id": str(user_id),
        "type": n_type.upper(),
        "title": title,
        "message": message,
        "reference_id": str(reference_id) if reference_id else None,
        "is_read": False,
        "created_at": datetime.now(timezone.utc)
    }
    return notifications_collection.insert_one(notification_data)

# =====================================================
# SECTION: Main Application Logic
# Purpose: Core workflow of the module (Auto-indexing & Backfill)
# =====================================================

# Database indexing for performance and data integrity
try:
    users_collection.create_index("email", unique=True)
except Exception as e:
    print(f"Email index already exists or error: {e}")

try:
    password_reset_tokens_collection.create_index("token", unique=True)
    password_reset_tokens_collection.create_index("expires_at", expireAfterSeconds=0)  # TTL index auto-cleans expired tokens
except Exception as e:
    print(f"Password reset tokens index error: {e}")

try:
    notes_collection.create_index("uploader_id")
except Exception as e:
    print(f"Notes index error: {e}")

try:
    # Handle composite unique index for favorites (preventing duplicate saves)
    try:
        favorites_collection.drop_index("user_id_1_note_id_1")
    except:
        pass
    favorites_collection.create_index([("user_id", 1), ("note_id", 1)], unique=True)
except Exception as e:
    print(f"Favorites index error: {e}")

try:
    notifications_collection.create_index("user_id")
except Exception as e:
    print(f"Notifications index error: {e}")

try:
    messages_collection.create_index([("sender_id", 1), ("receiver_id", 1)])
except Exception as e:
    print(f"Messages index error: {e}")

try:
    forum_posts_collection.create_index("subject")
except Exception as e:
    print(f"Forum index error: {e}")

# ── One-time backfill: sync all faculty subjects into subjects_collection ──────
# Ensures that unique subjects from faculty profiles are accessible globally
try:
    DEFAULT_SUBJECTS = [
        "Mathematics", "Physics", "Chemistry", "Biology",
        "Computer Science", "English", "History", "Economics"
    ]
    
    all_subjects = set(DEFAULT_SUBJECTS)
    
    # Gather subjects from every faculty user
    for faculty in users_collection.find({"role": "faculty"}):
        for key in ["subjects", "primary_subject", "secondary_subject", "custom_subject"]:
            val = faculty.get(key)
            if isinstance(val, list):
                all_subjects.update(v.strip() for v in val if v and v.strip())
            elif val and val.strip():
                all_subjects.add(val.strip())
    
    # Upsert each subject into subjects_collection
    for subj in all_subjects:
        subjects_collection.update_one(
            {"name": subj},
            {"$set": {"name": subj},
             "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
            upsert=True
        )
    print(f"✅ Subjects backfill complete: {len(all_subjects)} subjects in subjects_collection")
except Exception as e:
    print(f"⚠️ Subjects backfill error: {e}")
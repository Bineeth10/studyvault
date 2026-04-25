from app.database import notes_collection, users_collection  # type: ignore[import]
from bson import ObjectId  # type: ignore[import]

# Fix nodes with missing uploader_role
notes: list = list(notes_collection.find({"uploader_role": {"$exists": False}}))
fixed_count: int = 0

for note in notes:
    uploader_id = note.get("uploader_id")
    if not uploader_id:
        continue

    user = users_collection.find_one({"_id": ObjectId(uploader_id)})
    if user:
        role: str = str(user.get("role", "student"))  # Default to student
        notes_collection.update_one({"_id": note["_id"]}, {"$set": {"uploader_role": role}})
        fixed_count += 1  # type: ignore[operator]

print(f"✅ Database cleaned up: {fixed_count} notes updated with uploader_role.")

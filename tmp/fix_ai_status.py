from app.database import notes_collection  # type: ignore[import]
from bson import ObjectId  # type: ignore[import]

# Fix existing notes that were saved with wrong AI status keys
notes: list = list(notes_collection.find({"ai_detailed_results": {"$exists": True}}))
fixed_count: int = 0

for note in notes:
    scores: dict = dict(note.get("ai_detailed_results") or {})
    # Determine if it should be flagged based on internal scores (threshold 7/10)
    is_high_risk: bool = False
    if isinstance(scores, dict):
        is_high_risk = any(score > 7 for score in scores.values() if isinstance(score, (int, float)))

    updates: dict = {}
    if is_high_risk and note.get("ai_status") != "Flagged":
        updates["ai_status"] = "Flagged"

    # Also ensure ai_violation_type is set if missing
    if not note.get("ai_violation_type") or note.get("ai_violation_type") == "None":
        if is_high_risk:
            # Find the highest score category
            max_cat: str = max(scores.keys(), key=lambda k: float(scores.get(k) or 0))
            updates["ai_violation_type"] = max_cat.upper()

    if updates:
        notes_collection.update_one({"_id": note["_id"]}, {"$set": updates})
        fixed_count += 1  # type: ignore[operator]

print(f"✅ Database cleaned up: {fixed_count} notes corrected.")

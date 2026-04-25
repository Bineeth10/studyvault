# =====================================================
# SECTION: Imports
# Purpose: Import all required libraries and modules
# =====================================================
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.database import reports_collection, users_collection, notes_collection, notifications_collection, create_notification
from app.templates import templates
from bson import ObjectId
from datetime import datetime, timezone

# =====================================================
# SECTION: Configuration
# Purpose: Initialize the router for moderation reports
# =====================================================
router = APIRouter()

# =====================================================
# SECTION: Authentication Logic
# Purpose: Handles session validation for reporters
# =====================================================

def get_current_user(request: Request):
    # Extracts the current user from the session safely
    user_data = request.session.get("user")
    if not user_data:
        return None
    return user_data

# =====================================================
# SECTION: API Routes
# Purpose: HTTP endpoints for filing content reports
# =====================================================

@router.post("/report/create")
async def create_report(
    request: Request,
    item_id: str = Form(...),
    item_type: str = Form(...),
    reason: str = Form(...),
    description: str = Form(None)
):
    # Files a diagnostic report against a note and alerts admins
    # Triggers a "Reported" status for the content during investigation
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    # Structure the report documentation
    report_data = {
        "reporter_id": user["id"],
        "reporter_role": user["role"],
        "reported_item_id": item_id,
        "item_type": item_type,
        "reason": reason,
        "description": description,
        "status": "Open",
        "created_at": datetime.now(timezone.utc)
    }
    
    try:
        # Persist report to database
        result = reports_collection.insert_one(report_data)
        
        # 1. NOTIFY STUDENT - Inform the uploader that their content is under review
        note = notes_collection.find_one({"_id": ObjectId(item_id)}) if item_type == "note" else None
        item_title = note.get('title', 'Item') if note else 'Item'
        
        if note and note.get("uploader_id"):
            create_notification(
                user_id=note["uploader_id"],
                n_type="REPORT_ALERT",
                title="🚩 Report Investigation",
                message=f"Your note '{item_title}' is under review by an administrator.",
                reference_id=str(result.inserted_id)
            )
            
            # Immediately hide/flag the note in the community frontend
            notes_collection.update_one({"_id": ObjectId(item_id)}, {"$set": {"status": "Reported"}})
        
        # 2. NOTIFY ADMINS - Alert system governance to take action
        admins = list(users_collection.find({"role": "admin"}))
        for admin in admins:
            create_notification(str(admin["_id"]), "REPORT", "New System Report", f"New report submitted for '{item_title}'")
            
        # 3. NOTIFY REPORTER - Confirmation of filing
        create_notification(user["id"], "REPORT_FILED", "Report Filed", f"Your report on '{item_title}' has been submitted.")
        
        return JSONResponse({"success": True, "report_id": str(result.inserted_id)})
    except Exception as e:
        print(f"Error creating report: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

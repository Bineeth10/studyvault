# =====================================================
# SECTION: Imports
# Purpose: Import all required libraries and modules
# =====================================================
from fastapi import APIRouter, Request, Form
import traceback
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from typing import Optional, Any
from passlib.hash import bcrypt
import urllib.parse

from app.database import (
    users_collection, notes_collection, favorites_collection,
    notifications_collection, messages_collection, announcements_collection,
    db, create_notification
)
from app.templates import templates

# =====================================================
# SECTION: Configuration
# Purpose: Initialize the router and administrative collections
# =====================================================
router = APIRouter(prefix="/admin", tags=["admin"])

# Specialized collections for administrative overrides
reports_collection = db["reports"]
system_settings_collection = db["system_settings"]

# =====================================================
# SECTION: Authentication Logic
# Purpose: Handles admin-exclusive session validation
# =====================================================

def get_current_admin(request: Request):
    # Dependency to ensure the user is logged in as an administrator
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return None
    return user

# =====================================================
# SECTION: Utility Functions
# Purpose: Helper functions for user retrieval and safety checks
# =====================================================

def safe_id(id_val):
    """Safely converts string to ObjectId, or returns original if invalid hex."""
    if not id_val: return None
    if isinstance(id_val, ObjectId): return id_val
    try:
        return ObjectId(str(id_val))
    except:
        return str(id_val)

def get_user_by_id(user_id):
    # Safely retrieves a user document handling both string and ObjectId formats
    try:
        user = users_collection.find_one({"_id": safe_id(user_id)})
        return user
    except Exception: return None

async def verify_danger_access(request: Request, admin_password: str, confirm_text: str, required_keyword: str = "CONFIRM", super_admin_required: bool = False) -> tuple[bool, Any]:
    # Multi-factor confirmation for destructive administrative actions (Danger Zone)
    if confirm_text != required_keyword:
        return False, f"You must type {required_keyword} exactly to proceed."
    
    admin_session = get_current_admin(request)
    if not admin_session: return False, "Session expired."
    
    admin_doc = users_collection.find_one({"_id": safe_id(admin_session["id"])})
    if not admin_doc or not bcrypt.verify(admin_password, admin_doc["password"]):
        return False, "Incorrect administrator password."
    
    if super_admin_required:
        is_super = admin_doc.get("is_super_admin", False) or admin_doc.get("email") == "admin@studyvault.com"
        if not is_super: return False, "Super Admin access required."
            
    return True, admin_doc

# =====================================================
# SECTION: Main Application Logic
# Purpose: Core workflow for automated monitoring (Workload Awareness)
# =====================================================

async def run_workload_checks():
    # Automated system to monitor faculty response times
    # Escalates notifications if reviews are pending for more than 48 hours
    try:
        now = datetime.now(timezone.utc)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        active_faculty = list(users_collection.find({"role": "faculty", "is_active": True, "is_deleted": {"$ne": True}}))
        
        for f in active_faculty:
            f_subjects = f.get("subjects", [])
            oldest_note = notes_collection.find_one({"status": "pending", "subject": {"$in": f_subjects}}, sort=[("assigned_at", 1)])
            
            if oldest_note:
                start_time = oldest_note.get("assigned_at") or oldest_note.get("uploaded_at")
                if start_time and isinstance(start_time, datetime):
                    if start_time.tzinfo is None:
                        start_time = start_time.replace(tzinfo=timezone.utc)
                    hours_diff = (now - start_time).total_seconds() / 3600
                    if 24 < hours_diff <= 48:
                        create_notification(str(f["_id"]), "WORKLOAD", "⚡ Workload Reminder", "You have pending reviews.")
                    elif hours_diff > 48:
                        create_notification(str(f["_id"]), "URGENT", "🚨 Urgent Escalation", "Reviews are heavily delayed.")
    except Exception as e:
        print(f"Error in workload checks: {e}")

# =====================================================
# SECTION: API Routes (Admin Features)
# Purpose: HTTP endpoints for system governance and moderation
# =====================================================

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    # Central command center with real-time analytics and faculty performance metrics
    user = get_current_admin(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    await run_workload_checks()
    
    # Calculate global platform stats
    now = datetime.now(timezone.utc)
    last_7_days = [(now - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    
    # 1. User Stats
    total_users = users_collection.count_documents({"is_deleted": {"$ne": True}})
    total_students = users_collection.count_documents({"role": "student", "is_deleted": {"$ne": True}})
    total_faculty = users_collection.count_documents({"role": "faculty", "is_deleted": {"$ne": True}})
    
    # 2. Note Stats
    total_notes = notes_collection.count_documents({})
    pending_notes = notes_collection.count_documents({"status": "pending"})
    approved_notes = notes_collection.count_documents({"status": "approved"})
    rejected_notes = notes_collection.count_documents({"status": "rejected"})
    admin_review_notes = notes_collection.count_documents({"status": "admin_review"})
    
    # 3. Report Stats
    open_reports = reports_collection.count_documents({"status": "open"})
    
    # 4. Chart Data (Notes)
    notes_chart_data = []
    for day_str in last_7_days:
        day_date = datetime.strptime(day_str, '%Y-%m-%d')
        next_day = day_date + timedelta(days=1)
        # Check both created_at and uploaded_at for robustness
        count = notes_collection.count_documents({
            "$or": [
                {"uploaded_at": {"$gte": day_date, "$lt": next_day}},
                {"created_at": {"$gte": day_date, "$lt": next_day}}
            ]
        })
        notes_chart_data.append(count)
    
    # 5. Chart Data (Reports)
    reports_chart_data = []
    for day_str in last_7_days:
        day_date = datetime.strptime(day_str, '%Y-%m-%d')
        next_day = day_date + timedelta(days=1)
        count = reports_collection.count_documents({
            "created_at": {"$gte": day_date, "$lt": next_day}
        })
        reports_chart_data.append(count)

    day_labels = [(now - timedelta(days=i)).strftime('%a') for i in range(6, -1, -1)]

    # 6. Faculty Analytics
    faculty_list = list(users_collection.find({"role": "faculty", "is_deleted": {"$ne": True}}))
    faculty_analytics = []
    for f in faculty_list:
        # Real-time experience calculation - Improved for granularity
        join_date = f.get("created_at") or now
        # Fallback for mock/test data that might have string dates or be missing
        if isinstance(join_date, str):
            try: join_date = datetime.fromisoformat(join_date)
            except: join_date = now
            
        if isinstance(join_date, datetime) and join_date.tzinfo is None:
            join_date = join_date.replace(tzinfo=timezone.utc)

        # 1. Registered real-world experience
        reg_exp = f.get("years_of_experience")
        try:
            reg_exp = int(reg_exp) if reg_exp is not None else 0
        except:
            reg_exp = 0

        # 2. Platform seniority (Account age)
        days_since_join = (now - join_date).days
        years_on_platform = days_since_join // 365
        
        # 3. Combined Total Experience
        total_exp_years = reg_exp + years_on_platform
        
        if total_exp_years > 0:
            experience_label = f"{total_exp_years}y"
        elif days_since_join >= 30:
            experience_label = f"{days_since_join // 30}m"
        else:
            experience_label = f"{max(0, days_since_join)}d"

        # Calculate Average Review Time from real data
        reviewed_notes = list(notes_collection.find({
            "reviewed_by": str(f["_id"]),
            "reviewed_at": {"$exists": True},
            "uploaded_at": {"$exists": True}
        }))
        
        avg_time = None
        fastest = None
        slowest = None
        if reviewed_notes:
            times: list[float] = []
            for n in reviewed_notes:
                try:
                    r_at = n["reviewed_at"]
                    u_at = n["uploaded_at"]
                    if isinstance(r_at, str): r_at = datetime.fromisoformat(r_at)
                    if isinstance(u_at, str): u_at = datetime.fromisoformat(u_at)
                    delta = (r_at - u_at).total_seconds()
                    if delta > 0: times.append(delta)
                except: pass
            if times:
                avg_time = sum(times) / len(times)
                fastest = min(times)
                slowest = max(times)
        
        faculty_analytics.append({
            "name": f.get("name", "Unknown"),
            "experience_label": experience_label,
            "actions": len(reviewed_notes) or notes_collection.count_documents({"reviewed_by": str(f["_id"])}),
            "monthly_reviews": notes_collection.count_documents({
                "reviewed_by": str(f["_id"]),
                "reviewed_at": {"$gte": now.replace(day=1, hour=0, minute=0, second=0)}
            }),
            "pending": notes_collection.count_documents({"status": "pending", "subject": {"$in": f.get("subjects", [])}}),
            "avg_time_sec": avg_time,
            "fastest_sec": fastest,
            "slowest_sec": slowest,
            "status": "Active" if f.get("is_active", True) else "Inactive"
        })

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request, 
        "user": user,
        "total_users": total_users,
        "total_students": total_students,
        "total_faculty": total_faculty,
        "total_notes": total_notes,
        "pending_notes": pending_notes,
        "approved_notes": approved_notes,
        "rejected_notes": rejected_notes,
        "admin_review_notes": admin_review_notes,
        "open_reports": open_reports,
        "recent_notes": list(notes_collection.find().sort("uploaded_at", -1).limit(5)),
        "recent_reports": list(reports_collection.find().sort("created_at", -1).limit(5)),
        "recent_announcements": list(announcements_collection.find().sort("created_at", -1).limit(5)),
        "notes_chart_labels": day_labels,
        "notes_chart_data": notes_chart_data,
        "reports_chart_labels": day_labels,
        "reports_chart_data": reports_chart_data,
        "faculty_analytics": faculty_analytics
    })

@router.get("/users", response_class=HTMLResponse)
async def manage_users(request: Request, role: Optional[str] = None):
    # User management directory with status toggles and role filtering
    user = get_current_admin(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    
    query = {"role": role} if role and role != "all" else {}
    all_users = list(users_collection.find(query, {"password": 0}).sort("created_at", -1))
    
    # Calculate faculty workloads for the UI
    for u in all_users:
        if u.get("role") == "faculty":
            u["pending_count"] = notes_collection.count_documents({
                "status": "pending", 
                "subject": {"$in": u.get("subjects", [])}
            })
            
    deleted_users_count = users_collection.count_documents({"is_deleted": True})
            
    return templates.TemplateResponse("admin/users.html", {
        "request": request, 
        "user": user, 
        "all_users": all_users, 
        "selected_role": role or "all",
        "deleted_users_count": deleted_users_count
    })

@router.post("/users/toggle-status")
async def toggle_user_status(request: Request, user_id: str = Form(...), action_preference: Optional[str] = Form(None)):
    # Deactivates or Reactivates a user account immediately
    admin = get_current_admin(request)
    if not admin: return RedirectResponse(url="/login", status_code=303)
    
    target = users_collection.find_one({"_id": safe_id(user_id)})
    if target:
        if target.get("role") == "admin":
            return RedirectResponse(url="/admin/users?error=Cannot+modify+admin+status", status_code=303)
            
        new_status = not target.get("is_active", True)
        
        # Handle special faculty deactivation logic (Rule 3)
        if not new_status and target.get("role") == "faculty":
            if action_preference == "reassign":
                # Logic to clear assigned subjects or notify system to reassign
                pass
            elif action_preference == "notify":
                # Logic to send urgent reminder
                create_notification(user_id, "SYSTEM_URGENT", "Urgent: Complete Reviews", "Your account is being deactivated. Please complete pending reviews immediately.")

        users_collection.update_one({"_id": safe_id(user_id)}, {"$set": {"is_active": new_status}})
        
    return RedirectResponse(url="/admin/users", status_code=303)

@router.post("/users/delete")
async def soft_delete_user(request: Request, user_id: str = Form(...)):
    # Marks a user as deleted (soft delete) for archive purposes
    admin = get_current_admin(request)
    if not admin: return RedirectResponse(url="/login", status_code=303)
    
    target_user = users_collection.find_one({"_id": safe_id(user_id)})
    if target_user:
        if target_user.get("role") == "admin":
            return RedirectResponse(url="/admin/users?error=Admin+accounts+cannot+be+deleted", status_code=303)
                
        users_collection.update_one({"_id": safe_id(user_id)}, {"$set": {"is_deleted": True, "is_active": False}})
    return RedirectResponse(url="/admin/users", status_code=303)

@router.post("/users/cleanup")
async def permanent_cleanup_users(request: Request):
    # Hard deletes all users marked as deleted in the database
    admin = get_current_admin(request)
    if not admin: return RedirectResponse(url="/login", status_code=303)
    
    users_collection.delete_many({"is_deleted": True})
    return RedirectResponse(url="/admin/users?success=Database+cleaned", status_code=303)

@router.get("/notes", response_class=HTMLResponse)
async def manage_notes(request: Request, subject: Optional[str] = None, status: Optional[str] = None, role: Optional[str] = None, q: Optional[str] = None):
    # Global note moderation panel for administrative overrides
    user = get_current_admin(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    
    query: dict[str, Any] = {}
    if subject and subject != "all": query["subject"] = subject
    if status and status != "all": query["status"] = {"$regex": f"^{status}$", "$options": "i"}
    if role and role != "all": query["uploader_role"] = role
    if q: query["$or"] = [
        {"title": {"$regex": q, "$options": "i"}},
        {"uploader_name": {"$regex": q, "$options": "i"}}
    ]
    
    # Sort by created_at or uploaded_at (most recent first)
    notes = list(notes_collection.find(query).sort([("created_at", -1), ("uploaded_at", -1)]))
    
    # Enrichment for template (ensure uploader details exist)
    for note in notes:
        # Check if basic info is missing or null and fetch from user collection
        if not note.get("uploader_name") or not note.get("uploader_role"):
            uploader = users_collection.find_one({"_id": safe_id(note.get("uploader_id"))})
            if uploader:
                note["uploader_name"] = uploader.get("name", "Unknown User")
                note["uploader_role"] = uploader.get("role", "student")
                # Backfill to DB for future performance
                notes_collection.update_one(
                    {"_id": note["_id"]}, 
                    {"$set": {
                        "uploader_name": note["uploader_name"],
                        "uploader_role": note["uploader_role"]
                    }}
                )
            else:
                # If user doesn't exist, provide fallback but don't overwrite with None
                note["uploader_name"] = note.get("uploader_name") or "Deleted User"
                note["uploader_role"] = note.get("uploader_role") or "student"

    subjects = notes_collection.distinct("subject")
    
    return templates.TemplateResponse("admin/notes.html", {
        "request": request, 
        "user": user, 
        "all_notes": notes,
        "subjects": sorted(subjects),
        "selected_subject": subject or "all",
        "selected_status": status or "all",
        "selected_role": role or "all",
        "search_query": q
    })

@router.post("/notes/approve")
async def approve_note(request: Request, note_id: str = Form(...)):
    # Officially marks a note as approved and notifies the user
    admin = get_current_admin(request)
    if not admin: return RedirectResponse(url="/login", status_code=303)
    
    note = notes_collection.find_one({"_id": safe_id(note_id)})
    if note:
        notes_collection.update_one({"_id": safe_id(note_id)}, {"$set": {
            "status": "approved",
            "approved_at": datetime.now(timezone.utc),
            "reviewed_by": admin["id"]
        }})
        create_notification(note["uploader_id"], "SUCCESS", "Note Approved", f"Your note '{note['title']}' has been approved and is now public.")
    return RedirectResponse(url="/admin/notes", status_code=303)

@router.post("/notes/reject")
async def reject_note(request: Request, note_id: str = Form(...), reason: str = Form(...)):
    # Rejects a note and provides uploader with specific feedback
    admin = get_current_admin(request)
    if not admin: return RedirectResponse(url="/login", status_code=303)
    
    note = notes_collection.find_one({"_id": safe_id(note_id)})
    if note:
        notes_collection.update_one({"_id": safe_id(note_id)}, {"$set": {
            "status": "rejected",
            "rejection_reason": reason,
            "reviewed_by": admin["id"]
        }})
        create_notification(note["uploader_id"], "DANGER", "Note Rejected", f"Your note '{note['title']}' was rejected. Reason: {reason}")
    return RedirectResponse(url="/admin/notes", status_code=303)

@router.post("/notes/return")
async def return_note(request: Request, note_id: str = Form(...), reason: str = Form(...)):
    # Returns note to 'Admin Review' status with feedback for uploader
    admin = get_current_admin(request)
    if not admin: return RedirectResponse(url="/login", status_code=303)
    
    note = notes_collection.find_one({"_id": safe_id(note_id)})
    if note:
        notes_collection.update_one({"_id": safe_id(note_id)}, {"$set": {
            "status": "admin_review",
            "admin_review_reason": reason,
            "returned_at": datetime.now(timezone.utc)
        }})
        create_notification(note["uploader_id"], "WARNING", "Action Required", f"Revisions requested for '{note['title']}': {reason}")
    return RedirectResponse(url="/admin/notes", status_code=303)

@router.post("/notes/warn")
async def warn_on_note(request: Request, note_id: str = Form(...), warning_msg: str = Form(...)):
    # Issues a formal warning while keeping the note active or under review
    admin = get_current_admin(request)
    if not admin: return RedirectResponse(url="/login", status_code=303)
    
    note = notes_collection.find_one({"_id": safe_id(note_id)})
    if note:
        notes_collection.update_one({"_id": safe_id(note_id)}, {"$set": {
            "admin_warning": warning_msg,
            "warning_issued": True
        }})
        create_notification(note["uploader_id"], "WARNING", "System Warning", f"Policy warning for note '{note['title']}': {warning_msg}")
    return RedirectResponse(url="/admin/notes", status_code=303)

@router.post("/notes/delete")
async def delete_note(request: Request, note_id: str = Form(...)):
    # Permanently removes a note from the platform and notifies the uploader
    admin = get_current_admin(request)
    note = notes_collection.find_one({"_id": safe_id(note_id)})
    if note:
        notes_collection.delete_one({"_id": safe_id(note_id)})
        create_notification(note["uploader_id"], "SYSTEM", "Note Deleted", f"Your note '{note['title']}' was removed by admin.")
    return RedirectResponse(url="/admin/notes", status_code=303)

@router.get("/reports", response_class=HTMLResponse)
async def manage_reports(request: Request, status: str = "open", reason: str = "all"):
    # Moderation queue for processing content reports submitted by faculty/students
    user = get_current_admin(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    
    # Base query for status based on categorical selection
    query: dict[str, Any] = {}
    open_statuses = ["Open", "open", "Under Review", "Pending"]
    resolved_statuses = ["Resolved", "resolved", "Closed", "Warning Issued", "No Action Taken"]

    if status == "open":
        query["status"] = {"$in": open_statuses}
    elif status == "resolved":
        query["status"] = {"$in": resolved_statuses}
    elif status != "all":
        query["status"] = {"$regex": f"^{status}$", "$options": "i"}
    
    # Optional filtering by reason
    if reason != "all":
        query["reason"] = reason

    # Fetch reports
    reports = list(reports_collection.find(query).sort("created_at", -1))
    
    # Get all reports to gather uploader/title info if missing (joining logic)
    for r in reports:
        if "item_title" not in r and r.get("reported_item_id"):
            try:
                # Assuming item_type 'note' for now, can be expanded
                note = notes_collection.find_one({"_id": safe_id(r["reported_item_id"])})
                if note:
                    r["item_title"] = note.get("title", "Unknown Item")
                    # Also get reporter name if not stored
                    reporter = users_collection.find_one({"_id": safe_id(r["reporter_id"])})
                    if reporter:
                        r["reporter_name"] = reporter.get("name", "Unknown User")
            except:
                r["item_title"] = "Item Not Found"
                r["reporter_name"] = "Unknown"

    # Statistics for the dashboard (consistent with filtering logic)
    total_stats = {
        "total": reports_collection.count_documents({}),
        "open": reports_collection.count_documents({"status": {"$in": open_statuses}}),
        "resolved": reports_collection.count_documents({"status": {"$in": resolved_statuses}})
    }

    # Unique reasons for the filter dropdown
    reasons = reports_collection.distinct("reason")

    return templates.TemplateResponse("admin/reports.html", {
        "request": request, 
        "user": user, 
        "all_reports": reports, 
        "selected_status": status,
        "selected_reason": reason,
        "reasons": sorted(reasons),
        "total_stats": total_stats
    })

@router.post("/reports/resolve")
async def resolve_report(
    request: Request,
    report_id: str = Form(...),
    action: str = Form(...)
):
    # Handles administrative decisions on moderation reports
    admin = get_current_admin(request)
    if not admin: return RedirectResponse(url="/login", status_code=303)

    report = reports_collection.find_one({"_id": safe_id(report_id)})
    if not report: return RedirectResponse(url="/admin/reports?error=Report+not+found", status_code=303)

    # Prevent duplicate actions: if already resolved, skip
    if report.get("resolved_at"):
        return RedirectResponse(url="/admin/reports?error=Report+already+resolved", status_code=303)

    note_id = report.get("reported_item_id")
    note = notes_collection.find_one({"_id": safe_id(note_id)}) if note_id else None
    content_name = report.get("item_title") or (note.get("title") if note else "Unknown Content")

    # Map action → human-readable label and report status
    action_label_map = {
        "delete_content": ("Content Blocked", "ACTION_TAKEN"),
        "warning":        ("Warning Issued",  "ACTION_TAKEN"),
        "no_action":      ("No Action Taken", "REJECTED"),
    }
    admin_action_label, new_report_status = action_label_map.get(action, (action.replace("_", " ").title(), "ACTION_TAKEN"))

    # Apply content-level consequence
    if action == "delete_content" and note:
        notes_collection.update_one({"_id": safe_id(note_id)}, {"$set": {"status": "Blocked"}})
        create_notification(note["uploader_id"], "SYSTEM_ALERT", "Content Blocked",
                            f"Your note '{content_name}' was blocked due to a policy violation.")

    elif action == "warning" and note:
        create_notification(note["uploader_id"], "WARNING", "Content Warning",
                            f"A report was filed against your note '{content_name}'. Please ensure it follows all platform guidelines.")

    elif action == "no_action" and note:
        # Notify the uploader that the report against their content was dismissed
        create_notification(note["uploader_id"], "SYSTEM", "Report Dismissed",
                            f"A report against your note '{content_name}' was reviewed and no action was taken.")

    # Update report with action details
    reports_collection.update_one(
        {"_id": safe_id(report_id)},
        {"$set": {
            "status": new_report_status,
            "admin_action": admin_action_label,
            "resolution": action,
            "resolved_by": admin["id"],
            "resolved_at": datetime.now(timezone.utc)
        }}
    )

    # Notify the faculty reporter (once, guarded by resolved_at above)
    reporter_id = report.get("reporter_id")
    if reporter_id and reporter_id != "system":
        create_notification(
            str(reporter_id),
            "ADMIN_ACTION",
            "Admin Reviewed Your Report",
            f"Admin reviewed your report on '{content_name}'. Action: {admin_action_label}"
        )

    return RedirectResponse(url="/admin/reports?success=Report+processed", status_code=303)

@router.get("/announcements", response_class=HTMLResponse)
async def announcements_page(request: Request):
    # Administrative portal for broadcasting platform-wide updates
    user = get_current_admin(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    
    announcements = list(announcements_collection.find().sort("created_at", -1))
    return templates.TemplateResponse("admin/announcements.html", {"request": request, "user": user, "announcements": announcements})

@router.post("/announcements/create")
async def create_announcement(request: Request, title: str = Form(...), content: str = Form(...), audience: str = Form("all")):
    # Creates platform-wide announcements from the administration
    admin = get_current_admin(request)
    if not admin: return RedirectResponse(url="/login", status_code=303)
    announcements_collection.insert_one({
        "title": title, "content": content, "message": content, "audience": audience, 
        "author_id": admin["id"], "author_name": admin["name"], "author_role": "admin", 
        "created_at": datetime.now(timezone.utc)
    })
    # Notify all users matching the selected audience
    try:
        role_query: dict = {"is_deleted": {"$ne": True}}
        if audience == "student":
            role_query["role"] = "student"
        elif audience == "faculty":
            role_query["role"] = "faculty"
        # audience == "all" notifies both students and faculty
        recipients = list(users_collection.find(role_query))
        for r in recipients:
            if r.get("role") in ("student", "faculty"):
                create_notification(
                    str(r["_id"]), "ANNOUNCEMENT",
                    f"📢 Announcement: {title}",
                    content[:200] if len(content) > 200 else content
                )
    except Exception as e:
        print(f"[Announcements] Failed to notify users: {e}")
    return RedirectResponse(url="/admin/announcements", status_code=303)

@router.post("/announcements/delete")
async def delete_announcement(request: Request, announcement_id: str = Form(...)):
    # Removes a specific announcement from the database
    admin = get_current_admin(request)
    if not admin: return RedirectResponse(url="/login", status_code=303)
    
    try:
        announcements_collection.delete_one({"_id": safe_id(announcement_id)})
        return RedirectResponse(url="/admin/announcements?success=Announcement+deleted", status_code=303)
    except Exception as e:
        print(f"Error deleting announcement: {e}")
        return RedirectResponse(url=f"/admin/announcements?error=Deletion+failed", status_code=303)

@router.get("/messages", response_class=HTMLResponse)
async def messages_page(request: Request):
    # Global communications hub for administrative messaging
    user = get_current_admin(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    
    students = list(users_collection.find({"role": "student", "is_deleted": {"$ne": True}}))
    faculty = list(users_collection.find({"role": "faculty", "is_deleted": {"$ne": True}}))
    
    # Fetch messages sent by admin
    sent_messages = list(messages_collection.find({"sender_id": user["id"]}).sort("created_at", -1))
    
    return templates.TemplateResponse("admin/messages.html", {
        "request": request, 
        "user": user, 
        "students": students,
        "faculty": faculty,
        "sent_messages": sent_messages
    })

@router.post("/messages/send")
async def send_admin_message(
    request: Request, 
    message_type: str = Form(...), 
    subject: str = Form(...), 
    message: str = Form(...),
    receiver_id: Optional[str] = Form(None)
):
    # Dispatcher for individual or platform-wide administrative messages
    admin = get_current_admin(request)
    if not admin: return RedirectResponse(url="/login", status_code=303)
    
    recipients = []
    if message_type == "individual" and receiver_id:
        recipients = [receiver_id]
    elif message_type == "all_students":
        recipients = [str(u["_id"]) for u in users_collection.find({"role": "student", "is_deleted": {"$ne": True}})]
    elif message_type == "all_faculty":
        recipients = [str(u["_id"]) for u in users_collection.find({"role": "faculty", "is_deleted": {"$ne": True}})]
        
    for r_id in recipients:
        target_user = users_collection.find_one({"_id": safe_id(r_id)})
        if target_user:
            messages_collection.insert_one({
                "sender_id": admin["id"],
                "sender_name": admin["name"],
                "receiver_id": r_id,
                "receiver_name": target_user.get("name", "User"),
                "subject": subject,
                "message": message,
                "is_read": False,
                "created_at": datetime.now(timezone.utc)
            })
            create_notification(r_id, "MESSAGE", f"New Message: {subject}", f"You have a new message from Administrator.")
            
    return RedirectResponse(url="/admin/messages?success=Messages+sent", status_code=303)

@router.get("/settings", response_class=HTMLResponse)
async def system_settings(request: Request):
    # Configuration panel for platform-wide logic like registration and AI toggles
    user = get_current_admin(request)
    settings = system_settings_collection.find_one({}) or {}
    return templates.TemplateResponse("admin/settings.html", {"request": request, "user": user, "settings": settings})

@router.post("/settings/update")
async def update_settings(
    request: Request,
    registrations_enabled: bool = Form(False),
    ai_enabled: bool = Form(False),
    max_upload_size: int = Form(...),
    allowed_file_types: str = Form(...)
):
    # Persists global platform parameters to the database
    admin = get_current_admin(request)
    if not admin: return RedirectResponse(url="/login", status_code=303)
    
    system_settings_collection.update_one(
        {}, 
        {"$set": {
            "registrations_enabled": registrations_enabled,
            "ai_enabled": ai_enabled,
            "max_upload_size": max_upload_size,
            "allowed_file_types": allowed_file_types,
            "updated_at": datetime.now(timezone.utc)
        }},
        upsert=True
    )
    return RedirectResponse(url="/admin/settings?success=Settings+updated+successfully", status_code=303)

@router.post("/danger/archive-all-notes")
async def danger_archive_notes(request: Request, admin_password: str = Form(...), confirm_text: str = Form(...)):
    # Danger Zone: Mass-archives all platform content for systemic cleanup
    success, result = await verify_danger_access(request, admin_password, confirm_text, "ARCHIVE")
    if success:
        notes_collection.update_many({"status": {"$ne": "archived"}}, {"$set": {"status": "archived", "archived_at": datetime.now(timezone.utc)}})
    else:
        return RedirectResponse(url=f"/admin/settings?error={urllib.parse.quote(result)}", status_code=303)
    return RedirectResponse(url="/admin/settings?success=Mass+archiving+complete", status_code=303)

@router.post("/danger/restore-all-notes")
async def danger_restore_notes(request: Request, admin_password: str = Form(...), confirm_text: str = Form(...)):
    # Reverts mass-archiving by bringing notes back to public/pending status
    success, result = await verify_danger_access(request, admin_password, confirm_text, "RESTORE")
    if success:
        notes_collection.update_many({"status": "archived"}, {"$set": {"status": "approved", "restored_at": datetime.now(timezone.utc)}})
    else:
        return RedirectResponse(url=f"/admin/settings?error={urllib.parse.quote(result)}", status_code=303)
    return RedirectResponse(url="/admin/settings?success=Mass+restoration+complete", status_code=303)

@router.post("/danger/delete-archived-notes")
async def danger_delete_archived(request: Request, admin_password: str = Form(...), confirm_text: str = Form(...)):
    # Permanently liquidates archived content (Super Admin Only)
    success, result = await verify_danger_access(request, admin_password, confirm_text, "DELETE", super_admin_required=True)
    if success:
        notes_collection.delete_many({"status": "archived"})
    else:
        return RedirectResponse(url=f"/admin/settings?error={urllib.parse.quote(result)}", status_code=303)
    return RedirectResponse(url="/admin/settings?success=Archives+permanently+deleted", status_code=303)

@router.post("/danger/reset-reports")
async def danger_reset_reports(request: Request, admin_password: str = Form(...), confirm_text: str = Form(...)):
    # Clears all platform moderation history logs
    success, result = await verify_danger_access(request, admin_password, confirm_text, "RESET")
    if success:
        reports_collection.delete_many({})
    else:
        return RedirectResponse(url=f"/admin/settings?error={urllib.parse.quote(result)}", status_code=303)
    return RedirectResponse(url="/admin/settings?success=Report+history+cleared", status_code=303)

@router.post("/danger/clear-audit-logs")
async def danger_clear_logs(request: Request, admin_password: str = Form(...), confirm_text: str = Form(...)):
    # Wipes all notification/audit trails (Super Admin Only)
    success, result = await verify_danger_access(request, admin_password, confirm_text, "CLEAR", super_admin_required=True)
    if success:
        notifications_collection.delete_many({})
    else:
        return RedirectResponse(url=f"/admin/settings?error={urllib.parse.quote(result)}", status_code=303)
    return RedirectResponse(url="/admin/settings?success=System+audit+logs+purged", status_code=303)

from fastapi.responses import JSONResponse

# =====================================================
# SECTION: Admin Notification Routes
# Purpose: Mark-read and clear-all for admin's own notifications
# =====================================================

@router.get("/notifications", response_class=HTMLResponse)
async def admin_notifications_page(request: Request):
    # Renders the admin notification inbox
    user = get_current_admin(request)
    if not user: return RedirectResponse(url="/login", status_code=303)

    user_id = user["id"]
    notifications = list(notifications_collection.find({"user_id": user_id}).sort("created_at", -1))
    unread_count = notifications_collection.count_documents({"user_id": user_id, "is_read": False})
    return templates.TemplateResponse("admin/notifications.html", {
        "request": request, "user": user,
        "notifications": notifications, "unread_count": unread_count
    })

@router.post("/notifications/mark-read/{notif_id}")
async def admin_mark_notification_read(request: Request, notif_id: str):
    # Marks a specific admin notification as read
    admin = get_current_admin(request)
    if not admin: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    try:
        notifications_collection.update_one(
            {"_id": safe_id(notif_id), "user_id": admin["id"]},
            {"$set": {"is_read": True}}
        )
    except Exception:
        pass
    return JSONResponse({"status": "Success"})

@router.post("/notifications/mark-all-read")
async def admin_mark_all_read(request: Request):
    # Marks all admin notifications as read
    admin = get_current_admin(request)
    if not admin: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    result = notifications_collection.update_many(
        {"user_id": admin["id"], "is_read": False},
        {"$set": {"is_read": True}}
    )
    # The database saves the transaction automatically, returning success format as specified
    print(f"[Notifications] Admin mark-all-read: {result.modified_count} updated for {admin['email']}")
    return JSONResponse({"message": "All notifications marked as read", "status": "Success", "updated": result.modified_count})

@router.delete("/notifications/clear-all")
async def admin_clear_all_notifications(request: Request):
    # Permanently deletes all of this admin's own notifications
    admin = get_current_admin(request)
    if not admin: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    result = notifications_collection.delete_many({"user_id": admin["id"]})
    print(f"[Notifications] Admin clear-all: {result.deleted_count} deleted for {admin['email']}")
    return JSONResponse({"status": "Success", "deleted": result.deleted_count})

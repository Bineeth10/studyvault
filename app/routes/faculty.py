# =====================================================
# SECTION: Imports
# Purpose: Import all required libraries and modules
# =====================================================
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone
from bson import ObjectId
import os
import shutil
from typing import List, Optional

from app.database import (
    notes_collection, 
    notifications_collection,
    messages_collection,
    users_collection,
    announcements_collection,
    forum_posts_collection,
    system_settings_collection,
    create_notification
)
from app.templates import templates

# =====================================================
# SECTION: Configuration
# Purpose: Initialize the router and storage settings
# =====================================================
router = APIRouter(prefix="/faculty")

# Local storage for uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# =====================================================
# SECTION: Authentication Logic
# Purpose: Handles faculty-specific session validation
# =====================================================

def get_current_faculty(request: Request):
    # Dependency to ensure the user is logged in as a faculty member
    # Fetches full user data from DB to ensure subject assignments are up-to-date
    user = request.session.get("user")
    if not user or user.get("role") != "faculty":
        return None
    
    full_user = users_collection.find_one({"_id": ObjectId(user["id"])})
    if full_user:
        user = user.copy()
        user.update(full_user)
        user["id"] = str(full_user["_id"])
        if "_id" in user:
            user["_id"] = str(user["_id"])
    return user

def safe_id(id_val):
    """Safely converts string to ObjectId, or returns original if invalid hex."""
    if not id_val: return None
    if isinstance(id_val, ObjectId): return id_val
    try: return ObjectId(str(id_val))
    except: return str(id_val)

# =====================================================
# SECTION: API Routes (Faculty Features)
# Purpose: HTTP endpoints for note review, management, and communication
# =====================================================

@router.get("/dashboard", response_class=HTMLResponse)
async def faculty_dashboard(request: Request):
    # Provides an analytical overview of reviews, subjects, and recent activity
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    
    # Get subjects this faculty is assigned to
    faculty_subjects = user.get("subjects", [])
    if user.get("primary_subject"): faculty_subjects.append(user.get("primary_subject"))
    if user.get("secondary_subject"): faculty_subjects.append(user.get("secondary_subject"))
    
    # Calculate performance stats and recent activity
    pending_approvals = notes_collection.count_documents({"status": "pending", "subject": {"$in": faculty_subjects}})
    
    # Show both my past reviews AND any new pending notes for my subjects in Recent Activity
    recent_activity_query = {
        "subject": {"$in": faculty_subjects}, 
        "$or": [
            {"status": "pending"}, 
            {"reviewed_by": str(user["id"])}, 
            {"action_by": str(user["id"])}
        ]
    }
    
    # Calculate Average Review Time metrics
    reviewed_notes = list(notes_collection.find({
        "reviewed_by": str(user["id"]),
        "status": {"$in": ["approved", "rejected", "returned"]}
    }))
    
    total_time: float = 0.0
    avg_time: Optional[float] = None
    fastest: Optional[float] = None
    slowest: Optional[float] = None
    monthly_completed = 0
    current_month = datetime.now(timezone.utc).month
    
    if reviewed_notes:
        times: List[float] = []
        for n in reviewed_notes:
            try:
                # Monthly reviews
                r_at_m = n.get("reviewed_at") or n.get("approved_at") or n.get("rejected_at") or n.get("returned_at")
                if r_at_m:
                    if isinstance(r_at_m, str): r_at_m = datetime.fromisoformat(r_at_m)
                    if hasattr(r_at_m, "month") and getattr(r_at_m, "month") == current_month:
                        monthly_completed += 1
            except Exception: pass
            
            try:
                # Get the finish time (approval or rejection time)
                r_at = n.get("reviewed_at") or n.get("approved_at") or n.get("rejected_at") or n.get("returned_at")
                # Get the start time (upload or creation time)
                u_at = n.get("uploaded_at") or n.get("created_at")
                
                if r_at and u_at:
                    if isinstance(r_at, str): r_at = datetime.fromisoformat(r_at)
                    if isinstance(u_at, str): u_at = datetime.fromisoformat(u_at)
                    
                    if isinstance(r_at, datetime) and isinstance(u_at, datetime):
                        delta_val: float = (r_at - u_at).total_seconds()
                        if delta_val > 0: 
                            times.append(delta_val)
            except Exception: pass
        if times:
            total_time = sum(times)
            avg_time = total_time / len(times)
            fastest = min(times)
            slowest = max(times)

    return templates.TemplateResponse("faculty/dashboard.html", {
        "request": request,
        "user": user,
        "stats": {
            "my_uploads": notes_collection.count_documents({"uploader_id": str(user["id"])}),
            "pending_approvals": pending_approvals,
            "total_completed": notes_collection.count_documents({"reviewed_by": str(user["id"]), "status": {"$ne": "pending"}}),
            "monthly_completed": monthly_completed,
            "avg_time_sec": avg_time,
            "total_time_sec": total_time,
            "fastest_sec": fastest,
            "slowest_sec": slowest,
            "subjects_count": len(set(faculty_subjects))
        },
        "recent_notes": list(notes_collection.find(recent_activity_query).sort("uploaded_at", -1).limit(5))
    })

@router.get("/approvals", response_class=HTMLResponse)
async def approvals_page(request: Request, status: str = "pending"):
    # Displays notes filtered by status (Pending/Approved/Rejected) for review
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    
    faculty_subjects = user.get("subjects", [])
    query = {"status": status.lower(), "subject": {"$in": faculty_subjects}}
    notes = list(notes_collection.find(query).sort("uploaded_at", -1))
    
    # Process notes for template compatibility (add id string)
    for note in notes:
        note["id"] = str(note["_id"])
        if note.get("uploaded_at"): note["uploaded_at"] = note["uploaded_at"].strftime('%Y-%m-%d %H:%M')
        if note.get("approved_at"): note["approved_at"] = note["approved_at"].strftime('%Y-%m-%d %H:%M')
        if note.get("rejected_at"): note["rejected_at"] = note["rejected_at"].strftime('%Y-%m-%d %H:%M')

    return templates.TemplateResponse("faculty/approvals.html", {
        "request": request, "user": user, "notes": notes, "current_status": status.upper(),
        "pending_count": notes_collection.count_documents({"status": "pending", "subject": {"$in": faculty_subjects}}),
        "approved_count": notes_collection.count_documents({"status": "approved", "subject": {"$in": faculty_subjects}}),
        "rejected_count": notes_collection.count_documents({"status": "rejected", "subject": {"$in": faculty_subjects}})
    })

@router.get("/api/notes")
async def get_notes_api(request: Request, status: str = "pending"):
    # API endpoint for AJAX tab switching on the approvals page
    user = get_current_faculty(request)
    if not user: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    faculty_subjects = user.get("subjects", [])
    query = {"status": status.lower(), "subject": {"$in": faculty_subjects}}
    notes = list(notes_collection.find(query).sort("uploaded_at", -1))
    
    processed_notes = []
    for note in notes:
        note["id"] = str(note["_id"])
        del note["_id"] # Remove ObjectId for JSON serialization
        if note.get("uploaded_at"): note["uploaded_at"] = note["uploaded_at"].strftime('%Y-%m-%d %H:%M')
        if note.get("approved_at"): note["approved_at"] = note["approved_at"].strftime('%Y-%m-%d %H:%M')
        if note.get("rejected_at"): note["rejected_at"] = note["rejected_at"].strftime('%Y-%m-%d %H:%M')
        processed_notes.append(note)
        
    return {
        "notes": processed_notes,
        "pending_count": notes_collection.count_documents({"status": "pending", "subject": {"$in": faculty_subjects}}),
        "approved_count": notes_collection.count_documents({"status": "approved", "subject": {"$in": faculty_subjects}}),
        "rejected_count": notes_collection.count_documents({"status": "rejected", "subject": {"$in": faculty_subjects}})
    }

@router.post("/approve/{note_id}")
async def approve_note(request: Request, note_id: str):
    # Approves a note, making it visible to students, and sends a notification
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    
    # Simple safe_id for faculty context
    try: oid = ObjectId(note_id)
    except: oid = note_id

    # Atomic update to prevent multiple reviews of the same note
    result = notes_collection.update_one(
        {"_id": oid, "status": "pending"},
        {"$set": {"status": "approved", "reviewed_by": str(user["id"]), "reviewed_by_name": user["name"], "approved_at": datetime.now(timezone.utc)}}
    )
    
    if result.modified_count > 0:
        note = notes_collection.find_one({"_id": oid})
        # Notify the student (uploader) about the approval
        create_notification(
            note["uploader_id"], "APPROVAL",
            "Note Approved",
            f"Your note '{note['title']}' was approved by Prof. {user['name']}."  
        )
        # Notify faculty themselves — appears in their Reviews tab
        create_notification(
            str(user["id"]), "APPROVAL",
            "Note Approved",
            f"You approved '{note['title']}' by {note.get('uploader_name', 'student')}."  
        )
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JSONResponse({"success": True})
    return RedirectResponse(url="/faculty/approvals?success=Note approved", status_code=303)

@router.post("/reject/{note_id}")
async def reject_note(request: Request, note_id: str, reason: str = Form(...)):
    # Rejects a note with a reason provided to the student
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)

    from bson import ObjectId
    try: oid = ObjectId(note_id)
    except: oid = note_id

    result = notes_collection.update_one(
        {"_id": oid, "status": "pending"},
        {"$set": {"status": "rejected", "rejection_reason": reason, "reviewed_by": str(user["id"]), "reviewed_by_name": user["name"], "rejected_at": datetime.now(timezone.utc)}}
    )
    
    if result.modified_count > 0:
        note = notes_collection.find_one({"_id": oid})
        # Notify the student (uploader) about the rejection
        create_notification(
            note["uploader_id"], "REJECTION",
            "Note Rejected",
            f"Your note '{note['title']}' was rejected. Reason: {reason}"
        )
        # Notify faculty themselves with RETURN type - shows in their Returns tab
        create_notification(
            str(user["id"]), "RETURN",
            "You Returned a Note with Feedback",
            f"You returned '{note['title']}' to the student with feedback. Reason: {reason}"
        )
        # Also notify faculty with REJECTION type - shows in their Reviews tab
        create_notification(
            str(user["id"]), "REJECTION",
            "Note Reviewed: Rejected",
            f"You rejected '{note['title']}' by {note.get('uploader_name', 'student')}. Reason: {reason}"
        )
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JSONResponse({"success": True})
    return RedirectResponse(url="/faculty/approvals?success=Note rejected", status_code=303)

@router.post("/return/{note_id}")
async def return_note(request: Request, note_id: str, reason: str = Form(...)):
    # Returns a note to the student with a revision request and sends a RETURN notification
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)

    try: oid = ObjectId(note_id)
    except: oid = note_id

    result = notes_collection.update_one(
        {"_id": oid, "status": "pending"},
        {"$set": {
            "status": "returned",
            "return_reason": reason,
            "reviewed_by": str(user["id"]),
            "reviewed_by_name": user["name"],
            "returned_at": datetime.now(timezone.utc)
        }}
    )

    if result.modified_count > 0:
        note = notes_collection.find_one({"_id": oid})
        create_notification(
            note["uploader_id"], "RETURN",
            "Note Returned for Revision",
            f"Prof. {user['name']} returned your note '{note['title']}' for revision. Reason: {reason}"
        )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JSONResponse({"success": True})
    return RedirectResponse(url="/faculty/approvals?success=Note returned", status_code=303)

@router.get("/preview/{note_id}", response_class=HTMLResponse)
async def preview_note(request: Request, note_id: str):
    # Provides a full-screen preview of the note for thorough review
    user = get_current_faculty(request)
    note = notes_collection.find_one({"_id": ObjectId(note_id)})
    if not note: return HTMLResponse("Note not found", status_code=404)
    
    file_ext = os.path.splitext(note.get('filename', ''))[1].lower() if note.get('filename') else ""
    
    return templates.TemplateResponse("faculty/preview_note.html", {
        "request": request, 
        "user": user, 
        "note": note,
        "file_ext": file_ext
    })

@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    # Renders the faculty note upload form
    user = get_current_faculty(request)
    return templates.TemplateResponse("faculty/upload_notes.html", {"request": request, "user": user})

@router.post("/upload")
async def process_upload(request: Request, title: str = Form(...), subject: str = Form(...), description: str = Form(...), file: UploadFile = File(...)):
    # Handles faculty uploads - notes are auto-approved as they come from faculty
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    notes_collection.insert_one({
        "title": title, "subject": subject, "description": description, "file_path": file_path, 
        "filename": file.filename, "original_filename": file.filename,
        "uploader_id": user["id"], "uploader_name": user["name"], "uploader_role": "faculty", "status": "approved", "uploaded_at": datetime.now(timezone.utc)
    })
    
    # Notify all active students about the new faculty note
    students = list(users_collection.find({"role": "student", "is_deleted": {"$ne": True}}))
    for std in students:
        create_notification(
            str(std["_id"]), "UPLOAD",
            "New Study Material",
            f"Prof. {user['name']} uploaded a new note: '{title}' for {subject}."
        )
    
    return RedirectResponse(url="/faculty/manage-notes", status_code=303)

@router.get("/manage-notes", response_class=HTMLResponse)
async def manage_notes(request: Request, subject: Optional[str] = None):
    # Lists all notes uploaded by this faculty member for editing or removal
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    
    query = {"uploader_id": str(user["id"])}
    if subject and subject != "all": query["subject"] = subject
    
    notes = list(notes_collection.find(query).sort("uploaded_at", -1))
    subjects = notes_collection.distinct("subject", {"uploader_id": str(user["id"])})
    
    return templates.TemplateResponse("faculty/manage_notes.html", {
        "request": request, 
        "user": user, 
        "notes": notes,
        "subjects": subjects,
        "current_subject": subject
    })

@router.get("/edit-note/{note_id}", response_class=HTMLResponse)
async def edit_note_page(request: Request, note_id: str):
    # Renders the edit form for a specific note
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    
    note = notes_collection.find_one({"_id": ObjectId(note_id), "uploader_id": str(user["id"])})
    if not note: return RedirectResponse(url="/faculty/manage-notes?error=Note not found", status_code=303)
    
    return templates.TemplateResponse("faculty/edit_note.html", {"request": request, "user": user, "note": note})

@router.post("/edit-note/{note_id}")
async def update_note(request: Request, note_id: str, title: str = Form(...), subject: str = Form(...), description: str = Form(...)):
    # Updates note metadata
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    
    result = notes_collection.update_one(
        {"_id": ObjectId(note_id), "uploader_id": str(user["id"])},
        {"$set": {"title": title, "subject": subject, "description": description, "updated_at": datetime.now(timezone.utc)}}
    )
    
    if result.modified_count > 0:
        return RedirectResponse(url="/faculty/manage-notes?success=Note updated", status_code=303)
    return RedirectResponse(url="/faculty/manage-notes?error=Update failed", status_code=303)

@router.get("/delete-note/{note_id}")
async def delete_note(request: Request, note_id: str):
    # Removes a note (Permanent delete for faculty their own notes)
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    
    notes_collection.delete_one({"_id": ObjectId(note_id), "uploader_id": str(user["id"])})
    return RedirectResponse(url="/faculty/manage-notes?success=Note deleted", status_code=303)

@router.get("/announcements", response_class=HTMLResponse)
async def announcements_page(request: Request):
    # Management page for faculty announcements to students
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    announcements = list(announcements_collection.find({"faculty_id": user["id"]}).sort("created_at", -1))
    return templates.TemplateResponse("faculty/announcements.html", {"request": request, "user": user, "announcements": announcements})

@router.post("/announcements")
async def post_announcement(request: Request, title: str = Form(...), message: str = Form(...), priority: str = Form("general")):
    # Broadcasts a new announcement to all students and sends a notification to each
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    announcements_collection.insert_one({
        "faculty_id": user["id"], "faculty_name": user["name"], "title": title, "message": message, "priority": priority, "audience": "student", "created_at": datetime.now(timezone.utc)
    })
    # Notify all active students about the new announcement
    try:
        students = list(users_collection.find({"role": "student", "is_deleted": {"$ne": True}}))
        for student in students:
            create_notification(
                str(student["_id"]), "ANNOUNCEMENT",
                f"📢 Announcement: {title}",
                message[:200] if len(message) > 200 else message
            )
    except Exception as e:
        print(f"[Announcements] Failed to notify students: {e}")
    return RedirectResponse(url="/faculty/announcements", status_code=303)

@router.get("/messages", response_class=HTMLResponse)
async def messages_page(request: Request):
    # Faculty messaging inbox with grouped conversation threads
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    
    students = list(users_collection.find({"role": "student", "is_deleted": {"$ne": True}}))
    
    # Logic to fetch and group messages into conversations
    all_messages = list(messages_collection.find({
        "$or": [{"sender_id": str(user["id"])}, {"receiver_id": str(user["id"])}]
    }).sort("created_at", -1))
    
    conversations = {}
    for msg in all_messages:
        # Identify the other person (could be student, admin, or faculty)
        other_id = msg["receiver_id"] if msg["sender_id"] == str(user["id"]) else msg["sender_id"]
        
        # We only group by most recent message per user
        if other_id not in conversations:
            other_user = users_collection.find_one({"_id": safe_id(other_id)})
            if other_user:
                conversations[other_id] = {
                    "user": other_user,
                    "last_message": msg
                }
    
    return templates.TemplateResponse("faculty/messages.html", {
        "request": request, 
        "user": user, 
        "students": students, 
        "conversations": conversations
    })

@router.post("/messages")
async def send_faculty_message(
    request: Request, 
    student_id: str = Form(...), 
    subject: str = Form(...), 
    content: str = Form(...)
):
    # Sends messages from faculty to individuals or all students
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    
    recipients = []
    if student_id == "all":
        recipients = [str(s["_id"]) for s in users_collection.find({"role": "student", "is_deleted": {"$ne": True}})]
    else:
        recipients = [student_id]
        
    for r_id in recipients:
        target = users_collection.find_one({"_id": safe_id(r_id)})
        if target:
            messages_collection.insert_one({
                "sender_id": str(user["id"]),
                "sender_name": user["name"],
                "receiver_id": r_id,
                "receiver_name": target.get("name", "Student"),
                "subject": subject,
                "message": content,
                "is_read": False,
                "created_at": datetime.now(timezone.utc)
            })
            create_notification(r_id, "MESSAGE", f"Message from Fac: {subject}", f"Professor {user['name']} sent a new message.")
            
    return RedirectResponse(url="/faculty/messages?success=Message+sent", status_code=303)

@router.get("/chat/{student_id}", response_class=HTMLResponse)
async def chat_page(request: Request, student_id: str):
    # One-to-one chat thread with a specific student
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    student = users_collection.find_one({"_id": ObjectId(student_id)})
    history = list(messages_collection.find({"$or": [{"sender_id": user["id"], "receiver_id": student_id}, {"sender_id": student_id, "receiver_id": user["id"]}]}).sort("created_at", 1))
    return templates.TemplateResponse("faculty/chat.html", {"request": request, "user": user, "other_user": student, "chat_history": history})

@router.get("/forum", response_class=HTMLResponse)
async def forum_page(request: Request):
    # Displays the community forum where faculty can respond to academic queries
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    posts = list(forum_posts_collection.find().sort("created_at", -1))
    return templates.TemplateResponse("faculty/forum.html", {"request": request, "user": user, "posts": posts})

@router.post("/forum/post")
async def create_forum_post(request: Request, title: str = Form(...), subject: str = Form(...), content: str = Form(...)):
    # Creates a new forum discussion thread posted by a faculty member
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    post_data = {
        "title": title,
        "subject": subject,
        "content": content,
        "author_id": str(user["id"]),
        "author_name": user["name"],
        "author_role": "faculty",
        "replies": [],
        "created_at": datetime.now(timezone.utc)
    }
    forum_posts_collection.insert_one(post_data)
    
    # Notify all active students about the new faculty discussion
    students = list(users_collection.find({"role": "student", "is_deleted": {"$ne": True}}))
    for std in students:
        create_notification(
            str(std["_id"]), "FORUM_REPLY",
            "New Faculty Discussion",
            f"Prof. {user['name']} started a new discussion: '{title}'."
        )
    
    return RedirectResponse(url="/faculty/forum", status_code=303)

@router.post("/forum/reply/{post_id}")
async def reply_to_forum_post(request: Request, post_id: str, reply: str = Form(...)):
    # Appends a faculty reply to an existing forum thread
    user = get_current_faculty(request)
    if not user: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    from bson import ObjectId
    try: oid = ObjectId(post_id)
    except: return JSONResponse({"error": "Invalid post ID"}, status_code=400)
    reply_data = {
        "author_id": str(user["id"]),
        "author_name": user["name"],
        "author_role": "faculty",
        "content": reply,
        "created_at": datetime.now(timezone.utc)
    }
    forum_posts_collection.update_one(
        {"_id": oid},
        {"$push": {"replies": reply_data}}
    )
    
    # Notify the original author of the post if it is a student
    post = forum_posts_collection.find_one({"_id": oid})
    if post and post.get("author_role") == "student":
        create_notification(
            post["author_id"], "FORUM_REPLY",
            "Faculty Reply",
            f"Prof. {user['name']} replied to your forum discussion: '{post.get('title')}'."
        )
    
    return JSONResponse({"success": True})


@router.get("/students", response_class=HTMLResponse)
async def students_page(request: Request):
    # Lists all registered students for faculty reference
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)
    students = list(users_collection.find({"role": "student"}))
    return templates.TemplateResponse("faculty/students.html", {"request": request, "user": user, "students": students})


@router.get("/notifications", response_class=HTMLResponse)
async def notifications_page(request: Request, filter: str = "all"):
    # Detailed notification inbox for faculty — supports tab-based type filtering
    user = get_current_faculty(request)
    if not user: return RedirectResponse(url="/login", status_code=303)

    query: dict = {"user_id": str(user["id"])}
    type_map = {
        "reviews":  ["REVIEW", "APPROVAL", "REJECTION"],
        "reports":  ["REPORT", "REPORT_FILED", "REPORT_RESPONSE", "REPORT_ALERT"],
        "messages": ["MESSAGE"],
        "returns":  ["RETURNED_NOTE", "RETURN"],
        "system":   ["SYSTEM", "WORKLOAD", "URGENT", "ADMIN_ACTION", "SYSTEM_ALERT", "ANNOUNCEMENT"],
    }
    if filter == "unread":
        query["is_read"] = False
    elif filter in type_map:
        query["type"] = {"$in": type_map[filter]}
    # filter == "all" leaves query unchanged — returns everything

    notifications = list(notifications_collection.find(query).sort("created_at", -1))
    return templates.TemplateResponse("faculty/notifications.html", {
        "request": request, "user": user,
        "notifications": notifications, "current_filter": filter
    })

@router.post("/notifications/mark-read")
async def mark_notification_read(request: Request, notif_id: str = Form(...)):
    # Marks a specific notification as viewed by the faculty member
    user = get_current_faculty(request)
    if not user: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    notifications_collection.update_one(
        {"_id": ObjectId(notif_id), "user_id": str(user["id"])},
        {"$set": {"is_read": True}}
    )
    return JSONResponse({"status": "Success"})

@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(request: Request):
    # Marks all unread alerts as read for the current faculty member
    user = get_current_faculty(request)
    if not user: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    result = notifications_collection.update_many(
        {"user_id": str(user["id"]), "is_read": False},
        {"$set": {"is_read": True}}
    )
    print(f"[Notifications] Faculty mark-all-read: {result.modified_count} updated for {user['email']}")
    return JSONResponse({"status": "Success", "updated": result.modified_count})

@router.post("/notifications/mark-read/{notif_id}")
async def mark_notification_read_path(request: Request, notif_id: str):
    # Marks a specific notification as read (path-param version used by frontend JS)
    user = get_current_faculty(request)
    if not user: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    try:
        notifications_collection.update_one(
            {"_id": ObjectId(notif_id), "user_id": str(user["id"])},
            {"$set": {"is_read": True}}
        )
    except Exception:
        pass
    return JSONResponse({"status": "Success"})

@router.delete("/notifications/clear-all")
async def clear_all_notifications(request: Request):
    # Permanently deletes all notifications for the current faculty member
    user = get_current_faculty(request)
    if not user: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    result = notifications_collection.delete_many({"user_id": str(user["id"])})
    print(f"[Notifications] Faculty clear-all: {result.deleted_count} deleted for {user['email']}")
    return JSONResponse({"status": "Success", "deleted": result.deleted_count})

# =====================================================
# SECTION: Imports
# Purpose: Import all required libraries and modules
# =====================================================
from fastapi import APIRouter, Request, Form, Response
from typing import Optional, List
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.hash import bcrypt
from datetime import datetime, timedelta, timezone
from bson import ObjectId
import os
import secrets

from app.database import (
    users_collection,
    system_settings_collection,
    subjects_collection,
    password_reset_tokens_collection,
)
from app.templates import templates
from app.services.email_service import send_reset_email

# =====================================================
# SECTION: Configuration
# Purpose: Initialize the router for authentication
# =====================================================
router = APIRouter()

# =====================================================
# SECTION: Authentication Logic
# Purpose: Handles login, registration, and sessions
# =====================================================

@router.get("/roles", response_class=HTMLResponse)
async def roles_page(request: Request):
    # Renders the initial role selection page (Student/Faculty/Admin)
    return templates.TemplateResponse("auth/roles.html", {"request": request})

@router.post("/select-role")
async def select_role(request: Request, role: str = Form(...)):
    # Stores the user's intent to login/register as a specific role in the session
    request.session["selected_role"] = role
    return RedirectResponse(url="/login", status_code=303)

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    # Renders the registration form with role-specific fields and availability checks
    # Admin accounts are NEVER created via the web interface
    role = request.session.get("selected_role", "student")
    if role.lower() == "admin":
        return RedirectResponse(url="/login", status_code=303)

    settings = system_settings_collection.find_one({})
    registrations_enabled = settings.get("registrations_enabled", True) if settings else True
    
    # Load subjects for faculty registration
    subjects = []
    if role == "faculty":
        subjects = list(subjects_collection.find({}, {"_id": 0, "name": 1}).sort("name", 1))
        
    return templates.TemplateResponse("auth/register.html", {
        "request": request,
        "role": role,
        "registrations_enabled": registrations_enabled,
        "available_subjects": subjects
    })

@router.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    subjects: List[str] = Form(None),
    custom_subject: Optional[str] = Form(None),
    years_of_experience: Optional[int] = Form(None)
):
    # Creates a new user account with hashed passwords and role-based metadata
    # Admin accounts cannot be created through the web interface
    if role.lower() == "admin":
        return RedirectResponse(url="/login", status_code=303)

    settings = system_settings_collection.find_one({})
    registrations_enabled = settings.get("registrations_enabled", True) if settings else True
    
    if not registrations_enabled:
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": "Registrations are currently disabled by the administrator.",
            "role": role,
            "registrations_enabled": False
        })
        
    # Prevent duplicate registrations
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": "Email already registered",
            "role": role,
            "registrations_enabled": True
        })
    
    # Securely hash the password using bcrypt
    hashed_password = bcrypt.hash(password)
    
    # Base user object
    user_data = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "role": role,
        "created_at": datetime.now(timezone.utc),
        "profile_complete": False
    }

    if role == "faculty":
        # Additional validation for faculty members
        if not subjects or len(subjects) == 0:
             return templates.TemplateResponse("auth/register.html", {
                "request": request,
                "error": "Please select at least one subject.",
                "role": role,
                "registrations_enabled": True
            })
            
        # Handle custom "Other" subject input
        if "Other" in subjects:
            stripped_custom = custom_subject.strip() if custom_subject else ""
            if not stripped_custom:
                return templates.TemplateResponse("auth/register.html", {
                    "request": request,
                    "error": "Please specify the custom subject.",
                    "role": role,
                    "registrations_enabled": True
                })
            subjects.remove("Other")
            subjects.append(stripped_custom)
            user_data["custom_subject"] = stripped_custom
            
        user_data["subjects"] = subjects
        user_data["years_of_experience"] = years_of_experience
    
    # Persist user to database
    result = users_collection.insert_one(user_data)
    
    # Notify ALL admins about the new user registration
    try:
        from app.database import create_notification
        admins = list(users_collection.find({"role": "admin", "is_deleted": {"$ne": True}}))
        for adm in admins:
            create_notification(str(adm["_id"]), "SYSTEM", "New User Platform Registration", f"New user registered: {name} ({role})")
    except Exception as e:
        print(f"Error notifying admins of registration: {e}")
    
    # Synchronize subjects collection if a new subject was added
    faculty_subjects = user_data.get("subjects")
    if role == "faculty" and isinstance(faculty_subjects, list):
        for subj in faculty_subjects:
            subj_name = subj.strip()
            if subj_name:
                subjects_collection.update_one(
                    {"name": subj_name},
                    {"$set": {"name": subj_name, "updated_at": datetime.now(timezone.utc)},
                     "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
                    upsert=True
                )

    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "success": "Registration successful! Please login.",
        "role": role,
        "registrations_enabled": registrations_enabled
    })

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    # Renders the login form for the currently selected role
    settings = system_settings_collection.find_one({})
    registrations_enabled = settings.get("registrations_enabled", True) if settings else True
    
    role = request.session.get("selected_role", "Student")
    return templates.TemplateResponse("auth/login.html", {
        "request": request, 
        "role": role,
        "registrations_enabled": registrations_enabled
    })

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    # Authenticates user credentials and establishes a secure session
    settings = system_settings_collection.find_one({})
    registrations_enabled = settings.get("registrations_enabled", True) if settings else True

    # Generic error used to prevent credential harvesting
    GENERIC_ERROR = "Invalid email or password."
    selected_role = request.session.get("selected_role", "student")

    def fail():
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": GENERIC_ERROR,
            "role": selected_role,
            "registrations_enabled": registrations_enabled,
        })

    # Look up user by email
    user = users_collection.find_one({"email": email})

    # Constant-time password verification (even if user doesn't exist) to resist timing attacks
    if not user:
        bcrypt.verify(password, "$2b$12$invalidhashxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        return fail()

    if not bcrypt.verify(password, user["password"]):
        return fail()

    # Block access if account is inactive or deleted
    if not user.get("is_active", True) or user.get("is_deleted", False):
        return fail()

    # Security Check: Ensure user is logging in through the portal assigned to their role
    actual_role = user.get("role", "").lower()
    if selected_role.lower() != actual_role:
        return fail()

    # Login successful - Initialize session data
    request.session["user"] = {
        "id": str(user["_id"]),
        "role": user["role"],
        "email": user["email"],
        "name": user["name"],
    }

    # Redirect to the appropriate role-based dashboard
    if user["role"] == "student":
        return RedirectResponse(url="/student/dashboard", status_code=303)
    elif user["role"] == "faculty":
        return RedirectResponse(url="/faculty/dashboard", status_code=303)
    elif user["role"] == "admin":
        return RedirectResponse(url="/admin/dashboard", status_code=303)

    return RedirectResponse(url="/roles", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    # Clears the current session and redirects the user to the landing page
    request.session.clear()
    return RedirectResponse(url="/roles", status_code=303)


# =====================================================
# SECTION: Forgot Password
# Purpose: Generate and validate secure reset tokens
# =====================================================

@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    """Renders the Forgot Password form."""
    return templates.TemplateResponse("auth/forgot_password.html", {"request": request})


@router.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password(
    request: Request,
    email: str = Form(...),
):
    """
    Accepts an email address, generates a secure time-limited reset token,
    stores it, and sends a reset email (falls back to console if SMTP unconfigured).
    Always returns the same neutral message to avoid exposing whether the email exists.
    """
    # Security: always show the same neutral message regardless of outcome
    NEUTRAL_MSG = "If that email is registered, a password reset link has been sent."

    user = users_collection.find_one({"email": email})
    if user:
        # Invalidate any existing un-used tokens for this email
        password_reset_tokens_collection.delete_many({"user_email": email})

        # Generate a cryptographically secure token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        password_reset_tokens_collection.insert_one({
            "user_email": email,
            "token": token,
            "expires_at": expires_at,
            "used": False,
        })

        # Send reset email (falls back to console print if SMTP not configured)
        await send_reset_email(email, token)

    return templates.TemplateResponse(
        "auth/forgot_password.html",
        {"request": request, "success": NEUTRAL_MSG},
    )


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: str = ""):
    """Renders the Reset Password form, pre-validating the token."""
    error = None
    valid = False

    if not token:
        error = "Invalid or missing reset token."
    else:
        record = password_reset_tokens_collection.find_one({"token": token})
        if not record:
            error = "This reset link is invalid or has already been used."
        elif record.get("used"):
            error = "This reset link has already been used. Please request a new one."
        elif record["expires_at"] < datetime.now(timezone.utc):
            error = "This reset link has expired. Please request a new one."
        else:
            valid = True

    return templates.TemplateResponse(
        "auth/reset_password.html",
        {"request": request, "token": token, "error": error, "valid": valid},
    )


@router.post("/reset-password", response_class=HTMLResponse)
async def reset_password(
    request: Request,
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
):
    """Validates the token, ensures passwords match, then updates the user's password."""

    def fail(msg: str):
        return templates.TemplateResponse(
            "auth/reset_password.html",
            {"request": request, "token": token, "error": msg, "valid": True},
        )

    # --- Server-side guard (client validates too) ---
    if new_password != confirm_password:
        return fail("Passwords do not match. Please try again.")

    if len(new_password) < 8:
        return fail("Password must be at least 8 characters long.")

    # --- Validate token ---
    record = password_reset_tokens_collection.find_one({"token": token})
    if not record:
        return templates.TemplateResponse(
            "auth/reset_password.html",
            {"request": request, "token": token,
             "error": "Invalid or already-used reset link.", "valid": False},
        )

    if record.get("used") or record["expires_at"] < datetime.now(timezone.utc):
        return templates.TemplateResponse(
            "auth/reset_password.html",
            {"request": request, "token": token,
             "error": "This reset link has expired or was already used.", "valid": False},
        )

    # --- Update password ---
    hashed = bcrypt.hash(new_password)
    users_collection.update_one(
        {"email": record["user_email"]},
        {"$set": {"password": hashed}},
    )

    # --- Invalidate token (single-use) ---
    password_reset_tokens_collection.update_one(
        {"token": token},
        {"$set": {"used": True}},
    )

    print(f"✅ Password successfully reset for: {record['user_email']}")

    return templates.TemplateResponse(
        "auth/reset_password.html",
        {
            "request": request,
            "token": "",
            "success": "Your password has been reset successfully! You can now log in.",
            "valid": False,
        },
    )

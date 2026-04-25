# =====================================================
# SECTION: Imports
# Purpose: Import all required libraries and modules
# =====================================================
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os
from dotenv import load_dotenv

# =====================================================
# SECTION: Configuration
# Purpose: Load environment variables and app settings
# =====================================================
# Load environment variables
load_dotenv()

from app.routes import student, auth, faculty, admin, reports
from app.templates import templates

# Initialize FastAPI application
app = FastAPI(title="StudyVault")

# =====================================================
# SECTION: Main Application Logic
# Purpose: Core workflow of the module
# =====================================================
# Create required project directories
os.makedirs("app/static/css", exist_ok=True)
os.makedirs("app/static/js", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

class AdminAuthMiddleware(BaseHTTPMiddleware):
    # Middleware to verify admin role before accessing admin routes
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/admin"):
            user = None
            try:
                user = request.session.get("user")
            except:
                pass
            if not user or user.get("role") != "admin":
                return RedirectResponse(url="/login", status_code=303)
        return await call_next(request)

class NotificationMiddleware(BaseHTTPMiddleware):
    # Custom middleware to fetch unread notification counts for every request
    # Ensures the notification bell always shows the correct number
    async def dispatch(self, request: Request, call_next):
        from app.database import notifications_collection
        from bson import ObjectId
        
        # Initialize state
        request.state.unread_count = 0
        request.state.recent_notifications = []
        
        # Safe session access
        user = None
        try:
            user = request.session.get("user")
        except:
            # Session not yet available or failed
            pass
            
        if user and user.get("id"):
            try:
                user_id = user["id"]
                request.state.unread_count = notifications_collection.count_documents({
                    "user_id": user_id, 
                    "is_read": False
                })
                request.state.recent_notifications = list(notifications_collection.find({
                    "user_id": user_id
                }).sort("created_at", -1).limit(10))
            except Exception as e:
                print(f"Error in NotificationMiddleware: {e}")
                
        response = await call_next(request)
        return response

# Store templates in app state for access across the app
app.state.templates = templates

# Middleware Stack (Order: Last added runs first)
# NotificationMiddleware inside, SessionMiddleware outside
app.add_middleware(AdminAuthMiddleware)
app.add_middleware(NotificationMiddleware)

app.add_middleware(
    SessionMiddleware,
    secret_key="studyvault-secret-key"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and file uploads serving
import mimetypes
mimetypes.add_type("application/pdf", ".pdf")
mimetypes.add_type("image/jpeg", ".jpg")
mimetypes.add_type("image/jpeg", ".jpeg")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("text/plain", ".txt")
mimetypes.add_type("text/markdown", ".md")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# =====================================================
# SECTION: API Routes
# Purpose: HTTP endpoints used by the frontend
# =====================================================
# Include modular routers for different user roles
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(faculty.router)
app.include_router(admin.router)
app.include_router(reports.router)

# Root redirect and core pages
@app.get("/student/announcements", response_class=HTMLResponse)
async def announcements_page_main(request: Request):
    # Displays the student announcements page with notification context
    from app.routes.student import get_current_student, get_notif_context
    from app.database import announcements_collection
    
    user = get_current_student(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    all_announcements = list(announcements_collection.find().sort("created_at", -1))
    return templates.TemplateResponse("student/announcements.html", {
        "request": request,
        "user": user,
        "announcements": all_announcements,
        **get_notif_context(user["id"])
    })

@app.get("/test")
async def test():
    # Simple health check endpoint
    return {"status": "ok"}

@app.get("/")
async def root():
    # Redirects root URL to the role selection page
    return RedirectResponse(url="/roles")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # Handles browser favicon requests gracefully
    return Response(status_code=204)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Catches all unhandled exceptions and displays a traceback for debugging
    import traceback
    tb = traceback.format_exc()
    print("GLOBAL EXCEPTION:\n", tb)
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(tb, status_code=500)

from fastapi.exceptions import RequestValidationError
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Handles Pydantic validation errors from API requests
    print("VALIDATION EXCEPTION:\n", exc.errors())
    from fastapi.responses import JSONResponse
    return JSONResponse({"detail": exc.errors()}, status_code=422)

# =====================================================
# SECTION: Main Execution
# Purpose: Run the application server
# =====================================================
if __name__ == "__main__":
    import uvicorn
    # Start the Uvicorn ASGI server with hot reloading enabled
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)



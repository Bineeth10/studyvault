<<<<<<< HEAD
# 🎓 StudyVault — Student Module

> A full-stack, production-ready academic notes sharing platform built with **FastAPI**, **MongoDB**, and **AI-powered safety analysis** using the **Groq API (Llama models)**.

---

## 📑 Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [System Architecture](#system-architecture)
5. [Project Structure](#project-structure)
6. [Setup Instructions](#setup-instructions)
7. [Workflow Overview](#workflow-overview)
8. [AI Features & Safety Analysis](#ai-features--safety-analysis)
9. [Security](#security)
10. [Database Collections](#database-collections)
11. [UI Highlights](#ui-highlights)
12. [Testing Checklist](#testing-checklist)
13. [Conclusion / Project Summary](#conclusion--project-summary)

---

## 🏫 Introduction

**StudyVault** is a collaborative academic platform where students can upload their study notes, browse and download notes shared by peers, interact through a discussion forum, and leverage AI-powered study tools. All uploaded content passes through an **AI-driven safety analysis pipeline** before being sent to faculty for review — ensuring high-quality, appropriate content across the platform.

The system supports three distinct roles: **Student**, **Faculty**, and **Admin**, each with dedicated dashboards, permissions, and workflows.

---

## 📋 Features

### 🔐 Authentication
- ✅ Role-based login (Student / Faculty / Admin)
- ✅ User registration with bcrypt password hashing
- ✅ Session-based authentication with secure cookies
- ✅ Password visibility toggle (eye icon)
- ✅ Role validated from database — prevents cross-role access
- ✅ Secure logout with session clearing

---

### 🎛️ Student Dashboard
- ✅ Statistics overview (total uploads, approved, pending, saved)
- ✅ Recent activity feed
- ✅ Quick action buttons
- ✅ Announcement banners (synced from faculty)

---

### 📤 Upload System
- ✅ Multi-file upload support
- ✅ Drag-and-drop interface
- ✅ File metadata input (title, subject)
- ✅ Automatic status assignment (`pending`) on upload
- ✅ Upload notifications generated automatically
- ✅ AI safety scan triggered automatically on upload

---

### 📝 My Notes
- ✅ View all uploaded notes with status tracking
- ✅ Status badges: `Pending` / `Approved` / `Rejected`
- ✅ Preview links available for approved notes
- ✅ Upload date and reviewer info displayed

---

### 🔍 Browse Notes
- ✅ Studocu-style card layout
- ✅ Search by title or subject keyword
- ✅ Subject-based filtering
- ✅ Inline preview for all file types
- ✅ One-click download
- ✅ Favorite (bookmark) toggle

---

### ❤️ Favorites System
- ✅ Add / remove notes from favorites
- ✅ No duplicate favorites stored
- ✅ Dedicated "Saved Notes" page
- ✅ Real-time UI updates on toggle

---

### 👁️ Note Preview
- ✅ Unified preview template for all file types
- ✅ Embedded PDF viewer
- ✅ Image viewer
- ✅ Plain text file preview
- ✅ Download prompts for Office documents (`.docx`, `.pptx`, `.xlsx`)

---

### 🔔 Notifications
- ✅ Upload confirmation notifications
- ✅ Approval / rejection notifications (with reviewer name)
- ✅ Forum reply notifications
- ✅ Message notifications
- ✅ Read / unread status with visual indicator
- ✅ Mark as read functionality

---

### 💬 Messaging
- ✅ One-to-one private messaging
- ✅ Conversation inbox system
- ✅ Student ↔ Student communication
- ✅ Student ↔ Faculty communication
- ✅ Integrated chat interface
- ✅ Timestamped messages
- ✅ Subject-line visibility

---

### 🗣️ Discussion Forum
- ✅ Create posts (Student & Faculty)
- ✅ Reply to forum posts
- ✅ Faculty distinction (role badges and color coding)
- ✅ Subject categorization
- ✅ Upvote system
- ✅ Reply notifications

---

### 📢 Announcements
- ✅ Faculty-wide announcements visible on student dashboards
- ✅ Real-time dashboard banners
- ✅ Announcement history page
- ✅ Automatic synchronization across roles

---

### 🤖 AI Assistant (Groq-powered)
- ✅ Generate note summaries (Groq API — `llama-3.1-8b-instant`)
- ✅ Create flashcards from uploaded notes
- ✅ Ask questions about note content
- ✅ Study guide generator (Groq API — `llama-3.3-70b-versatile` for Q&A)
- ✅ Demo mode fallback (works without API key)
- ✅ Smart Groq API integration with retry models

---

### 🏫 Faculty Module
- ✅ Dedicated faculty dashboard
- ✅ Approve / reject student-uploaded notes
- ✅ View AI safety report per note before review decision
- ✅ Manage forum posts and announcements
- ✅ Note editing and management
- ✅ Student management view
- ✅ Messaging and notifications
- ✅ Race-condition-safe atomic approval operations

---

### 🛡️ Admin Module
- ✅ Admin dashboard with analytics
- ✅ User management (CRUD)
- ✅ System-wide notes management
- ✅ Reports view
- ✅ System settings with Danger Zone (Archive / Restore all notes)
- ✅ Role-based access enforcement

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI (Python) |
| **Frontend** | Jinja2 Templates + Vanilla CSS + JavaScript |
| **Database** | MongoDB (via `motor` async driver) |
| **Authentication** | Session-based (`itsdangerous`) + bcrypt password hashing |
| **AI Provider** | Groq API (`llama-3.1-8b-instant`, `llama-3.3-70b-versatile`) |
| **File Storage** | Local `/uploads` directory |
| **Server** | Uvicorn (ASGI) |
| **Async Runtime** | Python `asyncio` + `asyncio.to_thread` for AI calls |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        BROWSER CLIENT                       │
│           (Student / Faculty / Admin Dashboards)            │
└──────────────────────────┬──────────────────────────────────┘
                           │  HTTP / Form Submissions
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  auth.py    │  │  student.py  │  │   faculty.py      │  │
│  │  (login /   │  │  (upload /   │  │   (approvals /    │  │
│  │  register)  │  │  browse / AI)│  │   management)     │  │
│  └─────────────┘  └──────────────┘  └───────────────────┘  │
│                          │                                  │
│               ┌──────────▼──────────┐                       │
│               │   admin.py          │                       │
│               │   (users / settings)│                       │
│               └─────────────────────┘                       │
└──────────┬─────────────────────────────────────────────────-┘
           │
    ┌──────▼──────┐        ┌───────────────────────┐
    │  MongoDB    │        │  Groq API (External)   │
    │  (motor)    │        │  llama-3.1-8b-instant  │
    │             │        │  llama-3.3-70b-versatile│
    │  users      │        └───────────────────────┘
    │  notes      │
    │  favorites  │        ┌───────────────────────┐
    │  messages   │        │  Local File System     │
    │  forum_posts│        │  /uploads directory    │
    │  notifs     │        └───────────────────────┘
    └─────────────┘
```

**Request Flow:**
1. User submits a form or HTTP request to a FastAPI route.
2. FastAPI verifies the session cookie and role.
3. The route handler interacts with MongoDB and/or the local file system.
4. For file uploads, content is extracted and passed to the Groq AI safety pipeline (async, non-blocking).
5. AI results are stored alongside the note document in MongoDB.
6. Jinja2 templates render the response and return HTML to the browser.

---

## 📁 Project Structure

```
studyvault/
│
├── app/
│   ├── main.py                   # FastAPI app entry point, middleware, router registration
│   ├── database.py               # MongoDB async connection (motor)
│   │
│   ├── routes/
│   │   ├── auth.py               # Login, registration, logout, role validation
│   │   ├── student.py            # All student routes + Groq AI integration
│   │   ├── faculty.py            # Faculty routes (approvals, announcements, forum)
│   │   ├── admin.py              # Admin routes (users, notes, settings, reports)
│   │   └── reports.py            # Reporting / analytics routes
│   │
│   ├── templates/
│   │   ├── auth/                 # Authentication pages
│   │   │   ├── roles.html        # Role selection landing page
│   │   │   ├── login.html        # Login form
│   │   │   └── register.html     # Registration form
│   │   │
│   │   ├── student/              # Student-facing pages
│   │   │   ├── base.html
│   │   │   ├── dashboard.html
│   │   │   ├── upload.html
│   │   │   ├── my_notes.html
│   │   │   ├── browse.html
│   │   │   ├── preview.html
│   │   │   ├── saved.html
│   │   │   ├── messages.html
│   │   │   ├── chat.html
│   │   │   ├── forum.html
│   │   │   ├── ai_assistant.html
│   │   │   ├── announcements.html
│   │   │   ├── notifications.html
│   │   │   ├── faculty.html
│   │   │   └── view_note.html
│   │   │
│   │   ├── faculty/              # Faculty-facing pages
│   │   │   ├── base.html
│   │   │   ├── dashboard.html
│   │   │   ├── approvals.html    # Note review + AI safety modal
│   │   │   ├── manage_notes.html
│   │   │   ├── edit_note.html
│   │   │   ├── preview_note.html
│   │   │   ├── students.html
│   │   │   ├── forum.html
│   │   │   ├── messages.html
│   │   │   ├── chat.html
│   │   │   ├── notifications.html
│   │   │   ├── upload_notes.html
│   │   │   └── announcements.html
│   │   │
│   │   └── admin/                # Admin-facing pages
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── users.html
│   │       ├── notes.html
│   │       ├── reports.html
│   │       ├── settings.html
│   │       ├── messages.html
│   │       └── announcements.html
│   │
│   └── static/
│       ├── css/
│       │   └── student.css       # Custom stylesheet (no frameworks)
│       └── js/
│           └── student.js        # Client-side interactivity
│
├── uploads/                      # Uploaded files stored here
├── .env                          # Environment variables (GROQ_API_KEY, SECRET_KEY)
├── .env.example                  # Template for environment variables
├── requirements.txt              # Python dependencies
└── README.md
```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9+
- MongoDB running on `localhost:27017`
- A free [Groq API key](https://console.groq.com) for AI features

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in the required values:
```env
SECRET_KEY=your_super_secret_key
GROQ_API_KEY=your_groq_api_key_here
```

> 💡 The application runs in **demo mode** if `GROQ_API_KEY` is not set — all features work except live AI responses.

### 3. Start MongoDB
Ensure MongoDB is running on the default port:
```bash
mongod
```

### 4. Run the Application
```bash
uvicorn app.main:app --reload
```

### 5. Open in Browser
```
http://localhost:8000
```

---

## 🔄 Workflow Overview

The complete lifecycle of a note in StudyVault:

```
 ┌─────────────────┐
 │  Student Upload  │  → Student submits file with title & subject
 └────────┬─────────┘
          │
          ▼
 ┌──────────────────────┐
 │  AI Safety Analysis  │  → Groq (llama-3.1-8b-instant) scans content
 │  (Automatic)         │    Scores: toxicity, plagiarism, spam, etc.
 └────────┬─────────────┘
          │
          ▼
 ┌─────────────────────┐
 │  Faculty Review      │  → Faculty views note + AI safety report
 │  (Approvals Panel)   │    and decides: Approve or Reject
 └────────┬─────────────┘
          │
          ▼
 ┌──────────────────────┐
 │  Approved Notes       │  → Note status set to "approved" in DB
 │  (Stored in MongoDB)  │    Student receives approval notification
 └────────┬──────────────┘
          │
          ▼
 ┌──────────────────────┐
 │  Student Access       │  → All students can browse, preview,
 │  (Browse / Download)  │    download, save, and use AI tools on note
 └──────────────────────┘
```

---

## 🤖 AI Features & Safety Analysis

### AI Assistant
The AI Assistant is powered by the **Groq API** using Meta's **Llama models**:

| Tool | Model Used |
|---|---|
| Summarize | `llama-3.1-8b-instant` |
| Flashcards | `llama-3.1-8b-instant` |
| Study Guide | `llama-3.1-8b-instant` |
| Q&A / Ask Questions | `llama-3.3-70b-versatile` |

All AI calls are made asynchronously (via `asyncio.to_thread`) to ensure the server remains non-blocking.

### 🛡️ AI Safety Analysis
Every uploaded document is automatically scanned by the Groq AI pipeline before being presented to faculty for review.

**How it works:**
1. **Text Extraction** — The system extracts readable text from the uploaded file (PDF, DOCX, images via OCR, plain text).
2. **Groq Safety Prompt** — The extracted text is submitted to `llama-3.1-8b-instant` with a structured prompt that instructs it to act as an academic content safety analyzer.
3. **JSON Safety Report** — The model returns a structured JSON report with:
   - `overall`: `Safe` or `Flagged`
   - `violation_type`: e.g., `Hate Speech`, `Plagiarism`, `Spam`, or `None`
   - `reason`: A human-readable explanation
   - `scores`: Numeric scores per category (toxicity, spam, academic integrity, etc.)
4. **Stored with Note** — The safety report is saved in MongoDB alongside the note document.
5. **Faculty Review** — Faculty can open the AI Analysis modal in the approvals panel to view the full safety breakdown before making a decision.

> ⚠️ If `GROQ_API_KEY` is not configured, safety analysis is skipped and notes are marked as `Safe` by default. A warning is logged server-side.

---

## 🔒 Security

| Feature | Status |
|---|---|
| bcrypt password hashing | ✅ |
| Session-based authentication | ✅ |
| Role validation from database (no client trust) | ✅ |
| Role-based access control on all routes | ✅ |
| CORS middleware | ✅ |
| File type and size validation on upload | ✅ |
| Atomic note approval (race-condition safe) | ✅ |
| Session clearing on logout | ✅ |

---

## 📊 Database Collections

| Collection | Purpose |
|---|---|
| `users` | User accounts (all roles), hashed passwords, role field |
| `notes` | Uploaded notes with status, AI safety report, reviewer info |
| `favorites` | Bookmarked note references per student |
| `notifications` | Per-user notification objects with read/unread state |
| `messages` | One-to-one message threads between users |
| `forum_posts` | Forum posts and nested replies |

---

## ✨ UI Highlights

- 🎨 Modern gradient design system with custom CSS variables
- 📱 Fully responsive layout (mobile-friendly)
- 🎯 Role-specific navigation sidebars
- 🎭 Smooth enter/exit animations on cards and modals
- 🔔 Live notification badge counter
- 🪄 AI Modal with structured safety score display
- 📁 Drag-and-drop upload zone with progress feedback
- 🌙 Consistent color scheme across all three portals

---

## 🐛 Error Handling

- ✅ Session expiry detection and redirect to login
- ✅ Graceful file upload error reporting
- ✅ MongoDB error catching with meaningful messages
- ✅ Form validation (frontend + backend)
- ✅ Clean redirects with flash-style status messages
- ✅ AI failures handled gracefully (defaults to Safe, logs warning)

---

## 🧩 Customization

### Change the Color Scheme
Edit `app/static/css/student.css`:
```css
/* Main gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Add or Modify Subjects
Edit the subject dropdown options inside the relevant Jinja2 templates (e.g., `upload.html`, `browse.html`).

### Modify Upload Rules
Edit the `upload_notes` function in `app/routes/student.py`.

---

## ✅ Testing Checklist

### Authentication
- [ ] Student registration creates account
- [ ] Login redirects to correct role dashboard
- [ ] Cross-role login is blocked
- [ ] Logout clears session and redirects

### Student Workflow
- [ ] Upload accepts multiple files with metadata
- [ ] Uploaded notes appear in "My Notes" with `Pending` status
- [ ] AI safety analysis result is stored with note
- [ ] Approved notes appear in Browse with correct status
- [ ] Favorite toggle adds/removes note from Saved
- [ ] Saved page displays bookmarked notes
- [ ] Forum posts and replies appear correctly
- [ ] Notifications display for approvals and replies
- [ ] AI Assistant returns summaries, flashcards, and study guides

### Faculty Workflow
- [ ] Approvals page lists pending notes
- [ ] AI Analysis modal shows safety scores per note
- [ ] Approve action sets status to `approved`
- [ ] Reject action sets status to `rejected`
- [ ] Notification sent to student after review

### Admin Workflow
- [ ] Admin dashboard displays analytics
- [ ] User management CRUD operates correctly
- [ ] Danger Zone archive/restore functions work

---

## 🏁 Conclusion / Project Summary

**StudyVault** is a complete, multi-role academic notes sharing platform. All three modules — **Student**, **Faculty**, and **Admin** — are fully implemented and functional.

Key highlights for demonstration:
- **AI-powered safety pipeline**: Every uploaded note is automatically analyzed by Groq's Llama models before faculty review, ensuring content quality and appropriateness.
- **End-to-end workflow**: From student upload through AI analysis, faculty approval, and student access — the complete lifecycle is implemented.
- **Robust security**: Role validation is enforced server-side on every route, with atomic operations preventing race conditions in the approval flow.
- **Production-quality code**: Async FastAPI routes, non-blocking AI calls, proper error handling, and a clean project structure.

> ✅ **The system is fully functional and ready for demonstration.**

---

*Built with ❤️ for academic excellence*
=======
# studyvault
StudyVault – Online Notes Sharing Platform with AI Moderation built using FastAPI, MongoDB, and Groq API for structured data handling and workflow management.
>>>>>>> 384e8e2dd51959b3dafc8597d44b5905cd043b48

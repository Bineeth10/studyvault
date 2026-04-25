# StudyVault — Complete Project Audit Report
**Project:** Online Notes Sharing Platform  
**Report Generated:** 2026-03-11  
**Prepared By:** Bineeth (BCA Final Year Project)  
**Technology Stack:** FastAPI · MongoDB · Jinja2 · Python 3.x  

---

## 1. Project Overview

StudyVault is a full-stack web application that enables students to upload, share, and discover academic notes. Faculty members review and approve uploaded content. An administrator oversees the entire platform including users, content, reports, announcements, and system settings. The platform includes an AI layer (powered by Groq / LLaMA 3.1) for automatic content safety analysis and intelligent study tools.

---

## 2. Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Web Framework | FastAPI | 0.104.1 |
| ASGI Server | Uvicorn | 0.24.0 |
| Template Engine | Jinja2 | 3.1.2 |
| Database | MongoDB (via PyMongo) | 4.6.0 |
| Password Hashing | Passlib + bcrypt | 1.7.4 / 4.1.1 |
| Session Management | Starlette SessionMiddleware | 0.27.0 |
| AI / LLM Integration | Groq SDK (LLaMA 3.1-8B) | 0.3.0 |
| PDF Text Extraction | PyPDF2 | 3.0.1 |
| Image OCR | Pillow + pytesseract | 10.1.0 / 0.3.10 |
| Word Document Parsing | python-docx | 1.1.0 |
| PowerPoint Parsing | python-pptx | 0.6.21 |
| Environment Config | python-dotenv | 1.0.0 |
| File Uploads | python-multipart | 0.0.6 |

---

## 3. Project Folder Structure

```
studyvault/
├── app/
│   ├── __init__.py               (14 B)
│   ├── main.py                   (6,210 B  — 168 lines)
│   ├── database.py               (4,430 B  — 117 lines)
│   ├── templates.py              (2,899 B)
│   ├── routes/
│   │   ├── __init__.py           (83 B)
│   │   ├── auth.py               (9,088 B  — 235 lines)
│   │   ├── admin.py              (34,245 B — 727 lines)
│   │   ├── faculty.py            (22,774 B — 478 lines)
│   │   ├── student.py            (33,603 B — 738 lines)
│   │   └── reports.py            (3,957 B)
│   ├── static/
│   │   ├── css/
│   │   │   ├── admin.css         (17,836 B)
│   │   │   ├── faculty.css       (13,950 B)
│   │   │   ├── student.css       (34,640 B)
│   │   │   ├── auth.css          (1,811 B)
│   │   │   └── theme_toggle.css  (7,994 B)
│   │   └── js/
│   │       ├── admin.js          (2,504 B)
│   │       ├── faculty.js        (4,413 B)
│   │       ├── student.js        (7,720 B)
│   │       └── theme_toggle.js   (2,007 B)
│   └── templates/
│       ├── admin/      (8 HTML files)
│       ├── faculty/    (13 HTML files)
│       ├── student/    (15 HTML files)
│       └── auth/       (3 HTML files)
├── uploads/                      (User-uploaded files)
├── requirements.txt              (297 B — 16 packages)
├── create_admin.py               (1,809 B)
├── .env                          (environment secrets)
├── README.md                     (21,124 B)
└── QUICK_SETUP.md                (6,368 B)
```

---

## 4. Source Code Metrics

| File | Lines | Size | Purpose |
|---|---|---|---|
| [app/main.py](file:///c:/Users/Lenovo/studyvault/app/main.py) | 168 | 6.1 KB | App entry point, middleware, routers |
| [app/database.py](file:///c:/Users/Lenovo/studyvault/app/database.py) | 117 | 4.3 KB | DB connection, collections, indexes |
| [app/routes/auth.py](file:///c:/Users/Lenovo/studyvault/app/routes/auth.py) | 235 | 8.9 KB | Login, register, logout |
| [app/routes/admin.py](file:///c:/Users/Lenovo/studyvault/app/routes/admin.py) | 727 | 33.4 KB | Admin dashboard and all admin features |
| [app/routes/faculty.py](file:///c:/Users/Lenovo/studyvault/app/routes/faculty.py) | 478 | 22.2 KB | Faculty review, upload, communication |
| [app/routes/student.py](file:///c:/Users/Lenovo/studyvault/app/routes/student.py) | 738 | 32.8 KB | Student features + AI tools |
| [app/routes/reports.py](file:///c:/Users/Lenovo/studyvault/app/routes/reports.py) | ~80 | 3.9 KB | Content reporting |
| **Total Python** | **~2,543** | **~111 KB** | |
| HTML Templates | 28 files | ~440 KB | Jinja2 server-rendered UI |
| CSS Stylesheets | 5 files | ~76 KB | Role-scoped styling |
| JavaScript Files | 4 files | ~17 KB | Client-side interactivity |
| **Grand Total** | — | **~644 KB** | (excluding uploads and static assets) |

---

## 5. MongoDB Collections

| Collection | Purpose | Key Fields |
|---|---|---|
| [users](file:///c:/Users/Lenovo/studyvault/app/routes/admin.py#263-289) | All user accounts | `name`, `email`, `password` (hashed), [role](file:///c:/Users/Lenovo/studyvault/app/routes/auth.py#28-32), `subjects`, `is_active`, `is_deleted`, `created_at` |
| [notes](file:///c:/Users/Lenovo/studyvault/app/routes/student.py#376-386) | Uploaded study notes | `title`, `subject`, `uploader_id`, `uploader_name`, `uploader_role`, `filename`, `file_path`, [status](file:///c:/Users/Lenovo/studyvault/app/routes/admin.py#290-312), `uploaded_at`, `ai_status`, `ai_flag_reason`, `ai_detailed_results` |
| [notifications](file:///c:/Users/Lenovo/studyvault/app/routes/student.py#687-697) | System event log / alerts | `user_id`, `type`, `title`, [message](file:///c:/Users/Lenovo/studyvault/app/routes/student.py#496-527), `reference_id`, `is_read`, `created_at` |
| [messages](file:///c:/Users/Lenovo/studyvault/app/routes/student.py#496-527) | Direct messaging | `sender_id`, `receiver_id`, `subject`, [message](file:///c:/Users/Lenovo/studyvault/app/routes/student.py#496-527), `is_read`, `created_at` |
| `favorites` | Saved notes per student | `user_id`, `note_id`, `created_at` |
| [reports](file:///c:/Users/Lenovo/studyvault/app/routes/admin.py#456-516) | Content moderation reports | `reporter_id`, `reported_item_id`, `reason`, [status](file:///c:/Users/Lenovo/studyvault/app/routes/admin.py#290-312), `resolved_by`, `resolved_at` |
| [announcements](file:///c:/Users/Lenovo/studyvault/app/routes/faculty.py#333-340) | Platform-wide broadcasts | `title`, `content`, `audience`, `author_id`, `created_at` |
| `forum_posts` | Academic Q&A forum | `title`, `subject`, `content`, `author_id`, `replies`, `created_at` |
| [system_settings](file:///c:/Users/Lenovo/studyvault/app/routes/admin.py#646-652) | Global config | `registrations_enabled`, `ai_enabled`, `max_upload_size`, `allowed_file_types`, `updated_at` |
| `subjects` | Subject master list | `name`, `created_at` |

**Database Indexes Created:**

| Index | Type | Purpose |
|---|---|---|
| `users.email` | Unique | Prevents duplicate registrations |
| `notes.uploader_id` | Standard | Fast "my notes" queries |
| `favorites(user_id, note_id)` | Composite Unique | Prevents duplicate saves |
| `notifications.user_id` | Standard | Fast notification lookup |
| [messages(sender_id, receiver_id)](file:///c:/Users/Lenovo/studyvault/app/routes/student.py#496-527) | Composite | Conversation threading |
| `forum_posts.subject` | Standard | Forum subject filtering |

---

## 6. API Routes — Complete Listing

### Authentication Routes

| Method | Route | Description |
|---|---|---|
| GET | `/roles` | Role selection landing page |
| POST | `/select-role` | Save chosen role to session |
| GET | `/register` | Registration form |
| POST | `/register` | Create new user account |
| GET | `/login` | Login form |
| POST | `/login` | Authenticate and create session |
| GET | `/logout` | Clear session and redirect |
| GET | `/` | Root — redirects to `/roles` |
| GET | `/test` | Health-check endpoint |

### Student Routes (`/student/`)

| Method | Route | Description |
|---|---|---|
| GET | `/student/dashboard` | Personal overview + stats |
| GET | `/student/upload` | Note upload form (drag-and-drop) |
| POST | `/student/upload` | Process file upload + AI safety scan |
| GET | `/student/my-notes` | List own uploaded notes |
| GET | `/student/browse` | Browse all approved community notes |
| POST | `/student/favorite/{note_id}` | Toggle bookmark/save a note |
| GET | `/student/saved` | Personal saved notes library |
| GET | `/student/preview/{note_id}` | Preview note (PDF/Image/Doc) |
| POST | `/student/generate-summary/{note_id}` | AI-generated note summary |
| GET | `/student/download/{note_id}` | Download approved note file |
| GET | `/student/messages` | Messaging inbox |
| GET | `/student/chat/{other_user_id}` | Chat thread with faculty/admin |
| POST | `/student/messages/send` | Send a direct message |
| GET | `/student/forum` | Academic forum posts |
| POST | `/student/forum/post` | Create new forum thread |
| GET | `/student/ai` | AI study tools landing page |
| POST | `/student/ai/process` | AI request (summary/flashcards/Q&A/guide) |
| GET | `/student/announcements` | View platform announcements |
| GET | `/student/notifications` | Full notification inbox |
| POST | `/student/notifications/mark-read` | Mark one notification read |
| POST | `/student/notifications/mark-all-read` | Mark all notifications read |
| GET | `/student/faculty` | Faculty directory for contact |

### Faculty Routes (`/faculty/`)

| Method | Route | Description |
|---|---|---|
| GET | `/faculty/dashboard` | Analytics overview of reviews |
| GET | `/faculty/approvals` | Note approval queue (by status) |
| GET | `/faculty/api/notes` | AJAX endpoint for tab switching |
| POST | `/faculty/approve/{note_id}` | Approve a pending note |
| POST | `/faculty/reject/{note_id}` | Reject a note with reason |
| GET | `/faculty/preview/{note_id}` | Full-screen note preview |
| GET | `/faculty/upload` | Faculty note upload form |
| POST | `/faculty/upload` | Upload faculty note (auto-approved) |
| GET | `/faculty/manage-notes` | Manage own uploaded notes |
| GET | `/faculty/edit-note/{note_id}` | Edit note metadata form |
| POST | `/faculty/edit-note/{note_id}` | Update note metadata |
| GET | `/faculty/delete-note/{note_id}` | Delete own note |
| GET | `/faculty/announcements` | Faculty announcements page |
| POST | `/faculty/announcements` | Post new announcement |
| GET | `/faculty/messages` | Messaging inbox with conversations |
| POST | `/faculty/messages` | Send message to student(s) |
| GET | `/faculty/chat/{student_id}` | One-to-one chat thread |
| GET | `/faculty/forum` | View academic forum |
| GET | `/faculty/students` | Student directory |
| GET | `/faculty/notifications` | Faculty notification inbox |
| POST | `/faculty/notifications/mark-read` | Mark one notification read |
| POST | `/faculty/notifications/mark-all-read` | Mark all notifications read |

### Admin Routes (`/admin/`)

| Method | Route | Description |
|---|---|---|
| GET | `/admin/dashboard` | Command center with analytics |
| GET | `/admin/users` | User management directory |
| POST | `/admin/users/toggle-status` | Activate / deactivate user |
| POST | `/admin/users/delete` | Soft-delete a user |
| POST | `/admin/users/cleanup` | Permanently remove deleted users |
| GET | `/admin/notes` | Global note moderation panel |
| POST | `/admin/notes/approve` | Admin approve a note |
| POST | `/admin/notes/reject` | Admin reject a note with reason |
| POST | `/admin/notes/return` | Return note for revision |
| POST | `/admin/notes/warn` | Issue warning on a note |
| POST | `/admin/notes/delete` | Permanently delete a note |
| GET | `/admin/reports` | Moderation report queue |
| POST | `/admin/reports/resolve` | Resolve a content report |
| GET | `/admin/announcements` | Announcements management |
| POST | `/admin/announcements/create` | Publish new announcement |
| POST | `/admin/announcements/delete` | Delete an announcement |
| GET | `/admin/messages` | Admin communications hub |
| POST | `/admin/messages/send` | Send message to user(s) |
| GET | `/admin/settings` | System configuration panel |
| POST | `/admin/settings/update` | Save platform settings |
| POST | `/admin/danger/archive-all-notes` | Danger: archive all notes |
| POST | `/admin/danger/restore-all-notes` | Danger: restore all archived notes |
| POST | `/admin/danger/delete-archived-notes` | Danger: hard delete archives (Super Admin) |
| POST | `/admin/danger/reset-reports` | Danger: clear all moderation history |
| POST | `/admin/danger/clear-audit-logs` | Danger: purge notification/audit trail (Super Admin) |

**Total API Endpoints: 59**

---

## 7. Features Inventory

### Authentication & Access Control
- Role-based login portals (Student / Faculty / Admin)
- bcrypt password hashing with constant-time verification (anti-timing attack)
- Session-based authentication via Starlette SessionMiddleware
- Account deactivation and soft-deletion
- Admin-controlled registration toggle

### Note Management
- Multi-file drag-and-drop upload (Student)
- Subject-tagging and metadata
- Full status workflow: `pending → approved / rejected / admin_review / archived / blocked`
- Faculty notes are auto-approved
- Unique timestamped filenames to prevent collisions
- File type whitelist (admin-configurable)
- Max upload size enforcement (admin-configurable)
- PDF / Image / DOCX / PPTX browser preview
- Download of approved notes
- Favorite / Bookmark system
- Admin override: approve, reject, return, warn, delete, block

### AI Integration (Groq LLaMA 3.1-8B-Instant)
- **Automatic Safety Scan** on every student upload
  - Detects: Plagiarism, Academic Misconduct, Copyright Violation, Spam, Inappropriate, Malicious content
  - Structured JSON output with 0–10 scores per category
- **AI Summary** — 3–5 academic bullet points from note content
- **AI Flashcards** — 5 Q&A cards on a topic (JSON mode)
- **AI Q&A** — expert tutor answers to student questions
- **Study Guide** — long-form comprehensive guides
- Text extraction: PDF (PyPDF2), Images (Tesseract OCR), DOCX/PPTX (python-docx/python-pptx)
- Demo mode fallback when API key is absent

### Communication
- Admin-to-user, Faculty-to-student, Student-to-faculty direct messaging
- One-to-one chat thread history
- Platform-wide announcements (Admin + Faculty)
- Real-time unread notification count (via custom middleware)
- Per-role notification inbox with mark-read support

### Forum
- Subject-tagged academic Q&A forum threads
- Reply support
- Available to both Students and Faculty

### Admin Analytics
- 7-day trend charts (notes uploaded, reports filed)
- Faculty performance table (avg/fastest/slowest review time, monthly count)
- Automated workload escalation alerts (24h / 48h thresholds)
- Global counters: users by role, notes by status, open reports

### Content Moderation
- User content reporting system
- Report resolution workflow (delete / warn / no action)
- Per-note admin warning flag

### System Settings & Danger Zone
- Toggle registrations on/off, AI on/off
- File type whitelist chip UI, max upload size
- Danger Zone (password + typed keyword confirmation required):
  - Mass archive / restore notes
  - Permanent delete of archives (Super Admin only)
  - Wipe moderation history
  - Purge notification/audit trail (Super Admin only)

### Dark Mode
- Auto-detects system preference
- Manual toggle persisted in localStorage
- Applied across all three role panels

---

## 8. Security Mechanisms

| Mechanism | Details |
|---|---|
| Password storage | bcrypt hashing (passlib) — one-way salted |
| Authentication | Server-side session cookie (Starlette) |
| Role enforcement | Every route checks `session["user"]["role"]` |
| Timing-safe auth | `bcrypt.verify()` runs even for non-existent users |
| Danger Zone | Requires admin password + correctly typed keyword |
| Super Admin gating | Additional `is_super_admin` MongoDB flag check |
| File type security | Extension whitelist from DB; blocked types silently skipped |
| Soft deletion | Users: `is_deleted=True`; not hard-deleted by default |
| Account blocking | `is_active=False` prevents login |

---

## 9. Middleware Stack

```
HTTP Request
  └─► CORSMiddleware          (all origins allowed — dev config)
        └─► SessionMiddleware  (signed cookie sessions)
              └─► NotificationMiddleware
                    └─► Route Handler → Response
```

[NotificationMiddleware](file:///c:/Users/Lenovo/studyvault/app/main.py#37-71) — runs on every request:
- Reads `session["user"]["id"]`
- Attaches `request.state.unread_count` and `request.state.recent_notifications`

---

## 10. File Upload Pipeline

```
1. Student selects file(s)
2. Extension check vs. allowed_file_types (system_settings)
   ├── Not allowed → File silently skipped
   └── Allowed → Continue
3. Save to /uploads/ with unique name: {user_id}_{timestamp}_{original_name}
4. Text extraction (async thread):
   ├── .pdf  → PyPDF2 (first 3,000 characters)
   ├── .docx → python-docx
   ├── .pptx → python-pptx
   └── .jpg/.png → Tesseract OCR (4,000 chars)
5. Groq AI Safety Analysis (async thread) → JSON scores
6. Insert to notes_collection (status: "pending")
7. Notification sent to student
```

---

## 11. Note Status Workflow

```
Student Upload
    ↓
 [pending]
    ├── Faculty Approve  ──► [approved]     ← Visible to all students
    ├── Faculty Reject   ──► [rejected]
    ├── Admin Actions:
    │   ├── Approve      ──► [approved]
    │   ├── Reject       ──► [rejected]
    │   ├── Return       ──► [admin_review] ← Student can revise and re-upload
    │   ├── Warn         ──► [approved + warning_flag]
    │   ├── Block        ──► [blocked]      ← Via report resolution
    │   ├── Archive      ──► [archived]
    │   └── Delete       ──► (removed from DB)
```

---

## 12. AI Tool Summary

| Tool | Input | Model | Output Format |
|---|---|---|---|
| Safety Scan | Note text (≤4,000 chars) | llama-3.1-8b-instant (JSON mode) | `{overall, violation_type, reason, scores{}}` |
| Summary | Note text or custom input | llama-3.1-8b-instant | 3–5 bullet points (HTML) |
| Flashcards | Topic or text | llama-3.1-8b-instant (JSON mode) | `[{q, a}, ...]` — 5 cards |
| Q&A | User question | llama-3.1-8b-instant | Expert answer (variable length) |
| Study Guide | Topic | llama-3.1-8b-instant | Long-form structured guide (HTML) |

---

## 13. Summary Statistics

| Metric | Value |
|---|---|
| Total Python source files | 7 |
| Total Python lines of code | ~2,543 |
| Total API endpoints | 59 |
| HTML template files | 39 |
| CSS files | 5 |
| JavaScript files | 4 |
| MongoDB collections | 10 |
| MongoDB indexes | 6 |
| User roles | 3 (Student, Faculty, Admin) |
| AI tools integrated | 5 |
| Supported file upload types | 8 (pdf, doc, docx, ppt, pptx, jpg, jpeg, png) |
| Danger Zone operations | 5 |
| Total project code size | ~644 KB |

---

## 14. Environment Variables

| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` | API key for Groq LLaMA AI service |
| Session secret | Hardcoded in [main.py](file:///c:/Users/Lenovo/studyvault/app/main.py) (should be moved to [.env](file:///c:/Users/Lenovo/studyvault/.env) for production) |

---

## 15. Known Configuration Notes for Production

1. **MongoDB** — currently unauthenticated on `localhost:27017`; add auth for production
2. **Session secret** — static string; should be a random 32+ character key from [.env](file:///c:/Users/Lenovo/studyvault/.env)
3. **CORS** — `allow_origins=["*"]`; restrict to specific domain in production
4. **Tesseract** — Windows path hardcoded; needs env-var or config for Linux deployment
5. **File storage** — local filesystem only; consider AWS S3 / Cloudflare R2 for scale
6. **AI fallback** — platform degrades gracefully when `GROQ_API_KEY` is missing

---

*End of StudyVault Project Audit Report*  
*Generated: 2026-03-11 | BCA Final Year Project — Bineeth*

# StudyVault — Complete Project Audit Report (Updated)
**Project:** Online Notes Sharing Platform (StudyVault)  
**Report Generated:** 2026-03-12  
**Prepared By:** Bineeth (BCA Final Year Project)  
**Technology Stack:** FastAPI · MongoDB · Jinja2 · Python 3.x  

---

## 1. Project Overview

StudyVault is a full-stack web application that enables students to safely upload, share, and discover academic notes. Faculty members review and approve uploaded content. An administrator oversees the entire platform including users, content, reports, announcements, and system settings. The platform integrates a multi-layered AI & Anti-Plagiarism Engine (powered by Groq / LLaMA 3.1 and local sequence matching) for automatic content safety analysis, plagiarism detection, and intelligent study tools.

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
| Email / SMTP | fastapi-mail + email_validator | 1.4.1 / 2.1.0.post1 |
| AI / LLM Integration | Groq SDK (LLaMA 3.1-8B) | 0.3.0 |
| PDF Text Extraction | PyPDF2 | 3.0.1 |
| Content Matching | Python Native `difflib.SequenceMatcher` | Built-in |
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
│   ├── __init__.py               
│   ├── main.py                   (App entry point, core configs, MIME types)
│   ├── database.py               (PyMongo driver, indexing, initializations)
│   ├── templates.py              (Jinja2 templating global config)
│   ├── core/
│   │   └── email_config.py       (SMTP setup for password resets)
│   ├── routes/
│   │   ├── __init__.py           
│   │   ├── auth.py               (Login, registration, forgot password)
│   │   ├── admin.py              (Admin tools, danger zone, user management)
│   │   ├── faculty.py            (Faculty approvals, document previews)
│   │   ├── student.py            (Upload pipelines, AI tools, plagiarism engine)
│   │   └── reports.py            (Moderation ticketing system)
│   ├── static/
│   │   ├── css/                  (Role-based stylesheets)
│   │   └── js/                   (AJAX async requests, dynamic toasts)
│   └── templates/
│       ├── admin/      
│       ├── faculty/    
│       ├── student/    
│       └── auth/       
├── uploads/                      (Secure local file storage)
├── requirements.txt              
├── create_admin.py               
├── .env                          (Secrets + SMTP credentials)
└── README.md                     
```

---

## 4. Source Code Metrics

| File | Lines | Size | Purpose |
|---|---|---|---|
| `app/main.py` | ~170 | ~6.3 KB | App entry point, middleware, routers, MIME patches |
| `app/database.py` | ~125 | ~4.7 KB | DB connection, collections, indexes |
| `app/routes/auth.py` | ~235 | ~8.9 KB | Login, registration, password reset flows |
| `app/routes/admin.py` | ~750 | ~35.0 KB | Admin dashboard, notifications, systems management |
| `app/routes/faculty.py` | ~500 | ~24.0 KB | Faculty review queues, document previewing |
| `app/routes/student.py` | ~930 | ~43.0 KB | Uploads, AI/LLM connections, deep plagiarism scans |
| `app/core/email_config.py`| ~25 | ~1.0 KB | Configuration for automatic SMTP emails |
| **Total Python** | **~2,735** | **~122 KB** | |
| HTML Templates | 39 files | ~480 KB | Advanced Jinja2 server-rendered UI |
| CSS Stylesheets | 5 files | ~76 KB | Role-scoped modern styling |
| JavaScript Files | 4 files | ~22 KB | Async AJAX calls, badge synchronization, toast rendering |

---

## 5. MongoDB Collections

| Collection | Purpose | Key Fields |
|---|---|---|
| `users` | All system accounts | `name`, `email`, `password` (hashed), `role`, `subjects`, `is_active` |
| `notes` | Uploaded study material | `title`, `file_path`, `status`, `ai_status`, `plagiarism_score`, `duplicate_of` |
| `notifications` | System event alerts | `user_id`, `type`, `title`, `message`, `is_read`, `created_at` |
| `messages` | Direct messages | `sender_id`, `receiver_id`, `subject`, `message`, `is_read` |
| `favorites` | Bookmarks tracking | `user_id`, `note_id` |
| `reports` | Moderation desk items | `reporter_id`, `reported_item_id`, `reason`, `status`, `resolved_by` |
| `password_reset_tokens`| Security | `email`, `token`, `expires_at` (TTL auto-expires) |
| `announcements` | Broadcasts | `title`, `content`, `audience`, `author_id` |
| `forum_posts` | Support/Q&A | `title`, `subject`, `author_id`, `replies` |
| `system_settings` | Global rules | `registrations_enabled`, `ai_enabled`, `max_upload_size` |
| `subjects` | Master topic list | `name`, `created_at` |

---

## 6. API Routes — Newly Added Additions

*Note: In addition to the ~59 original routes, the following critical integrations were recently added to modernise the workflow.*

| Method | Role | Route | Description |
|---|---|---|---|
| POST | Auth | `/auth/forgot-password` | Generates TTL token & sends SMTP reset email |
| POST | Auth | `/auth/reset-password` | Validates token and updates user password in DB |
| POST | Admin | `/admin/notifications/mark-all-read` | AJAX: Marks all admin notifications read instantly |
| DELETE| Admin | `/admin/notifications/clear-all` | AJAX: Wipes the entire admin inbox |
| POST | Faculty| `/faculty/notifications/mark-read/{id}` | AJAX: Marks specific faculty notification |
| DELETE| Faculty| `/faculty/notifications/clear-all` | AJAX: Clears faculty dashboard drawer |
| POST | Student| `/student/notifications/mark-all-read` | AJAX: Synchronizes student notification unread badges |

---

## 7. Advanced Features & Integrations Inventory

### Authentication & Recovery 
- Role-based login portals (Student / Faculty / Admin).
- **Forgot Password Workflow**: Secure 15-minute expiring tokens generated via UUID. Emails dispatched synchronously via standard SMTP (Gmail integration) using `fastapi-mail`.
- Admin-controller registration toggles.

### Advanced Multi-Stage Integrity & Plagiarism Engine
Every student upload undergoes four immediate security layers before reaching pending status:
1. **Extraction:** Async processing parses PDFs (PyPDF2), DOCX (python-docx), PPTX, and Images (Tesseract OCR).
2. **AI Safety Moderation:** Groq LLaMA-3.1 instantly analyses text for hate speech, copyright violations, and spam.
3. **Duplicate Sweeping:** Instantly queries the database to prevent duplicate title submissions across the entire system.
4. **Deep Sequence Matching (Plagiarism Check):** Uses Python's native `difflib.SequenceMatcher` to mathematically correlate the uploaded text against every historically uploaded note in that subject. Content registering **>75% structural similarity** triggers a Plagiarism Flag.
5. **Instant Auto-Reporting:** Plagiarism and High-Risk safety hits automatically push ⚠️ reports directly into the Admin dashboard and notify the uploading student.

### Live View & Approvals Workflow (Faculty)
- **Inline Previewing:** Deep integration overriding browser MIME-types ensures users can safely preview PDFs embedded cleanly within an `<iframe>` inside the system (without forcing hazardous local downloads).
- **Dynamic AI Badging:** Instead of a binary "Safe/Flagged", faculty dashboards intelligently map document states to granular badges (🔴 High Risk, 🟠 Plagiarism % Match, 🟡 Duplicate Title, 🟢 Safe). Corrects nested Jinja2 dictionary looping algorithms for zero-error rendering.
- **Approvals via AJAX:** Faculty action buttons operate flawlessly in the background without refreshing the page.

### Smooth UI Notifications 
- All standard POST/form submissions mapped to asynchronous Javascript `fetch()`.
- Unread badge counters mathematically subtract in real-time.
- Toast notifications pop up softly for action feedback (e.g. "Note Approved", "Inbox Cleared").

---

## 8. Security Mechanisms

| Mechanism | Details |
|---|---|
| Password Storage | bcrypt hashing (passlib) — one-way salted. |
| Time-Safe Tokens | Password reset tokens TTL strictly bound to 15-minute Mongo intervals. |
| Session Identity | Server-side signed session cookies (Starlette). |
| Role Execution | Backend hard-enforces `session["user"]["role"]` validation per API endpoint. |
| Safe Content Delivery | FastAPI `mimetypes` forcefully dictates static assets preventing `octet-stream` executable exploits. |

---

## 9. Middleware Stack

```
HTTP Request
  └─► CORSMiddleware          (Cross-Origin isolation)
        └─► SessionMiddleware  (Cryptographically signed session state)
              └─► NotificationMiddleware  (Asynchronous unread UI counting injected into context)
                    └─► FastAPI Router → Client
```

---

## 10. File Upload Pipeline

```
1. File uploaded via multipart/form-data.
2. Extension mapped against Admin whitelist (system_settings).
3. Saved uniquely to /uploads/: {uploader_id}_{timestamp}_{filename}
4. async asyncio.to_thread extraction (PyPDF2 / Tesseract / DOCX).
5. async AI Moderation Call via Groq LLaMA instant API. 
6. async Plagiarism Check via difflib vs Note Database Candidates.
7. Merge status arrays (Highest Priority Status overrides).
8. Save securely to MongoDB `notes`.
9. (Optional) Auto-generate Admin `reports` document if threshold breached.
```

---

## 11. AI Tool Summaries

| Tool | Engine | Functionality |
|---|---|---|
| **Safety Scanner** | Groq LLaMA-3.1 | JSON-forced content analysis (Hate Speech, Spam, Cheating Docs) |
| **Plagiarism Engine**| Local `difflib` | Exact character sequence pattern matching against historical notes (0-100% scores) |
| **Summarization** | Groq LLaMA-3.1 | Extracts 3–5 bullet points dynamically from 4000-character sample text |
| **Flashcard Generator**| Groq LLaMA-3.1 | Forces JSON strict format yielding exactly 5 study question-answer pairs |
| **Academic Q&A Chat** | Groq LLaMA-3.1 | Instructed model tuned strictly for educational curriculum assistance |

---

## 12. Summary Statistics

| Metric | Details |
|---|---|
| Core Python Scripts | 8 Modules |
| Backend Application Size | ~122 KB (Excluding Dependencies) |
| Total API Endpoints | 65+ |
| Jinja Templated Interfaces| 39 Separate Dynamic Pages  |
| Database Scale | 11 Purpose-Built MongoDB Collections |
| Supported File Extensions | PDF, DOC, DOCX, PPT, PPTX, JPG, JPEG, PNG, MD, TXT |

---

## 13. Environment Variables (.env) Requirements

| Variable | Security Status | Purpose |
|---|---|---|
| `GROQ_API_KEY` | Required | Provisions the LLaMA 3.1 LLM interactions. System safely falls back to Demo tags if absent. |
| `MAIL_USERNAME` | Required (SMTP) | Base email relay account |
| `MAIL_PASSWORD` | Required (SMTP) | **Must** be a 16-character Google App Password (not standard account password) |
| `MAIL_FROM` | Required (SMTP) | Dispatcher email header |
| `MAIL_PORT` | Required (SMTP) | Should always equal 587 (TLS Standard) |
| `MAIL_SERVER` | Required (SMTP) | smtp.gmail.com (Configuration standard) |

---

*End of Application Audit Report*  
*Generated: March 12, 2026 | BCA Final Year Project Delivery | Maintained by Bineeth*

# Real-time Chat Application

<p align="center">
  <strong>Enterprise-grade real-time messaging platform built with Django 6.0, Channels, WebSockets, and Celery.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Django-6.0.6-092E20?logo=django&logoColor=white" alt="Django 6.0">
  <img src="https://img.shields.io/badge/Channels-4.3-46BC99?logo=django&logoColor=white" alt="Channels 4.3">
  <img src="https://img.shields.io/badge/Celery-5.6-37814A?logo=celery&logoColor=white" alt="Celery 5.6">
  <img src="https://img.shields.io/badge/WebSocket-Daphne-FF6C37" alt="Daphne ASGI">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
  <img src="https://img.shields.io/badge/tests-94%20passing-brightgreen" alt="Tests">
</p>

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Deployment](#deployment)
- [API Reference](#api-reference)
- [Design Decisions](#design-decisions)
- [Security](#security)
- [Performance](#performance)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

A production-ready real-time chat application featuring WebSocket-powered instant messaging, group conversations, media sharing, message reactions, read receipts, and push notifications. Built with Django 6.0 and Django Channels, it gracefully degrades from WebSockets to HTTP POST when necessary, making it deployable even on free-tier platforms that don't support ASGI.

---

## Features

### Messaging

- **Real-time messaging** — WebSocket-based instant messaging via Django Channels and Daphne with automatic reconnection
- **Private conversations** — One-on-one direct messaging between users
- **Group conversations** — Multi-user group chats with admin controls, naming, and group images
- **HTTP fallback** — Graceful degradation to HTTP POST when WebSockets are unavailable (e.g., free-tier hosting)
- **Message types** — Supports TEXT, IMAGE, VIDEO, FILE, and AUDIO message types with per-type validation
- **File and media sharing** — Upload attachments per message with S3-compatible storage support
- **Read receipts** — Track which messages each participant has read via `MessageRead` model
- **Message reactions** — Emoji-based reactions: 👍 Like, ❤️ Love, 😂 Laugh, 😮 Wow, 😢 Sad
- **Message history** — Chronological message history with `select_related` optimization on sender queries

### User Experience

- **Dark mode** — System-preference-aware with manual toggle persisted in `localStorage`
- **Responsive design** — Mobile-first layout adapting from 400px to desktop
- **Accessibility** — Skip-to-content link, `aria-current` navigation, `aria-live` regions, keyboard-accessible `:focus-visible` outlines, `prefers-reduced-motion` support
- **Animations** — Subtle fade-in, slide-up, and message entrance animations (disabled for reduced-motion users)
- **Inline SVG icons** — Custom Heroicons-style SVG icons (no external icon library dependency)

### Authentication & Profiles

- **Email-based authentication** — Custom user model with `USERNAME_FIELD = "email"`
- **Registration** — Sign-up form with email, username, password validation, and optional profile fields
- **Profile management** — Update username, bio, phone number, profile picture, and date of birth
- **Online presence** — `is_online` and `last_seen` tracking on user profiles
- **CSRF-protected logout** — POST-based logout with CSRF token

### Notifications

- **Push notifications** — Celery task creates in-app notifications for new messages
- **Notification types** — Supports MESSAGE, GROUP, REACTION, CALL, and SYSTEM notification types
- **Unread badge** — Global unread count in navigation via context processor
- **Bulk actions** — Mark individual or all notifications as read
- **User-scoped** — Notifications are strictly scoped to the recipient user

---

## Tech Stack

| Layer              | Technology                                                  |
|--------------------|-------------------------------------------------------------|
| **Framework**      | Django 6.0.6                                                |
| **ASGI Server**    | Daphne 4.2.2 (for WebSocket connections)                    |
| **WebSockets**     | Django Channels 4.3.2 via `AsyncWebsocketConsumer`          |
| **Message Broker** | Redis 8.0 (development) / `InMemoryChannelLayer` (production free tier) |
| **Task Queue**     | Celery 5.6.3 (eager mode on free tier)                      |
| **Database**       | SQLite (development & free tier) / PostgreSQL (production)  |
| **File Storage**   | Local filesystem or S3-compatible via `django-storages` and `boto3` |
| **Static Files**   | WhiteNoise 6.12                                             |
| **Image Handling** | Pillow 12.2                                                  |
| **Frontend**       | Django Templates, inline SVG icons, vanilla JavaScript (no framework) |

---

## Architecture

The application follows a **service-oriented Django architecture** with five independent apps communicating through shared models and Celery tasks.

```
┌─────────────────────────────────────────────────────────┐
│                       Browser                            │
└────────────┬───────────────────────────┬─────────────────┘
             │ WebSocket (wss://)        │ HTTP (POST/GET)
             ▼                           ▼
┌──────────────────────┐    ┌──────────────────────────────┐
│   Daphne (ASGI)      │    │   Django Views (HTTP)        │
│   ChatConsumer       │    │   - Conversation CRUD        │
│   - connect          │    │   - MessageCreate (fallback) │
│   - receive          │    │   - Auth & Profiles          │
│   - disconnect       │    │   - Notification management  │
└──────────┬───────────┘    └──────────────┬───────────────┘
           │                               │
           ▼                               ▼
┌──────────────────────┐    ┌──────────────────────────────┐
│  Channel Layer       │    │   Database (SQLite/Postgres) │
│  (Redis / InMemory)  │    │   ┌────────────────────────┐ │
│  - Group management  │    │   │ CustomUser             │ │
│  - Message broadcast │    │   │ Conversation           │ │
└──────────────────────┘    │   │ ConversationMember     │ │
                            │   │ Message                │ │
                            │   │ MessageRead            │ │
                            │   │ MessageReaction        │ │
                            │   │ Notification           │ │
                            │   └────────────────────────┘ │
                            └──────────────┬───────────────┘
                                           │
                                           ▼
                            ┌──────────────────────────────┐
                            │  Celery Task                  │
                            │  create_notification.delay()  │
                            │  - Iterates participants      │
                            │  - Creates Notification rows   │
                            └──────────────────────────────┘
```

### Data Flow

1. **WebSocket Path**: Browser establishes WebSocket → `ChatConsumer.connect()` validates membership → messages broadcast via channel layer group → all connected participants receive in real time
2. **HTTP Fallback Path**: Browser sends POST → `MessageCreateView` saves to DB → redirects to conversation detail → page refresh loads new messages
3. **Notification Flow**: After message creation (WebSocket or HTTP), `create_notification.delay()` runs → iterates conversation participants excluding sender → creates `Notification` records → unread badge updates on next page load

---

## Project Structure

```
Real-time Chat Application/
├── manage.py                        # Django management entry point
├── requirements.txt                 # Development dependencies
├── requirements_production.txt      # Production-only dependencies (minimal)
├── .env                             # Environment variables (local dev)
├── .gitignore
│
├── django_project/                  # Django project configuration
│   ├── __init__.py
│   ├── settings.py                  # Base settings (env-aware, DEBUG, DB, Channels)
│   ├── settings_production.py       # Production overrides (PythonAnywhere-ready)
│   ├── urls.py                      # Root URL configuration (5 app includes)
│   ├── asgi.py                      # ASGI app with WebSocket routing
│   ├── wsgi.py                      # WSGI app (HTTP-only fallback)
│   └── celery.py                    # Celery application instance
│
├── accounts/                        # User management app
│   ├── models.py                    # CustomUser (email auth, profile fields, online status)
│   ├── admin.py                     # CustomUserAdmin with profile fieldsets
│   ├── views.py                     # SignUpView (auto-login), ProfileUpdateView
│   ├── forms.py                     # SignUpForm, ProfileUpdateForm
│   ├── urls.py                      # /signup/, /profile/
│   └── tests.py                     # 21 tests (model, forms, views, auth)
│
├── chat/                            # Conversations app
│   ├── models.py                    # Conversation (PRIVATE/GROUP), ConversationMember
│   ├── views.py                     # ListView (paginated 50), DetailView, CreateView
│   ├── consumers.py                 # AsyncWebsocketConsumer for real-time messaging
│   ├── forms.py                     # ConversationForm (participant validation)
│   ├── urls.py                      # /chat/, /chat/create/, /chat/<pk>/
│   ├── templatetags/
│   │   └── chat_tags.py             # display_name, display_initial, display_status filters
│   └── tests.py                     # 27 tests (models, views, forms)
│
├── chat_messages/                   # Messages app
│   ├── models.py                    # Message (5 types), MessageRead, MessageReaction
│   ├── views.py                     # MessageCreateView (membership-enforced)
│   ├── forms.py                     # MessageForm (content/attachment validation)
│   ├── urls.py                      # /messages/send/<conversation_id>/
│   └── tests.py                     # 16 tests (models, forms, views)
│
├── notifications/                   # Notifications app
│   ├── models.py                    # Notification (5 types, read status, indexes)
│   ├── views.py                     # ListView, MarkAsReadView, MarkAllAsReadView
│   ├── tasks.py                     # Celery shared_task: create_notification
│   ├── context_processors.py        # Global unread_count for nav badge
│   ├── urls.py                      # /notifications/, /notifications/<pk>/read/, /notifications/read-all/
│   └── tests.py                     # 18 tests (models, views, permissions)
│
├── pages/                           # Static pages app
│   ├── views.py                     # HomePageView (TemplateView)
│   ├── urls.py                      # /
│   └── tests.py                     # 4 tests (status, template, auth states)
│
├── templates/                       # Project-level templates
│   ├── base.html                    # Master layout: nav, dark mode toggle, unread badge, messages
│   ├── home.html                    # Landing page with hero and feature cards
│   ├── 403.html                     # Forbidden error page with SVG icon
│   ├── 404.html                     # Not found error page with search SVG
│   ├── 500.html                     # Server error page with alert SVG
│   └── registration/
│       ├── login.html               # Email-based login form
│       └── signup.html              # Multi-field registration form
│
├── static/
│   ├── css/style.css                # Complete stylesheet (1266 lines) with design tokens
│   └── js/chat.js                   # WebSocket client with auto-reconnection (3s backoff)
│
└── deploy/
    ├── setup_pythonanywhere.sh      # Automated PythonAnywhere deployment script
    └── pythonanywhere_wsgi.py       # WSGI config file for PythonAnywhere
```

### App Responsibilities

| App              | Models                         | Key Views                                       | Tests |
|------------------|--------------------------------|-------------------------------------------------|-------|
| `accounts`       | `CustomUser`                   | `SignUpView`, `ProfileUpdateView`               | 21    |
| `chat`           | `Conversation`, `ConversationMember` | `ConversationListView`, `ConversationDetailView`, `ConversationCreateView`, `ChatConsumer` | 27 |
| `chat_messages`  | `Message`, `MessageRead`, `MessageReaction` | `MessageCreateView`              | 16    |
| `notifications`  | `Notification`                 | `NotificationListView`, `MarkAsReadView`, `MarkAllAsReadView` | 18 |
| `pages`          | —                              | `HomePageView`                                  | 4     |

---

## Screenshots

> *Screenshots coming soon. The UI features a clean, modern design system with dark mode support, responsive layout, and custom SVG icons.*

---

## Installation

### Prerequisites

- **Python 3.12+**
- **Redis** (optional — only needed for multi-process WebSocket development; falls back to `InMemoryChannelLayer`)
- **Git**

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Musthak2004/Real-time-Chat-Application.git
cd Real-time-Chat-Application

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (optional, defaults work for development)
cp .env.example .env
# Edit .env if needed — defaults use SQLite and local Redis

# 5. Run database migrations
python manage.py migrate

# 6. Collect static files
python manage.py collectstatic --noinput

# 7. Start the development server (ASGI with Daphne for WebSocket support)
daphne -p 8000 django_project.asgi:application
```

> **Note**: For HTTP-only testing (no WebSockets), you can use `python manage.py runserver`, but real-time messaging requires an ASGI server.

### Development with Redis

For full WebSocket functionality across multiple processes:

```bash
# Start Redis (if installed locally)
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:8

# Ensure REDIS_URL is set in .env
# REDIS_URL=redis://localhost:6379/0
```

---

## Usage

### User Flows

1. **Sign Up** → Navigate to `/accounts/signup/`, fill in your email, username, and password
2. **Create a Conversation** → Click "New Conversation", choose private or group, select participants
3. **Send a Message** → Type in the chat input and press Enter (WebSocket) or submit (HTTP fallback)
4. **View Notifications** → Click the bell icon in the nav bar, mark messages as read
5. **Update Profile** → Click your avatar → Edit Profile

### Admin Interface

Access the Django admin at `/admin/` after creating a superuser:

```bash
python manage.py createsuperuser
```

The admin includes custom `CustomUserAdmin` with:
- Profile fieldsets (phone, avatar, bio, DOB, online status)
- Search by username and email
- Filter by online status, staff status, and active status

---

## Testing

The project includes **94 tests** across all five apps with comprehensive coverage of models, forms, views, and edge cases.

```bash
# Run all tests with verbosity
python manage.py test -v 2

# Run tests for a specific app
python manage.py test accounts -v 2
python manage.py test chat -v 2
python manage.py test chat_messages -v 2
python manage.py test notifications -v 2
python manage.py test pages -v 2

# Run with coverage report
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Open htmlcov/index.html in your browser
```

### Test Coverage by App

| App              | Test Count | Coverage Areas                                                                 |
|------------------|------------|--------------------------------------------------------------------------------|
| `accounts`       | 21         | Model validation (DOB), form validation (email, password), view edge cases (duplicate email, login with email, forced logout), template assertions |
| `chat`           | 27         | Model string repr and `get_absolute_url`, `ConversationMember` defaults + unique constraint, permission enforcement (404 for non-members), form validation, pagination |
| `chat_messages`  | 16         | `Message`/`MessageRead`/`MessageReaction` models, form content/attachment validation per message type, membership enforcement, redirect after creation |
| `notifications`  | 18         | Model ordering and string truncation, unread badge count, bulk mark-as-read, ownership enforcement (404 for other users' notifications) |
| `pages`          | 4          | Home page status code, template used, content for anonymous and authenticated users |

### System Checks

```bash
# Run production readiness checks
python manage.py check --deploy --settings=django_project.settings_production
```

---

## Deployment

### PythonAnywhere (Free Plan)

The application is fully deployable on the PythonAnywhere free tier with the following adaptations:

- **No WebSocket support** → HTTP POST fallback for message sending
- **No Redis** → `InMemoryChannelLayer` for Channels
- **No Celery worker** → `CELERY_TASK_ALWAYS_EAGER = True` for synchronous tasks
- **SQLite database** → File-based, no separate DB server needed

**Automated deployment:**

```bash
# From a PythonAnywhere Bash console
bash deploy/setup_pythonanywhere.sh
```

The script handles:
1. Virtual environment creation and dependency installation
2. Secure SECRET_KEY generation (stored in `~/.secrets/`)
3. Database migrations
4. Static files collection
5. Superuser creation (interactive)
6. Media and logs directory creation

**Manual steps after the script:**
1. Go to the **Web** tab, create a new web app (Manual configuration → Python)
2. Set source code, working directory, and virtualenv paths
3. Copy the WSGI config from `deploy/pythonanywhere_wsgi.py`
4. Configure static files: `/static/` → `~/staticfiles`, `/media/` → `~/media`
5. Set environment variables (`SECRET_KEY`, `PYTHONANYWHERE_DOMAIN`)
6. Reload the web app

### Production Settings

The `django_project/settings_production.py` module provides:

| Setting                    | Value                         | Purpose                                  |
|----------------------------|-------------------------------|------------------------------------------|
| `DEBUG`                    | `False`                       | Disables debug mode                      |
| `SECRET_KEY`               | Env-var required              | Validated at startup, raises if missing  |
| `CHANNEL_LAYERS`           | `InMemoryChannelLayer`        | No Redis dependency                      |
| `CELERY_TASK_ALWAYS_EAGER` | `True`                        | Synchronous task execution               |
| `SECURE_HSTS_SECONDS`      | `31536000`                    | HTTP Strict Transport Security           |
| `SESSION_COOKIE_SECURE`    | `True`                        | HTTPS-only session cookies               |
| `CSRF_COOKIE_SECURE`       | `True`                        | HTTPS-only CSRF cookies                  |
| `EMAIL_BACKEND`            | SMTP                          | Email error reporting                    |
| `LOGGING`                  | Console + AdminEmail          | Structured logging with error emails     |

```bash
# Test locally with production settings
python manage.py runserver --settings=django_project.settings_production
```

### S3 File Storage

Enable S3-compatible storage for media files by setting environment variables:

```bash
export USE_S3=True
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_STORAGE_BUCKET_NAME=your_bucket
export AWS_S3_REGION_NAME=us-east-1
```

When `USE_S3=True`, the app uses `S3Boto3Storage` via `django-storages` for both media and static files.

---

## API Reference

### URL Endpoints

| Method | URL Pattern                           | View                        | Description                      |
|--------|---------------------------------------|-----------------------------|----------------------------------|
| GET    | `/`                                   | `HomePageView`              | Landing page                     |
| GET    | `/accounts/signup/`                   | `SignUpView`                | Registration form                |
| POST   | `/accounts/signup/`                   | `SignUpView`                | Create account                   |
| GET    | `/accounts/profile/`                  | `ProfileUpdateView`         | Edit profile form                |
| POST   | `/accounts/profile/`                  | `ProfileUpdateView`         | Update profile                   |
| GET    | `/accounts/login/`                    | Django `LoginView`          | Login form                       |
| POST   | `/accounts/logout/`                   | Django `LogoutView`         | Logout                           |
| GET    | `/chat/`                              | `ConversationListView`      | List conversations (paginated)   |
| GET    | `/chat/create/`                       | `ConversationCreateView`    | New conversation form            |
| POST   | `/chat/create/`                       | `ConversationCreateView`    | Create conversation              |
| GET    | `/chat/<pk>/`                         | `ConversationDetailView`    | Conversation with messages       |
| GET    | `/messages/send/<conversation_id>/`   | `MessageCreateView`         | Message form                     |
| POST   | `/messages/send/<conversation_id>/`   | `MessageCreateView`         | Send message (HTTP fallback)     |
| GET    | `/notifications/`                     | `NotificationListView`      | Notification list (paginated)    |
| POST   | `/notifications/<pk>/read/`           | `MarkAsReadView`            | Mark one notification as read    |
| POST   | `/notifications/read-all/`            | `MarkAllAsReadView`         | Mark all notifications as read   |
| WS     | `ws://host/ws/chat/<conversation_id>/`| `ChatConsumer`              | WebSocket real-time messaging    |

### WebSocket Protocol

**Connection:** `ws://<host>/ws/chat/<conversation_id>/`

**Client → Server:**
```json
{
  "content": "Hello, world!"
}
```

**Server → Client (broadcast):**
```json
{
  "type": "chat_message",
  "id": 42,
  "sender_id": 1,
  "sender_username": "alice",
  "content": "Hello, world!",
  "created_at": "2026-07-01T12:00:00+00:00"
}
```

**Error states:** The server closes the connection if the user is unauthenticated or not a conversation participant.

---

## Design Decisions

### Why CustomUser with email as USERNAME_FIELD

Users authenticate with their email address rather than a username, which is more intuitive for modern web applications and eliminates the need to remember a separate identifier. The `username` field is retained as a display name for the UI. The `REQUIRED_FIELDS` list includes `username`, keeping Django's admin and authentication system fully functional.

### Why WSGI + HTTP fallback on PythonAnywhere

The PythonAnywhere free plan does not support ASGI or WebSockets. The application falls back to HTTP POST for message sending via `MessageCreateView`, ensuring full functionality without WebSockets. The same form view works under both HTTP and WebSocket paths — the WebSocket consumer handles real-time delivery, while `MessageCreateView` persists messages and redirects for a full page refresh.

### Why InMemoryChannelLayer for production

Without Redis on the free plan, Django Channels falls back to `channels.layers.InMemoryChannelLayer`. This works correctly for a single-process WSGI deployment where the channel layer is only used for WebSocket group management (which is bypassed under HTTP fallback).

### Why CELERY_TASK_ALWAYS_EAGER = True

Without a Celery worker process, tasks must run synchronously during the HTTP request-response cycle. Notification creation is fast — a single DB insert per participant — so this does not impact response times. For deployments with a Celery worker, set `CELERY_TASK_ALWAYS_EAGER = False` and configure a real broker (Redis/RabbitMQ).

### Why StaticFilesStorage over CompressedManifestStaticFilesStorage

The manifest static files storage (`ManifestStaticFilesStorage`) requires running `collectstatic` before every test run and adds complexity for cache-busting. For a project of this scale, `StaticFilesStorage` is simpler and equally effective. For high-traffic production deployments, the `CompressedManifestStaticFilesStorage` can be swapped in.

### Why five separate apps

Each app has a distinct domain boundary: user management (`accounts`), conversation grouping (`chat`), individual messages with reactions (`chat_messages`), in-app alerts (`notifications`), and static pages (`pages`). This separation keeps models, views, and tests focused and maintainable. Cross-app references exist only through ForeignKey relationships (e.g., `Message` → `Conversation`, `Notification` → `CustomUser`).

---

## Security

| Measure                        | Implementation                                                |
|--------------------------------|---------------------------------------------------------------|
| **CSRF Protection**            | Enabled on all POST forms including logout                    |
| **WebSocket Origin Validation**| `AllowedHostsOriginValidator` on all WebSocket connections    |
| **XSS Prevention**             | Django template auto-escaping + `textContent` in JavaScript   |
| **HTTPS Enforcement**          | `SECURE_SSL_REDIRECT`, `HSTS`, and secure cookies in production |
| **Proxy SSL**                  | `SECURE_PROXY_SSL_HEADER` configured for PythonAnywhere       |
| **Clickjacking**               | `X-Frame-Options: DENY`                                       |
| **MIME Sniffing**              | `SECURE_CONTENT_TYPE_NOSNIFF = True`                          |
| **Secret Key Validation**      | SECRET_KEY validated at startup in production settings        |
| **User Data Scoping**          | All querysets filter by `request.user` to prevent data leakage|
| **Password Validation**        | Django's built-in validators (similarity, length, common, numeric) |
| **Session Security**           | `SESSION_COOKIE_SECURE = True` in production                  |

---

## Performance

### Database Optimizations

- **`select_related`** on message sender queries to avoid N+1 queries on every message
- **`prefetch_related`** on conversation participants to avoid N+1 on every conversation card
- **`annotate(Count("participants"))`** for member counts in a single query
- **Composite indexes** on frequently-filtered columns: `(conversation, created_at)`, `(recipient, created_at)`, and `(recipient, is_read)`
- **`.only()` and `.iterator()`** in Celery task to minimize memory overhead when iterating participants

### Frontend Optimizations

- **Pagination** on conversation list and notification list (50 items per page)
- **Debounced reconnection** (3-second backoff) for WebSocket disconnects
- **CSS `content-visibility`-like patterns** with scroll containers
- **Custom scrollbar styling** prevents layout shift
- **Semantic HTML** reduces DOM complexity

### Caching Strategy

- **Template-level**: Not currently cached (static content is minimal)
- **Database-level**: SQLite queries are fast for this scale; PostgreSQL or MySQL recommended for production
- **Application-level**: Session data stored in signed cookies (`SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"`)

---

## Database Schema

```sql
-- Core user model
CustomUser (
    id, password, last_login, is_superuser, username, first_name, last_name,
    email (UNIQUE), is_staff, is_active, date_joined,
    phone_number, profile_picture, bio, date_of_birth,
    is_online, last_seen, created_at, updated_at
)

-- Conversations (private or group)
Conversation (
    id, conversation_type (PRIVATE|GROUP), name, image,
    created_by (FK → CustomUser), created_at, updated_at
)
INDEX: (updated_at DESC)

-- Junction table with membership metadata
ConversationMember (
    id, conversation (FK → Conversation), user (FK → CustomUser),
    joined_at, is_admin, is_muted
)
UNIQUE: (conversation, user)

-- Individual messages
Message (
    id, conversation (FK → Conversation), sender (FK → CustomUser),
    message_type (TEXT|IMAGE|VIDEO|FILE|AUDIO), content, attachment,
    is_edited, created_at, updated_at
)
INDEXES: (created_at), (conversation, created_at)

-- Read receipts (tracking per-user read status)
MessageRead (
    id, message (FK → Message), user (FK → CustomUser), read_at
)
UNIQUE: (message, user)

-- Message reactions (emoji-based)
MessageReaction (
    id, message (FK → Message), user (FK → CustomUser),
    emoji (👍|❤️|😂|😮|😢)
)
UNIQUE: (message, user)

-- In-app notifications
Notification (
    id, recipient (FK → CustomUser), sender (FK → CustomUser),
    notification_type (MESSAGE|GROUP|REACTION|CALL|SYSTEM),
    title, message, is_read, created_at
)
INDEXES: (recipient, created_at DESC), (recipient, is_read)
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Write tests for all new functionality (maintain 90%+ coverage)
- Follow Django's CBV patterns (use `LoginRequiredMixin`, `SuccessMessageMixin`)
- Use `select_related` and `prefetch_related` to avoid N+1 queries
- Keep templates semantic and accessible (ARIA attributes, keyboard navigation)
- Add database indexes for new frequently-queried fields
- Run `python manage.py check --deploy` before submitting

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

## Acknowledgments

- **Django Channels** — WebSocket integration and async support
- **Celery** — Asynchronous task queue
- **WhiteNoise** — Static file serving in production
- **PythonAnywhere** — Free-tier hosting platform

---

<p align="center">
  Built with ❤️ using <a href="https://www.djangoproject.com/">Django</a> |
  <a href="https://github.com/Musthak2004/Real-time-Chat-Application">GitHub</a> |
  <a href="https://musthak2004.pythonanywhere.com/">Live Demo</a>
</p>

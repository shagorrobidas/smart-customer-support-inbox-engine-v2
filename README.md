# Smart Customer Support Inbox Engine v2

A highly secure, robust, and scalable backend API engine for a Smart Customer Support Inbox built using **Django**, **Django REST Framework (DRF)**, **Django Channels**, **Celery**, and **Redis**.

This project provides support agents with a real-time collaborative interface to manage client conversations, fetch thread histories, request rule-based AI reply suggestions, and coordinate work using a distributed thread-locking system to prevent duplicate replies.

---

## 🚀 Key Architectural Highlights & Design Patterns

### 1. Stateless JWT Authentication
We use stateless JWT authentication via `djangorestframework-simplejwt`. All client-agent endpoints require a valid `Bearer <token>` in the HTTP `Authorization` header.
*   **Seeded Account**: An idempotent database seed script is provided to create the default support agent:
    *   **Username**: `admin`
    *   **Email**: `admin@test.com`
    *   **Password**: `admin123`

### 2. Distributed Thread Locking Protocol
To avoid race conditions where multiple support agents reply to a single client thread concurrently, we enforce a strict 5-minute locking protocol:
*   **Storage**: Locks are managed in **Redis cache** (`lock:conversation:<id>`) for speed and native TTL support.
*   **Auto-Expiration**: Locks automatically expire in exactly 5 minutes (300 seconds) to prevent permanent lockouts if an agent abandons a tab.
*   **Enforcement**: Other agents are granted read-only access (e.g., listing, viewing thread history). However, any attempt to post a reply (`POST /api/v2/conversations/{id}/messages/`) is systematically blocked if an active, non-owned lock persists.

### 3. Asynchronous Background Sentiment Pipeline (Celery + Redis)
To keep HTTP response times sub-millisecond, text sentiment analysis is offloaded to a background Celery worker queue:
*   When an agent replies, the message is saved immediately and a success `201 Created` status code is returned.
*   Instantly, a non-blocking background task `analyze_sentiment` is dispatched.
*   The worker retrieves the thread, calculates the sentiment score based on keyword densities, and updates the `sentiment` field on the conversation profile to `Positive`, `Neutral`, or `Negative`.

### 4. Real-Time WebSocket Broadcasting & Keepalives (Django Channels)
To support a dynamic, alive inbox UI, updates are pushed instantly to connected clients:
*   When a new message is saved, the view broadcasts it to the Django Channels layer (`channels_redis`).
*   Connected agents listening on the WebSocket route (`ws/chat/{conversation_id}/`) receive the new message payload instantly, eliminating the need for database-heavy client polling.
*   **Robust Keepalives**: The Redis channel layer is configured with active heartbeats (`health_check_interval: 15` seconds) and `retry_on_timeout: True` to prevent idle connection drops and ensure maximum stability.

### 5. Service-Oriented Suggestion Engine
The rule-based AI reply suggestion engine is completely decoupled from Django views and serializers, residing in an isolated service layer (`conversations/services/ai.py`). It uses pre-compiled regex pattern matrices and templates, making it easily replaceable with real AI providers (like OpenAI) in the future without modifying core API views.

---

## 🛠️ Tech Stack Specifications

*   **Core**: Python 3.12, Django 6.0
*   **API Layer**: Django REST Framework, SimpleJWT
*   **Real-time Layer**: Django Channels, Daphne, Channels-Redis
*   **Async Processing & Caching**: Celery, Redis (for broker, result backend, and caches)
*   **Database**: SQLite (default, zero-configuration) / PostgreSQL compatible

---

## 📁 Project Directory Structure

```text
smart-customer-support-inbox-engine-v2/
│
├── core/                    # Project configuration
│   ├── settings.py          # DRF, JWT, Caches, & Celery configurations
│   ├── urls.py              # Global API routes (routes to /api/v2/)
│   ├── celery.py            # Celery app setup
│   ├── asgi.py              # ASGI routing (HTTP + WebSockets)
│   └── wsgi.py              # WSGI gateway
│
├── conversations/           # Conversations Core Application
│   ├── api/
│   │   ├── serializers/
│   │   │   └── conversations.py # Serializers & lock validations
│   │   └── views/
│   │       ├── conversations.py # Generic Views & Celery triggers
│   │       └── locks.py         # Lock management endpoints
│   ├── management/
│   │   └── commands/
│   │       └── seed_agent.py    # Custom seed command for support agent
│   ├── services/
│   │   └── ai.py            # Decoupled AI suggestion logic
│   ├── models.py            # Conversation & Message database models
│   ├── consumers.py         # Channels WebSocket consumer
│   ├── routing.py           # WebSocket routing patterns
│   ├── tasks.py             # Celery background tasks (sentiment analysis)
│   └── utils.py             # Redis-backed cache lock helpers
│
├── api/                     # Global API Helpers & Utilities
│   ├── utils/
│   │   ├── exceptions.py    # Standardized exception handler
│   │   ├── pagination.py    # Custom pagination structure
│   │   └── response.py      # Standardized custom response wrapper
│   └── urls.py              # Sub-routing for core resources
│
├── Dockerfile               # Production build configuration
├── docker-compose.yml       # Dev environment orchestrator (app + redis + celery)
├── manage.py
├── requirements.txt         # Project dependencies
└── Smart customer support.postman_collection .json  # Pre-configured Postman requests
```

---

## ⚙️ Quick Start Guide

### 1. Prerequisites
Ensure you have the following installed on your machine:
*   Python 3.12+
*   Redis server (running locally on port `6379`)

### 2. Install Dependencies & Set Up Environment
Activate your virtual environment and install the package requirements:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run Migrations & Seed the Agent
Apply database schemas and seed the default support agent:
```bash
python manage.py migrate
python manage.py seed_agent
```

### 4. Start the Application & Services
To run the full stack, start both the web server and the Celery background worker:

*   **Start Django Development Server (handles HTTP & WebSockets via Daphne)**:
    ```bash
    python manage.py runserver
    ```

*   **Start Celery Worker (handles background sentiment analysis)**:
    ```bash
    celery -A core worker --loglevel=info
    ```

---

## 🔌 API Documentation & Contract Endpoints

All endpoints are versioned and prefixed with `/api/v2/`.

### 1. Authentication
*   **Obtain JWT Token**: `POST /api/v2/token/`
    *   *Payload*: `{"username": "admin", "password": "admin123"}`
    *   *Response*: `{"status": "success", "data": {"access": "ACCESS_TOKEN", "refresh": "REFRESH_TOKEN"}}`
*   **Refresh JWT Token**: `POST /api/v2/token/refresh/`
    *   *Payload*: `{"refresh": "REFRESH_TOKEN"}`

*Note: All subsequent requests must include the header: `Authorization: Bearer ACCESS_TOKEN`*

### 2. Conversations
*   **List Conversations**: `GET /api/v2/conversations/?page=1&search=John&status=open`
    *   *Supports*: Pagination, search on `customer_name`, and strict filtering on `status` (`open`, `resolved`, `snoozed`).
*   **Thread History**: `GET /api/v2/conversations/{id}/messages/`
    *   *Response*: List of messages in the thread, sorted chronologically.
*   **Post Response (Agent Reply)**: `POST /api/v2/conversations/{id}/messages/`
    *   *Payload*: `{"message": "How can I help you today?"}`
    *   *Rules*: Blocked if another agent holds a lock on the thread. Automatically triggers background sentiment analysis and broadcasts to active WebSockets.
*   **Mock AI Suggestion**: `POST /api/v2/conversations/{id}/suggest-reply/`
    *   *Payload*: `{"message": "Customer wants a refund"}`
    *   *Response*: `{"status": "success", "data": {"suggestion": "We are sorry for the inconvenience..."}}`

### 3. Concurrency Thread Locking
*   **Acquire Lock**: `POST /api/v2/conversations/{id}/lock/`
    *   Acquires an exclusive 5-minute lock. Returns `409 Conflict` if already locked.
*   **Release Lock**: `POST /api/v2/conversations/{id}/unlock/`
    *   Releases lock. Returns `403 Forbidden` if attempting to release a lock owned by another agent.

### 4. Real-time WebSockets
*   **Connect Endpoint**: `ws://localhost:8000/ws/chat/{conversation_id}/`
    *   *Authentication*: Supports standard Django session authentication or token query parameter `?token=ACCESS_TOKEN`.
    *   *Heartbeat*: Includes a 15-second server-to-Redis heartbeat keepalive.

---

## 📮 Postman Collection
A pre-configured Postman Collection is included in the root directory as **`Smart customer support.postman_collection .json`**. Import it directly into Postman to instantly test all endpoints, token retrieval, thread locking, and real-time message broadcasting!

---

## 🧪 Testing

You can run the Django test suite using:
```bash
python manage.py test
```

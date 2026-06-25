# Smart Customer Support Inbox Engine v2

A real-time customer support platform with AI-assisted replies, sentiment analysis, and conversation management.

## Features

- **Real-time Chat** - WebSocket-powered instant messaging between customers and support agents
- **AI Reply Suggestions** - Intelligent pattern-based suggestions for common support scenarios
- **Sentiment Analysis** - Automatic emotion detection on conversations (positive/neutral/negative)
- **Conversation Locking** - Redis-backed locks prevent concurrent editing by multiple agents
- **Agent Dashboard** - List, filter, and manage conversations with pagination
- **JWT Authentication** - Secure token-based access control

## Tech Stack

- **Backend**: Django 6.0.6, Django REST Framework 3.17.1
- **Real-time**: Django Channels 4.3.2 with WebSockets
- **Tasks**: Celery 5.6.3 with Redis broker
- **Database**: PostgreSQL 15 (production), SQLite (development)
- **Server**: Daphne 4.2.2 (ASGI)
- **Authentication**: SimpleJWT 5.5.1
- **Language**: Python 3.12

## Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/shagorrobidas/smart-customer-support-inbox-engine-v2.git
cd smart-customer-support-inbox-engine-v2
docker-compose up -d
```

Services start automatically:
- Web: http://localhost:8000
- Database: PostgreSQL on 5432
- Cache: Redis on 6379
- Admin: admin@test.com / admin123

### Local Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export REDIS_HOST=127.0.0.1
python manage.py migrate
python manage.py seed_agent

# Terminal 1: Start Django
daphne -b 0.0.0.0 -p 8000 core.asgi:application

# Terminal 2: Start Celery worker
celery -A core worker --loglevel=info
```

## API Endpoints

### Authentication
```bash
POST   /api/token/                    # Get JWT token
POST   /api/token/refresh/            # Refresh token
```

### Conversations
```bash
GET    /api/conversations/            # List conversations
POST   /api/conversations/            # Create conversation
GET    /api/conversations/{id}/       # Get conversation details
POST   /api/conversations/{id}/lock/  # Acquire lock
POST   /api/conversations/{id}/unlock/# Release lock
```

### Messages
```bash
GET    /api/conversations/{id}/messages/     # List messages
POST   /api/conversations/{id}/messages/     # Send agent reply
POST   /api/conversations/{id}/suggest-reply/# Get AI suggestion
```

### WebSocket
```
ws://localhost:8000/ws/chat/{conversation_id}/
```

## Project Structure

```
smart-customer-support-inbox-engine-v2/
├── core/                      # Django settings & ASGI config
├── conversations/             # Main app
│   ├── models.py             # Conversation & Message models
│   ├── consumers.py          # WebSocket handlers
│   ├── tasks.py              # Celery sentiment analysis
│   ├── services/
│   │   └── ai.py             # AI suggestion engine
│   └── api/
│       ├── views/            # REST API views
│       ├── serializers.py     # DRF serializers
│       └── urls.py            # Routes
├── api/                       # Shared utilities
│   └── utils/
│       ├── response.py        # StandardResponse class
│       ├── pagination.py      # CustomPagination
│       └── exceptions.py      # Error handling
├── manage.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Database Models

### Conversation
- `customer_name` - Customer identifier (indexed)
- `status` - open, resolved, or snoozed
- `sentiment` - positive, neutral, or negative (auto-detected)
- `created_at`, `updated_at`, `is_active`, `deleted_at`

### Message
- `conversation` - Foreign key to Conversation
- `sender` - customer or agent
- `message` - Message text
- `timestamp` - Created timestamp

## How It Works

1. **Customer initiates** a conversation with initial message
2. **System broadcasts** message to connected agents via WebSocket
3. **AI generates** reply suggestion based on keyword patterns
4. **Agent acquires lock** to prevent conflicts
5. **Agent sends** response → triggers sentiment analysis task
6. **Sentiment analysis** scans all messages for emotion keywords
7. **Status updates** conversation as resolved/snoozed

## AI Suggestions

Pattern-based replies for:
- Refund requests → Refund policy response
- Damaged products → Replacement offer
- Shipping delays → Tracking assistance
- Pricing questions → Coupon codes
- Greetings → Welcome response
- Unmatched → Default human review message

## Configuration

Environment variables (see `docker-compose.yml`):
```
DB_NAME=smart_inbox
DB_USER=postgres
DB_PASSWORD=postgres_password
DB_HOST=db
DB_PORT=5432
REDIS_HOST=redis
```

## Running Tests

```bash
pytest
pytest conversations/tests/
pytest --cov=conversations --cov=api
```

## Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use strong database credentials
- [ ] Enable SSL/TLS
- [ ] Set up log aggregation
- [ ] Configure monitoring for Celery

### Docker Production
```bash
docker-compose -f docker-compose.yml up -d
```

## License

Open source - see LICENSE file

## Support

For issues, questions, or suggestions, open a GitHub issue.

---

**Language Composition**: Python (97.5%), Docker (2.5%)  
**Last Updated**: June 2026

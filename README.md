# Library Service API

A Django REST Framework API for managing library book borrowings. The project handles book catalog management, borrowings, payments, and Telegram notifications for overdue borrowings, processed asynchronously via Celery.

## Tech stack

- **Python / Django / Django REST Framework** — backend API
- **PostgreSQL** — database
- **Redis** — message broker for Celery
- **Celery + django-celery-beat** — asynchronous and periodic tasks (e.g. checking overdue borrowings)
- **Docker / Docker Compose** — containerization and service orchestration

## Features

- User registration and authentication
- Book catalog management (`Book`) with inventory tracking
- Creating and returning borrowings (`Borrowing`) with availability validation
- Payment handling (`Payment`) linked to borrowings, with Stripe Checkout integration
- Telegram notifications on borrowing creation
- Periodic Celery task checking for overdue borrowings

## Requirements

- Docker
- Docker Compose

No local installation of Python or PostgreSQL is required — everything runs in containers.

## Configuration

Create a `.env` file in the project root based on the example below:

```env
# PostgreSQL
POSTGRES_DB=library_service
POSTGRES_USER=library_service_user
POSTGRES_PASSWORD=your-db-password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Django
SECRET_KEY=your-secret-key

# Celery / Redis
CELERY_TIMEZONE="Europe/Warsaw"
CELERY_TASK_TRACK_STARTED=True
CELERY_BROKER_URL="redis://redis:6379"
CELERY_RESULT_BACKEND="redis://redis:6379"

# Telegram
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id

# Stripe
STRIPE_SECRET_KEY=your-stripe-secret-key
```

> **Important:** for values pointing to services running in Docker Compose (database, Redis), use the **service names** from `docker-compose.yml` (`db`, `redis`), not `localhost` — containers communicate with each other by service name, not `localhost`.

## Running the project

Build the images and start all services (database, Redis, the web app, the Celery worker, and Celery Beat):

```bash
docker-compose up --build
```

Database migrations run automatically on startup. The application will be available at:

```
http://localhost:8000/
```

To stop the containers:

```bash
docker-compose down
```

## Creating a superuser

To access the Django admin panel, create a superuser account:

```bash
docker-compose exec web python manage.py createsuperuser
```

The admin panel is available at `http://localhost:8000/admin/`.

## Test data

The repository includes a sample data file (`library_service_test_data.json`) to quickly seed the database with test data (sample users, books, and borrowings). To load it:

```bash
docker-compose exec web python manage.py loaddata library_service_test_data.json
```

## Authentication

The API uses JWT tokens. After logging in, send the token in the `Authorization` header, prefixed with **`Bearer`** (not `Token`):

```
Authorization: Bearer <your_token>
```

Example with `curl`:

```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." http://localhost:8000/api/borrowings/
```

## Tests

To run the project's tests:

```bash
docker-compose exec web python manage.py test
```

## Useful commands

| Command | Description |
|---|---|
| `docker-compose up --build` | Build images and start all services |
| `docker-compose up -d` | Start services in the background (no rebuild) |
| `docker-compose down` | Stop and remove containers |
| `docker-compose logs -f web` | Follow the web app's logs live |
| `docker-compose exec web python manage.py migrate` | Manually run migrations |
| `docker-compose exec web python manage.py createsuperuser` | Create an admin account |
| `docker-compose exec web python manage.py loaddata library_service_test_data.json` | Load test data |
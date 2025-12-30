# Task Management API

**Production-Ready API System**  
A FastAPI based task management API with JWT authentication, role based access control, rate limiting, structured logging, and production ready observability.  

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Features](#features)  
3. [Tech Stack](#tech-stack)  
4. [Setup & Installation](#setup--installation)  
5. [Environment Variables](#environment-variables)  
6. [Running Locally](#running-locally)  
7. [API Documentation](#api-documentation)  
8. [Endpoints](#endpoints)  
9. [Testing](#testing)  
10. [Deployment](#deployment)  
11. [Observability & Monitoring](#observability--monitoring)  
12. [Rate Limiting](#rate-limiting)  

---

## Project Overview

This API provides full CRUD functionality for task management, with secure user authentication, role based access control, Redis based rate limiting, and structured logging. It demonstrates production ready API design patterns, including:

- RESTful resource based routes  
- JWT authentication and password hashing  
- Rate limiting using Redis  
- Asynchronous endpoints and background task capability  
- Health checks and observability  
- API versioning (URL-based `/v1`)  

---

## Features

- User Registration & Login (JWT-based)  
- CRUD for Tasks (`Create`, `Read`, `Update`, `Delete`)  
- Role based access control (user/admin)  
- Rate limiting with Redis (configurable per IP)  
- Structured JSON logging with request IDs  
- Async external API call example (`/tasks/external-joke`)  
- Health and detailed health endpoints (`/health`, `/health/detailed`)  
- Dockerized for containerized deployment  
- OpenAPI/Swagger documentation  

---

## Tech Stack

- **Framework:** FastAPI  
- **Server:** Uvicorn  
- **Database:** SQLite (development)  
- **Authentication:** JWT, bcrypt (via passlib)  
- **Rate Limiting:** Redis  
- **Async HTTP:** httpx  
- **Testing:** pytest, pytest-asyncio, pytest-cov  
- **Containerization:** Docker & Docker Compose  

---

## Setup & Installation

1. **Clone the repository**

```bash
git clone https://github.com/Chelsy-AI/Advanced-API-Patterns.git
cd task-management-api
````

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Start Redis locally** (optional if using Docker)

```bash
redis-server
```

---

## Environment Variables

| Variable     | Description             | Default                    |
| ------------ | ----------------------- | -------------------------- |
| `REDIS_URL`  | Redis connection string | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT signing key         | `4MRzVM8PWPDNACAUBm+IKR5WEDQB2jXzuLNWeW48tkE=`   |

> **Note:** For production, make sure to set `SECRET_KEY` as a strong, random string.

---

## Running Locally

**Option 1: Using Python directly**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Option 2: Using Docker**

```bash
docker-compose up --build
```

* API will be accessible at `http://localhost:8000`
* Redis will be available at `redis://localhost:6379/0`

---

## API Documentation

FastAPI automatically provides **OpenAPI/Swagger**:

* Swagger UI: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

All endpoints, payloads, and response models are documented here.

---

## Endpoints

### Authentication

| Method | Endpoint            | Description                   | Auth Required |
| ------ | ------------------- | ----------------------------- | ------------- |
| POST   | `/v1/auth/register` | Register new user             | No            |
| POST   | `/v1/auth/login`    | Login user, returns JWT token | No            |

### Tasks

| Method | Endpoint                  | Description                     | Auth Required |
| ------ | ------------------------- | ------------------------------- | ------------- |
| POST   | `/v1/tasks/`              | Create a new task               | Yes           |
| GET    | `/v1/tasks/`              | List tasks (pagination)         | Yes           |
| GET    | `/v1/tasks/{task_id}`     | Retrieve a single task          | Yes           |
| PUT    | `/v1/tasks/{task_id}`     | Update task                     | Yes           |
| DELETE | `/v1/tasks/{task_id}`     | Delete task                     | Yes           |
| GET    | `/v1/tasks/external-joke` | Async external API call example | No            |

### Health Checks

| Method | Endpoint           | Description                   |
| ------ | ------------------ | ----------------------------- |
| GET    | `/health`          | Basic health check            |
| GET    | `/health/detailed` | Database + Redis status check |

---

## Testing

Run all tests with **pytest**:

```bash
pytest --cov=app tests/
```

* Ensure **minimum 80% test coverage**
* Tests include authentication, task CRUD, and health endpoints

---

## Deployment

* Dockerized with `Dockerfile` and `docker-compose.yml`
* Ready for deployment on platforms like **Heroku**, **Railway**, **Render**, or **AWS ECS**
* Example Docker Compose command:

```bash
docker-compose up --build
```

* API versioning allows safe future upgrades (`/v1/`)

---

## Observability & Monitoring

* Structured JSON logging with timestamps, log level, and request ID
* Request ID middleware: `X-Request-ID` header included in responses
* Global exception handler ensures consistent error messages
* Health endpoints allow load balancer and monitoring integration

---

## Rate Limiting

* Configurable via Redis (`RATE_LIMIT` = 5 requests per `RATE_PERIOD` = 60s per IP)
* Returns `429 Too Many Requests` with remaining time
* Included as a FastAPI dependency for protected routes

---

## Next Steps / Optional Enhancements

* Add **filtering & sorting** for tasks (`/tasks?completed=true&sort=created_at`)
* Background task processing examples (email notifications, batch operations)
* Response caching using Redis for expensive queries
* Load testing for production deployment

---

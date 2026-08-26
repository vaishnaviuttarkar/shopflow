# ShopFlow

ShopFlow is a Django REST Framework backend application for managing products, stores, inventory, and orders.

The project demonstrates REST API development, PostgreSQL database management, Redis caching, Celery asynchronous processing, Docker containerization, database transactions, API documentation, seed data, and automated testing.

---

## Tech Stack

- Python 3.10
- Django 5.2
- Django REST Framework
- PostgreSQL 16
- Redis 7
- Celery 5.6
- Docker
- Docker Compose
- drf-spectacular / OpenAPI
- Postman

---

## Features

- Product management
- Store management
- Store inventory management
- Order creation
- Order listing
- Product search
- Product autocomplete
- Database transactions using `transaction.atomic()`
- Inventory validation before order confirmation
- Automatic inventory deduction for confirmed orders
- Rejected orders when stock is insufficient
- Redis caching for inventory listing
- Redis cache invalidation after inventory changes
- Celery asynchronous order confirmation processing
- PostgreSQL database
- Seed data management command
- Swagger / OpenAPI documentation
- Postman API collection
- Automated tests
- Dockerized development environment

---

# Project Structure

```text
shopflow/
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
│
├── products/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── stores/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── orders/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tasks.py
│   └── tests.py
│
├── postman/
│   └── ShopFlow.postman_collection.json
│
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

# Setup Instructions

## Prerequisites

Make sure the following are installed:

- Python 3.10+
- Docker
- Docker Compose
- Git
- Postman (optional, for API testing)

---

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd shopflow
```

---

## 2. Local Virtual Environment

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root.

Example:

```env
DEBUG=True

POSTGRES_DB=shopflow
POSTGRES_USER=shopflow
POSTGRES_PASSWORD=shopflow
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/1

CELERY_BROKER_URL=redis://redis:6379/2
CELERY_RESULT_BACKEND=redis://redis:6379/2
```

Do not commit `.env` to GitHub.

The `.env` file should be included in `.gitignore`.

---

# Docker Usage

The project uses Docker Compose to run the application services.

The Docker environment consists of:

```text
Django
   |
   +---- PostgreSQL
   |
   +---- Redis
   |
   +---- Celery Worker
```

---

## Build Docker Images

```bash
docker compose build
```

---

## Start the Application

```bash
docker compose up
```

This starts:

| Service | Purpose |
|---|---|
| `web` | Django application |
| `db` | PostgreSQL database |
| `redis` | Redis cache and Celery broker |
| `celery` | Celery background worker |

Django runs on:

```text
http://127.0.0.1:8001/
```

---

## Run Migrations

After starting Docker:

```bash
docker compose exec web python manage.py migrate
```

---

## Create Seed Data

The project provides a management command for generating sample data.

Run:

```bash
docker compose exec web python manage.py seed_data
```

This creates sample:

- Products
- Stores
- Inventory
- Related application data

---

## Run Tests

Run the complete test suite:

```bash
docker compose exec web python manage.py test
```

The project contains tests covering core API and business functionality including:

- Product APIs
- Store APIs
- Inventory behavior
- Order creation
- Order validation
- Inventory updates

---

## Stop Docker Services

```bash
docker compose down
```

To stop the services and remove the containers while keeping the PostgreSQL volume:

```bash
docker compose down
```

---

# API Documentation

## Swagger UI

Swagger / OpenAPI documentation is integrated using `drf-spectacular`.

Open:

```text
http://127.0.0.1:8001/api/docs/
```

Swagger UI allows the APIs to be viewed and tested directly from the browser.

---

## OpenAPI Schema

The OpenAPI schema is available at:

```text
http://127.0.0.1:8001/api/schema/
```

---

# API Endpoints

## 1. Order Creation

### Endpoint

```http
POST /orders/
```

Creates an order for a store.

The API validates inventory availability before confirming the order.

### Request

```json
{
    "store_id": 1,
    "items": [
        {
            "product_id": 1,
            "quantity_requested": 2
        },
        {
            "product_id": 2,
            "quantity_requested": 1
        }
    ]
}
```

### cURL

```bash
curl -X POST http://127.0.0.1:8001/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": 1,
    "items": [
      {
        "product_id": 1,
        "quantity_requested": 2
      }
    ]
  }'
```

### Order Behavior

If all requested products have sufficient stock:

```text
Order → CONFIRMED
Inventory → Deducted
```

If any product has insufficient stock:

```text
Order → REJECTED
Inventory → Not Deducted
```

The entire operation is wrapped in a database transaction using:

```python
transaction.atomic()
```

This ensures that order creation and inventory updates remain consistent.

---

# 2. Order Listing

### Endpoint

```http
GET /stores/<store_id>/orders/
```

Returns all orders belonging to a store.

Example:

```bash
curl http://127.0.0.1:8001/stores/1/orders/
```

The response includes:

- Order ID
- Order status
- Created timestamp
- Total number of items

Orders are sorted by newest first.

The implementation uses optimized database queries to avoid N+1 query problems.

---

# 3. Inventory Listing

### Endpoint

```http
GET /stores/<store_id>/inventory/
```

Returns inventory for a specific store.

Example:

```bash
curl http://127.0.0.1:8001/stores/1/inventory/
```

The response contains:

- Product title
- Product price
- Category name
- Inventory quantity

Results are sorted alphabetically by product title.

---

# 4. Product Search

### Endpoint

```http
GET /api/search/products/
```

The search API supports keyword searching across:

- Product title
- Product description
- Category name

### Example

```bash
curl "http://127.0.0.1:8001/api/search/products/?q=phone"
```

### Optional Filters

The API supports optional filters such as:

```text
category
price range
store_id
in_stock
```

Example:

```text
/api/search/products/?q=phone&category=electronics&in_stock=true
```

### Sorting

Products can be sorted using supported sorting options such as:

```text
price
newest
relevance
```

Example:

```text
/api/search/products/?q=phone&sort=price
```

The API also provides pagination metadata.

When `store_id` is provided, the response includes the inventory quantity for that store.

---

# 5. Product Autocomplete

### Endpoint

```http
GET /api/search/suggest/?q=xxx
```

The autocomplete API requires a minimum of 3 characters.

Example:

```bash
curl "http://127.0.0.1:8001/api/search/suggest/?q=iph"
```

The API:

- Requires at least 3 characters
- Returns up to 10 product titles
- Prioritizes prefix matches
- Keeps the response lightweight
- Uses efficient database filtering

---

# Redis Caching

Redis is used for caching frequently accessed inventory data.

The inventory listing API checks Redis before querying PostgreSQL.

## Cache Flow

```text
Client
  |
  v
Inventory API
  |
  v
Check Redis
  |
  +---- Cache Hit ----> Return Cached Data
  |
  +---- Cache Miss
          |
          v
      PostgreSQL
          |
          v
      Store Result in Redis
          |
          v
      Return Response
```

Caching reduces repeated database queries for frequently accessed inventory data.

---

## Cache Invalidation

Inventory can change when an order is created.

Therefore, the corresponding inventory cache is invalidated after inventory changes.

```text
Order Created
     |
     v
Inventory Updated
     |
     v
Redis Cache Invalidated
     |
     v
Next Inventory Request
     |
     v
Fresh Data from PostgreSQL
```

This prevents stale inventory information from being returned.

---

# Celery Asynchronous Processing

Celery is used for asynchronous order confirmation processing.

Redis acts as the Celery message broker and result backend.

## Async Flow

```text
Order Created
     |
     v
Database Transaction
     |
     v
Inventory Updated
     |
     v
Celery Task Queued
     |
     v
Redis Broker
     |
     v
Celery Worker
     |
     v
Order Confirmation Processing
```

The Celery task is:

```text
orders.tasks.send_order_confirmation
```

The Celery worker is started automatically by Docker Compose:

```bash
docker compose up
```

A successful worker startup should display:

```text
celery@... ready.
```

This allows background processing to happen outside the main HTTP request-response cycle.

---

# Database Transactions

Order creation and inventory updates are handled using Django database transactions.

The order creation flow is:

```text
Begin Transaction
       |
       v
Validate Products
       |
       v
Check Inventory
       |
       v
Create Order
       |
       v
Update Inventory
       |
       v
Commit Transaction
```

If any validation or database operation fails, the transaction is rolled back.

This ensures:

- No partial inventory updates
- No inconsistent orders
- Stock remains accurate
- Order creation remains atomic

---

# Testing

Run all tests using:

```bash
docker compose exec web python manage.py test
```

The test suite covers core functionality such as:

- API endpoints
- Product functionality
- Store functionality
- Inventory listing
- Order creation
- Successful orders
- Rejected orders
- Inventory updates

---

# Postman Collection

A Postman collection containing the implemented APIs and sample requests is included in:

```text
postman/ShopFlow.postman_collection.json
```

The collection can be imported into Postman.

It includes requests for:

- Order creation
- Store order listing
- Store inventory listing
- Product search
- Product autocomplete

Base URL used by the collection:

```text
http://localhost:8001
```

Update the `store_id` and `product_id` variables according to the seed data in the database.

---

# Scalability Considerations

The application is designed with scalability and performance in mind.

## Redis Caching

Frequently requested inventory data is cached in Redis to reduce database queries and database load.

---

## Database Transactions

`transaction.atomic()` ensures consistency when an order and its inventory changes are performed together.

---

## Efficient Queries

Database relationships and query optimization are used to avoid N+1 query problems, particularly when retrieving:

- Orders
- Order items
- Products
- Categories
- Store inventory

---

## Celery

Long-running or asynchronous operations are handled by Celery workers instead of blocking the main Django request.

Multiple Celery workers can be added as traffic increases.

---

## PostgreSQL

PostgreSQL provides reliable relational storage and supports:

- Indexing
- Efficient filtering
- Transactions
- Concurrent database access
- Read replicas for future scaling

---

## Independent Services

Docker Compose separates the main components:

```text
Django
PostgreSQL
Redis
Celery
```

This architecture allows individual components to be scaled independently.

For example:

```text
                 Load Balancer
                      |
          +-----------+-----------+
          |           |           |
       Django      Django      Django
          |
          v
     PostgreSQL

          +
        Redis
          |
          v
    Celery Workers
     /     |     \
 Worker  Worker  Worker
```

---

# Future Improvements

For a production-scale deployment, the system could be extended with:

- Multiple Django application instances
- Load balancing
- Multiple Celery workers
- Redis clustering
- PostgreSQL read replicas
- Database indexing optimization
- API rate limiting
- Monitoring and centralized logging
- Celery retry policies
- Dead-letter queue handling
- Container orchestration using Kubernetes
- CI/CD pipeline
- Production WSGI/ASGI server

---

# Useful Docker Commands

Check running services:

```bash
docker compose ps
```

View Django logs:

```bash
docker compose logs web
```

View Celery logs:

```bash
docker compose logs celery
```

View Redis logs:

```bash
docker compose logs redis
```

View PostgreSQL logs:

```bash
docker compose logs db
```

Open Django shell:

```bash
docker compose exec web python manage.py shell
```

Run migrations:

```bash
docker compose exec web python manage.py migrate
```

Run seed data:

```bash
docker compose exec web python manage.py seed_data
```

Run tests:

```bash
docker compose exec web python manage.py test
```

Stop all services:

```bash
docker compose down
```

---

# Running the Complete Application

The complete application can be started using:

```bash
docker compose build
docker compose up -d
```

Apply migrations:

```bash
docker compose exec web python manage.py migrate
```

Load seed data:

```bash
docker compose exec web python manage.py seed_data
```

Check services:

```bash
docker compose ps
```

The application is available at:

```text
http://127.0.0.1:8001/
```

Swagger documentation:

```text
http://127.0.0.1:8001/api/docs/
```

OpenAPI schema:

```text
http://127.0.0.1:8001/api/schema/
```

---

# Author

Vaishnavi Uttarkar
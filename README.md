# ShopFlow

ShopFlow is a Django REST Framework backend for managing products, stores, inventory, and orders.

The project demonstrates REST API development, PostgreSQL database management, Redis caching, Celery asynchronous processing, Docker containerization, seed data, and automated testing.

---

## Tech Stack

- Python 3.10
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Docker
- Docker Compose

---

## Features

- Product management
- Store management
- Inventory management
- Order creation
- Automatic inventory deduction during order creation
- Database transactions for order and inventory consistency
- Redis caching for inventory listing
- Redis cache invalidation after inventory updates
- Celery asynchronous order confirmation task
- PostgreSQL database
- Seed data management command
- REST APIs
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
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
Local Setup
1. Clone the Repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd shopflow
2. Create Virtual Environment
python3 -m venv venv

Activate it:

macOS / Linux
source venv/bin/activate
Windows
venv\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
Environment Variables

Create a .env file in the project root.

Example:

DEBUG=True

POSTGRES_DB=shopflow
POSTGRES_USER=shopflow
POSTGRES_PASSWORD=shopflow
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/1

CELERY_BROKER_URL=redis://redis:6379/2
CELERY_RESULT_BACKEND=redis://redis:6379/2

Do not commit .env to GitHub.

Docker Setup

The project uses Docker Compose to run Django, PostgreSQL, Redis, and Celery.

Build Containers
docker compose build
Start All Services
docker compose up

The following services are started:

Django       → 8001
PostgreSQL   → 5432
Redis        → 6379
Celery       → Worker

Django is available at:

http://127.0.0.1:8001/
Run Migrations

After starting Docker:

docker compose exec web python manage.py migrate
Stop Services
docker compose down
Seed Data

The project includes a Django management command to populate the database with sample data.

Run:

docker compose exec web python manage.py seed_data

This creates sample:

Products
Stores
Inventory
Related application data
API Endpoints
Products
List Products
GET /products/

Example:

curl http://127.0.0.1:8001/products/
Stores
List Stores
GET /stores/

Example:

curl http://127.0.0.1:8001/stores/
Inventory
List Store Inventory
GET /stores/<store_id>/inventory/

Example:

curl http://127.0.0.1:8001/stores/2/inventory/

The inventory listing endpoint uses Redis caching.

Order API
Create Order
POST /orders/
Content-Type: application/json

Example request:

{
    "store": 2,
    "items": [
        {
            "product": 1,
            "quantity": 2
        }
    ]
}

Example using curl:

curl -X POST http://127.0.0.1:8001/orders/ \
  -H "Content-Type: application/json" \
  -d '{
        "store": 2,
        "items": [
            {
                "product": 1,
                "quantity": 2
            }
        ]
      }'
Redis Caching

Redis is used to cache the store inventory listing API.

Cache Flow
Client
  |
  v
Inventory API
  |
  v
Check Redis Cache
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

Caching reduces repeated database queries for frequently requested inventory data.

Cache Invalidation

When an order is created, inventory quantities are updated.

The corresponding inventory cache is invalidated after the inventory update.

Order Creation
      |
      v
Inventory Update
      |
      v
Cache Invalidation
      |
      v
Next Inventory Request
      |
      v
Fresh Data from Database

This prevents stale inventory data from being returned.

Celery Asynchronous Processing

Celery is used for asynchronous order confirmation processing.

Redis acts as the Celery message broker and result backend.

Celery Flow
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
Order Confirmation

The Celery task is:

orders.tasks.send_order_confirmation

The Celery worker is started automatically with Docker Compose:

docker compose up

The worker should show:

celery@... ready.
Database Transactions

Order creation and inventory updates are handled using database transactions.

This ensures that inventory is not partially updated if order creation fails.

The general flow is:

Begin Transaction
      |
      v
Validate Order
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

If an error occurs, the transaction is rolled back.

Testing

Run the complete test suite using:

docker compose exec web python manage.py test

The test suite covers core functionality such as:

API endpoints
Product/store functionality
Inventory behavior
Order creation
Inventory updates
Scalability Considerations

The project is designed with scalability in mind.

Redis Caching

Frequently requested inventory data is cached in Redis to reduce database load.

Database Transactions

Transactions ensure consistency when orders and inventory are updated concurrently.

Celery

Asynchronous tasks are moved outside the HTTP request-response cycle, allowing the API to respond without waiting for background operations.

PostgreSQL

PostgreSQL provides reliable relational data storage and supports indexing and efficient querying as the dataset grows.

Independent Services

Docker Compose separates:

Django
PostgreSQL
Redis
Celery

This allows application components to be scaled independently.

Future Improvements

For a production-scale deployment, the architecture could be extended with:

Multiple Django application instances
Multiple Celery workers
Load balancing
Redis clustering
PostgreSQL read replicas
Database indexing optimization
Monitoring and logging
Message retry and dead-letter handling
Horizontal scaling using Kubernetes
Running the Complete Application

The simplest way to run the complete application is:

docker compose build
docker compose up

In another terminal:

docker compose exec web python manage.py migrate

Then seed the database:

docker compose exec web python manage.py seed_data

The application is now available at:

http://127.0.0.1:8001/
Useful Docker Commands

Check running containers:

docker compose ps

View Django logs:

docker compose logs web

View Celery logs:

docker compose logs celery

View Redis logs:

docker compose logs redis

View PostgreSQL logs:

docker compose logs db

Run Django shell:

docker compose exec web python manage.py shell

Run tests:

docker compose exec web python manage.py test

Stop containers:

docker compose down
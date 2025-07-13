# Text-to-SQL System - Development Environment

**Branch: develop** - Complete demo environment with sample database

This branch provides a complete demo environment with local PostgreSQL and sample e-commerce data for testing, development, and demonstrations.

## Features

- Local PostgreSQL with sample e-commerce database
- Pre-loaded data: customers, products, orders, reviews
- Lightweight LLM (CodeLlama 7B)
- Ready-to-use examples
- Zero external dependencies

## Quick Start

```bash
git clone <your-repo>
cd text-to-sql-mvp
git checkout develop
docker-compose up -d
```

Wait for initialization (3-5 minutes for LLM model download):

```bash
docker-compose logs -f api-gateway
```

## URLs

- Swagger UI: http://localhost:8000/docs
- API Gateway: http://localhost:8000
- PostgreSQL: localhost:5432
- Ollama: http://localhost:11434

## Sample Database

The demo includes a complete e-commerce database:
- 10 customers with realistic data
- 16 products across 6 categories
- 10 orders with order items
- Product reviews and ratings
- Relationships between all tables

## Example Questions

Open Swagger UI and try these questions:

### Basic Queries
```
How many customers do we have?
Show me all product categories
What are our best selling products?
```

### Business Analytics
```
Show me the top 5 customers by total spending
Average order value by month
Products with ratings above 4 stars
Customers from California who bought electronics
```

### Complex Queries
```
Monthly revenue trends for the last 6 months
Which products have the highest profit margins?
Customers who have never left a review
Orders with more than 3 items
```

## API Endpoints

### Main Endpoint
```bash
POST /query
```

Request format:
```json
{
  "question": "Show me customers from New York",
  "include_explanation": true,
  "limit_rows": 10
}
```

### Utility Endpoints
```bash
GET /database-info
GET /examples
GET /schema-summary
GET /health/services
```

## Service Architecture

```
localhost:8000    # API Gateway (Swagger UI)
localhost:5432    # PostgreSQL (demo database)
localhost:11434   # Ollama (LLM service)
```

Internal services (not exposed):
- Schema Validator
- Query Generator
- Query Executor

## Development Commands

Check service status:
```bash
docker-compose ps
```

View logs:
```bash
docker-compose logs [service-name]
docker-compose logs -f api-gateway
```

Restart services:
```bash
docker-compose restart [service-name]
```

Rebuild services:
```bash
docker-compose build [service-name]
```

## Database Access

Connect to PostgreSQL directly:
```bash
docker exec -it postgres-demo psql -U demo_user -d ecommerce_demo
```

Test connection:
```bash
docker exec -it postgres-demo psql -U demo_user -d ecommerce_demo -c "SELECT COUNT(*) FROM customers;"
```

## Project Structure

```
text-to-sql-mvp/
├── docker-compose.yml           # Demo environment setup
├── .env                        # Demo configuration
├── services/                   # Microservices
│   ├── schema_validator/
│   ├── query_generator/
│   ├── query_executor/
│   └── api_gateway/
└── infrastructure/
    └── postgres/
        └── init.sql           # Sample data
```

## Troubleshooting

### Services not starting
```bash
docker-compose logs [service-name]
docker-compose restart [service-name]
```

### LLM model download issues
```bash
docker-compose logs ollama
```
Note: Model download is one-time only (first startup)

### Database connection issues
```bash
docker-compose logs postgres
docker exec -it postgres-demo psql -U demo_user -d ecommerce_demo -c "SELECT COUNT(*) FROM customers;"
```

### Reset environment
```bash
docker-compose down -v
docker-compose up -d
```

## Testing the API

Test main endpoint:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many customers do we have?",
    "include_explanation": true
  }'
```

Check system health:
```bash
curl http://localhost:8000/health/services
```

Get database info:
```bash
curl http://localhost:8000/database-info
```

Browse schema:
```bash
curl http://localhost:8000/schema-summary
```
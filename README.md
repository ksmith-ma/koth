# King of the Hill (KotH) - TV Ad Script Comparison Service

A high-performance, asynchronous backend service for comparing TV advertisement scripts using LLMs. This service evaluates multiple scripts simultaneously and determines which performs best.

## Features

- **Fast & Asynchronous**: Evaluates multiple scripts in parallel
- **LLM Agnostic**: Uses LiteLLM to support multiple LLM providers
- **RESTful API**: Simple HTTP API for submitting scripts and retrieving results
- **Scalable**: Can be scaled horizontally for high throughput
- **Docker Ready**: Easy deployment with Docker and docker-compose

## Getting Started

### Prerequisites

- Python 3.10+
- Redis (for production deployments with Celery)
- API key for an LLM provider (OpenAI, Anthropic, Azure OpenAI, etc.)

### Local Development Setup

1. **Clone the repository**

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Add your LLM API key and other configuration

5. **Run the service**:
   ```bash
   # Start the API server
   uvicorn app.main:app --reload

   # For production with Celery workers (in a separate terminal)
   # 1. Start Redis
   docker run -d -p 6379:6379 --name redis redis:latest
   
   # 2. Start Celery worker
   celery -A app.tasks.celery_app worker --loglevel=info
   ```

### Using Docker Compose

The easiest way to get everything running is with Docker Compose:

```bash
# Start all services (API, Celery worker, Redis)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## API Usage

### Comparing Scripts

```bash
curl -X POST "http://localhost:8000/api/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "scripts": [
      "Buy our product! It's the best thing ever!",
      "Our product will change your life forever. Try it today!"
    ],
    "model": "gpt-4"
  }'
```

Response:
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "PROCESSING"
}
```

### Getting Results

```bash
curl "http://localhost:8000/api/compare/3fa85f64-5717-4562-b3fc-2c963f66afa6/results"
```

Response:
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "COMPLETED",
  "evaluations": [
    {
      "script": "Our product will change your life forever. Try it today!",
      "score": 8.5,
      "analysis": "Strong emotional appeal with clear call to action"
    },
    {
      "script": "Buy our product! It's the best thing ever!",
      "score": 6.2,
      "analysis": "Direct but lacks specificity and emotional connection"
    }
  ],
  "winner": {
    "script": "Our product will change your life forever. Try it today!",
    "score": 8.5,
    "analysis": "Strong emotional appeal with clear call to action"
  }
}
```

## Architecture

This service follows a clean, modular architecture:

- **FastAPI**: Provides the HTTP API and handles request validation
- **Async Processing**: Uses FastAPI's background tasks for simple deployments
- **Celery Workers**: For production workloads, distributes tasks across workers
- **LiteLLM**: Abstracts LLM provider details for provider-agnostic implementation
- **Redis**: Used as message broker and result backend for Celery

## Extending the Service

### King of the Hill Tournament Implementation

To implement a full tournament where winners compete against each other:

1. Create a new endpoint in `api.py` for tournament creation
2. Track tournament state (participants, rounds, winners) in a database
3. Use the existing comparison logic for each round of evaluation

### Adding a Frontend Dashboard

To add a simple dashboard:

1. Create a new directory for frontend code (e.g., `frontend/`)
2. Implement a simple React or Vue.js app
3. Use the existing API endpoints to submit jobs and display results

## Performance Optimization

For maximum performance:

1. Run multiple Celery workers
2. Use a production-grade ASGI server like Gunicorn with Uvicorn workers
3. Configure Redis with appropriate persistence settings
4. Consider deploying on Kubernetes for auto-scaling

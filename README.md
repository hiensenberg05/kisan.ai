# Kisan.AI Backend Service

## Overview

Kisan.AI is an AI-powered agricultural assistant that provides farmers with valuable insights and information. This backend service powers the Kisan.AI platform, handling data processing, API integrations, and AI model inference.

## Features

- **Multi-agent System**: Modular agents for different agricultural domains (market, weather, disease diagnosis, etc.)
- **Web Scraping**: Tools for extracting agricultural data from various online sources
- **API Integrations**: Connections to Plant.Health, AgnoMarket, and other agricultural data providers
- **RESTful API**: FastAPI-based endpoints for frontend and mobile applications
- **Asynchronous Processing**: Efficient handling of concurrent requests
- **Comprehensive Logging**: Structured logging for monitoring and debugging

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL (for production)
- Redis (for caching and task queuing)
- API keys for external services (Plant.Health, AgnoMarket, etc.)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/kisan-ai-backend.git
   cd kisan-ai-backend/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Configuration

Create a `.env` file in the project root with the following variables:

```env
# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/kisan_ai
REDIS_URL=redis://localhost:6379/0

# API Keys
PLANT_HEALTH_API_URL=https://plant-health-api.example.com
PLANT_HEALTH_API_KEY=your_plant_health_api_key
AGNOMARKET_API_URL=https://agnomarket-api.example.com
AGNOMARKET_API_KEY=your_agnomarket_api_key

# CORS
ALLOWED_ORIGINS=*
```

## Running the Application

### Development

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Production

For production deployment, use a production-ready ASGI server like Uvicorn with Gunicorn:

```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 main:app
```

## API Documentation

Once the application is running, you can access:

- **Interactive API Docs**: `http://localhost:8000/docs`
- **Alternative API Docs**: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── api/                    # API routes and endpoints
│   ├── __init__.py
│   └── routes.py           # API route definitions
├── agents/                 # AI agents
│   ├── __init__.py
│   ├── base_agent.py       # Base agent class
│   ├── market_agent.py     # Market data agent
│   ├── disease_agent.py    # Plant disease agent
│   └── ...
├── models/                 # Database models
│   ├── __init__.py
│   └── schemas.py          # Pydantic models
├── services/               # Business logic
│   ├── __init__.py
│   └── plant_health.py     # Plant.Health API service
├── tools/                  # Utility tools
│   ├── __init__.py
│   ├── web_scraper.py      # Web scraping utilities
│   └── nlp_utils.py        # NLP utilities
├── tests/                  # Test files
│   └── test_web_scraper.py
├── main.py                 # Application entry point
├── requirements.txt        # Project dependencies
└── README.md               # This file
```

## Testing

Run the test suite with:

```bash
pytest tests/
```

For coverage report:

```bash
pytest --cov=./ tests/
```

## Deployment

### Docker

Build and run using Docker:

```bash
docker-compose up --build
```

### Kubernetes

For Kubernetes deployment, refer to the `k8s/` directory for example manifests.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For support or questions, please contact support@kisan.ai

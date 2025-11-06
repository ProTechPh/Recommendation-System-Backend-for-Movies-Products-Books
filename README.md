# Recommendation System Backend

A FastAPI-based recommendation system backend supporting Movies, Products, and Books with hybrid recommendation algorithms.

## Features

- User authentication (JWT tokens) with anonymous user support
- Item management for Movies, Products, and Books
- Rating system (1-5 stars)
- Hybrid recommendation engine:
  - Collaborative filtering
  - Content-based filtering
  - Popular recommendations
  - Personalized recommendations

## Setup

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
Create a `.env` file or export environment variables:
```bash
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=recommendation_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

### Docker Deployment

#### Using Docker Hub

Pull the pre-built image from Docker Hub:
```bash
docker pull jericko134/recommendation-api
```

Then run the container:
```bash
docker run -d -p 8000:8000 \
  --env-file .env \
  --name recommendation-api \
  jericko134/recommendation-api
```

#### Building from Source

1. Build the Docker image:
```bash
docker build -t recommendation-system-backend .
```

2. Run the container:
```bash
docker run -d -p 8000:8000 \
  --env-file .env \
  --name recommendation-api \
  recommendation-system-backend
```

Or with environment variables:
```bash
docker run -d -p 8000:8000 \
  -e MONGODB_URL=mongodb://your-mongodb-url:27017 \
  -e DATABASE_NAME=recommendation_db \
  -e SECRET_KEY=your-secret-key-change-in-production \
  -e ALGORITHM=HS256 \
  -e ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  --name recommendation-api \
  recommendation-system-backend
```

3. View logs:
```bash
docker logs recommendation-api
```

4. Stop the container:
```bash
docker stop recommendation-api
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc


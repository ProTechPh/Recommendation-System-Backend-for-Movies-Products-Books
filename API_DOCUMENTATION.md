# API Documentation

## Table of Contents

1. [API Overview](#api-overview)
2. [Docker Deployment](#docker-deployment)
3. [Authentication](#authentication)
4. [Endpoints](#endpoints)
   - [Root & Health](#root--health)
   - [Authentication](#authentication-endpoints)
   - [Users](#users-endpoints)
   - [Items](#items-endpoints)
   - [Ratings](#ratings-endpoints)
   - [Recommendations](#recommendations-endpoints)
5. [Data Models](#data-models)
6. [Error Handling](#error-handling)
7. [Usage Examples](#usage-examples)

---

## API Overview

### Service Description

The Recommendation System Backend API is a FastAPI-based service that provides personalized recommendations for Movies, Products, and Books. It uses hybrid recommendation algorithms combining collaborative filtering and content-based filtering to deliver accurate and relevant suggestions.

### Base URL

```
http://localhost:8000
```

### API Version

**Current Version:** `1.0.0`

### Interactive Documentation

Once the server is running, you can access:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

### Authentication and Authorization

The API uses **Bearer Token Authentication** (JWT tokens). Most endpoints require authentication, while some support anonymous users for read-only operations.

**Authentication Flow:**
1. Register a new user via `/auth/register`
2. Login via `/auth/login` to receive an access token
3. Include the token in subsequent requests using the `Authorization` header:
   ```
   Authorization: Bearer <your-token>
   ```

**Token Format:**
- Token type: `Bearer`
- Expiration: 30 minutes (configurable)
- Algorithm: HS256

### Rate Limiting

Currently, rate limiting is not implemented. For production, it's recommended to implement rate limiting based on your requirements.

### CORS Configuration

The API supports CORS (Cross-Origin Resource Sharing) with the following settings:
- All origins allowed (configure for production)
- All methods allowed
- All headers allowed
- Credentials allowed

---

## Docker Deployment

The API can be deployed using Docker for easy containerization and deployment.

### Prerequisites

- Docker installed on your system
- MongoDB instance (either local or remote)

### Building the Docker Image

To build the Docker image:

```bash
docker build -t recommendation-system-backend .
```

### Running the Container

#### Using Environment Variables

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

#### Using .env File

If you have a `.env` file in the project root:

```bash
docker run -d -p 8000:8000 \
  --env-file .env \
  --name recommendation-api \
  recommendation-system-backend
```

### Environment Variables

The following environment variables can be configured:

- `MONGODB_URL`: MongoDB connection string (default: `mongodb://localhost:27017`)
- `DATABASE_NAME`: Database name (default: `recommendation_db`)
- `SECRET_KEY`: Secret key for JWT token signing (required)
- `ALGORITHM`: JWT algorithm (default: `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes (default: `30`)

### Container Management

#### View Logs

```bash
docker logs recommendation-api
```

#### Follow Logs (Real-time)

```bash
docker logs -f recommendation-api
```

#### Stop Container

```bash
docker stop recommendation-api
```

#### Start Container

```bash
docker start recommendation-api
```

#### Remove Container

```bash
docker rm recommendation-api
```

#### Remove Container and Image

```bash
docker rm recommendation-api
docker rmi recommendation-system-backend
```

### Health Check

The Docker container includes a built-in health check that monitors the `/health` endpoint. You can check the container health status:

```bash
docker ps
```

The health status will be displayed in the `STATUS` column.

### Accessing the API

Once the container is running, the API will be available at:

- **API Base URL:** `http://localhost:8000`
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **Health Check:** `http://localhost:8000/health`

### Docker Compose (Optional)

For easier management, you can use Docker Compose. Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
      - DATABASE_NAME=recommendation_db
      - SECRET_KEY=your-secret-key-change-in-production
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30
    depends_on:
      - mongodb
    restart: unless-stopped

  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped

volumes:
  mongodb_data:
```

Then run:

```bash
docker-compose up -d
```

### Authentication with Docker

When using Docker, authentication works the same way as with local deployment:

1. **Register a user:**
   ```bash
   curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "username": "johndoe",
       "password": "securepassword123"
     }'
   ```

2. **Login to get token:**
   ```bash
   curl -X POST "http://localhost:8000/auth/login?email=user@example.com&password=securepassword123"
   ```

3. **Use Bearer token in requests:**
   ```bash
   curl -H "Authorization: Bearer <your-token>" \
     "http://localhost:8000/users/me"
   ```

The Bearer token authentication header format remains the same:
```
Authorization: Bearer <your-jwt-token>
```

---

## Endpoints

### Root & Health

#### Get Root Information

```http
GET /
```

**Description:** Returns API information and available documentation links.

**Response:** `200 OK`

```json
{
  "message": "Recommendation System Backend API",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

#### Health Check

```http
GET /health
```

**Description:** Health check endpoint to verify API availability.

**Response:** `200 OK`

```json
{
  "status": "healthy"
}
```

---

### Authentication Endpoints

#### Register User

```http
POST /auth/register
```

**Description:** Register a new user account.

**Authentication:** Not required

**Request Body:**

```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123",
  "preferences": {
    "favorite_genres": ["action", "drama"],
    "preferred_item_types": ["movie", "book"]
  }
}
```

**Request Schema:**
- `email` (string, required): Valid email address
- `username` (string, required): Unique username
- `password` (string, required): User password (min 8 characters recommended)
- `preferences` (object, optional): User preferences dictionary

**Response:** `201 Created`

```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "is_anonymous": false,
  "preferences": {
    "favorite_genres": ["action", "drama"],
    "preferred_item_types": ["movie", "book"]
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input data
- `409 Conflict`: Email or username already exists

#### Login

```http
POST /auth/login
```

**Description:** Authenticate user and receive access token.

**Authentication:** Not required

**Query Parameters:**
- `email` (string, required): User email
- `password` (string, required): User password

**Example Request:**

```bash
curl -X POST "http://localhost:8000/auth/login?email=user@example.com&password=securepassword123"
```

**Response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid email or password
- `422 Unprocessable Entity`: Validation error

#### Get Current User Info

```http
GET /auth/me
```

**Description:** Get information about the currently authenticated user.

**Authentication:** Required (Bearer Token)

**Response:** `200 OK`

```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "is_anonymous": false,
  "preferences": {
    "favorite_genres": ["action", "drama"]
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token

---

### Users Endpoints

#### Get My Profile

```http
GET /users/me
```

**Description:** Get the current user's profile information.

**Authentication:** Required (Bearer Token)

**Response:** `200 OK`

```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "is_anonymous": false,
  "preferences": {
    "favorite_genres": ["action", "drama"]
  }
}
```

#### Update My Profile

```http
PUT /users/me
```

**Description:** Update the current user's profile.

**Authentication:** Required (Bearer Token)

**Request Body:**

```json
{
  "username": "newusername",
  "preferences": {
    "favorite_genres": ["action", "comedy", "sci-fi"],
    "preferred_item_types": ["movie"]
  }
}
```

**Request Schema:**
- `username` (string, optional): New username
- `preferences` (object, optional): Updated preferences dictionary

**Response:** `200 OK`

```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "username": "newusername",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "is_anonymous": false,
  "preferences": {
    "favorite_genres": ["action", "comedy", "sci-fi"],
    "preferred_item_types": ["movie"]
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `400 Bad Request`: Invalid input data

---

### Items Endpoints

#### Create Movie

```http
POST /items/movies
```

**Description:** Create a new movie item.

**Authentication:** Not required

**Request Body:**

```json
{
  "title": "The Matrix",
  "description": "A computer hacker learns about the true nature of reality",
  "genres": ["action", "sci-fi", "thriller"],
  "tags": ["cyberpunk", "philosophy", "virtual-reality"],
  "metadata": {
    "director": "Lana Wachowski, Lilly Wachowski",
    "cast": ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss"],
    "release_date": "1999-03-31",
    "poster_url": "https://example.com/poster.jpg",
    "duration_minutes": 136
  }
}
```

**Request Schema:**
- `title` (string, required): Movie title
- `description` (string, required): Movie description
- `genres` (array of strings, optional): Movie genres
- `tags` (array of strings, optional): Movie tags
- `metadata` (object, optional): Movie metadata
  - `director` (string, optional)
  - `cast` (array of strings, optional)
  - `release_date` (string, optional)
  - `poster_url` (string, optional)
  - `duration_minutes` (integer, optional)

**Response:** `201 Created`

```json
{
  "id": "507f1f77bcf86cd799439012",
  "item_type": "movie",
  "title": "The Matrix",
  "description": "A computer hacker learns about the true nature of reality",
  "genres": ["action", "sci-fi", "thriller"],
  "tags": ["cyberpunk", "philosophy", "virtual-reality"],
  "metadata": {
    "director": "Lana Wachowski, Lilly Wachowski",
    "cast": ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss"],
    "release_date": "1999-03-31",
    "poster_url": "https://example.com/poster.jpg",
    "duration_minutes": 136
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Create Product

```http
POST /items/products
```

**Description:** Create a new product item.

**Authentication:** Not required

**Request Body:**

```json
{
  "name": "Wireless Headphones",
  "category": "electronics",
  "description": "High-quality wireless headphones with noise cancellation",
  "genres": ["electronics", "audio"],
  "tags": ["wireless", "noise-cancelling", "bluetooth"],
  "metadata": {
    "brand": "TechBrand",
    "price": 199.99,
    "image_url": "https://example.com/product.jpg",
    "stock": 50,
    "specifications": {
      "battery_life": "30 hours",
      "connectivity": "Bluetooth 5.0",
      "weight": "250g"
    }
  }
}
```

**Request Schema:**
- `name` (string, required): Product name
- `category` (string, required): Product category
- `description` (string, required): Product description
- `genres` (array of strings, optional): Product genres
- `tags` (array of strings, optional): Product tags
- `metadata` (object, optional): Product metadata
  - `brand` (string, optional)
  - `price` (float, optional)
  - `image_url` (string, optional)
  - `stock` (integer, optional)
  - `specifications` (object, optional): Custom specifications

**Response:** `201 Created`

```json
{
  "id": "507f1f77bcf86cd799439013",
  "item_type": "product",
  "name": "Wireless Headphones",
  "description": "High-quality wireless headphones with noise cancellation",
  "genres": ["electronics", "audio"],
  "tags": ["wireless", "noise-cancelling", "bluetooth"],
  "metadata": {
    "brand": "TechBrand",
    "price": 199.99,
    "image_url": "https://example.com/product.jpg",
    "stock": 50,
    "specifications": {
      "battery_life": "30 hours",
      "connectivity": "Bluetooth 5.0",
      "weight": "250g"
    }
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Create Book

```http
POST /items/books
```

**Description:** Create a new book item.

**Authentication:** Not required

**Request Body:**

```json
{
  "title": "1984",
  "description": "A dystopian social science fiction novel",
  "genres": ["fiction", "dystopia", "classic"],
  "tags": ["orwell", "totalitarianism", "classic-literature"],
  "metadata": {
    "author": "George Orwell",
    "isbn": "978-0-452-28423-4",
    "publication_date": "1949-06-08",
    "cover_url": "https://example.com/cover.jpg",
    "pages": 328,
    "publisher": "Secker & Warburg"
  }
}
```

**Request Schema:**
- `title` (string, required): Book title
- `description` (string, required): Book description
- `genres` (array of strings, optional): Book genres
- `tags` (array of strings, optional): Book tags
- `metadata` (object, optional): Book metadata
  - `author` (string, optional)
  - `isbn` (string, optional)
  - `publication_date` (string, optional)
  - `cover_url` (string, optional)
  - `pages` (integer, optional)
  - `publisher` (string, optional)

**Response:** `201 Created`

```json
{
  "id": "507f1f77bcf86cd799439014",
  "item_type": "book",
  "title": "1984",
  "description": "A dystopian social science fiction novel",
  "genres": ["fiction", "dystopia", "classic"],
  "tags": ["orwell", "totalitarianism", "classic-literature"],
  "metadata": {
    "author": "George Orwell",
    "isbn": "978-0-452-28423-4",
    "publication_date": "1949-06-08",
    "cover_url": "https://example.com/cover.jpg",
    "pages": 328,
    "publisher": "Secker & Warburg"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Get Movies

```http
GET /items/movies
```

**Description:** Get a list of movies with optional filtering.

**Authentication:** Not required

**Query Parameters:**
- `skip` (integer, optional, default: 0): Number of items to skip
- `limit` (integer, optional, default: 10, min: 1, max: 100): Maximum number of items to return
- `genre` (string, optional): Filter by genre

**Example Request:**

```bash
curl "http://localhost:8000/items/movies?skip=0&limit=20&genre=action"
```

**Response:** `200 OK`

```json
[
  {
    "id": "507f1f77bcf86cd799439012",
    "item_type": "movie",
    "title": "The Matrix",
    "description": "A computer hacker learns about the true nature of reality",
    "genres": ["action", "sci-fi", "thriller"],
    "tags": ["cyberpunk", "philosophy"],
    "metadata": {...},
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

#### Get Products

```http
GET /items/products
```

**Description:** Get a list of products with optional filtering.

**Authentication:** Not required

**Query Parameters:**
- `skip` (integer, optional, default: 0): Number of items to skip
- `limit` (integer, optional, default: 10, min: 1, max: 100): Maximum number of items to return
- `category` (string, optional): Filter by category
- `genre` (string, optional): Filter by genre

**Response:** `200 OK`

```json
[
  {
    "id": "507f1f77bcf86cd799439013",
    "item_type": "product",
    "name": "Wireless Headphones",
    "description": "High-quality wireless headphones",
    "genres": ["electronics", "audio"],
    "tags": ["wireless", "bluetooth"],
    "metadata": {...},
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

#### Get Books

```http
GET /items/books
```

**Description:** Get a list of books with optional filtering.

**Authentication:** Not required

**Query Parameters:**
- `skip` (integer, optional, default: 0): Number of items to skip
- `limit` (integer, optional, default: 10, min: 1, max: 100): Maximum number of items to return
- `genre` (string, optional): Filter by genre

**Response:** `200 OK`

```json
[
  {
    "id": "507f1f77bcf86cd799439014",
    "item_type": "book",
    "title": "1984",
    "description": "A dystopian social science fiction novel",
    "genres": ["fiction", "dystopia"],
    "tags": ["orwell", "classic"],
    "metadata": {...},
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

#### Get Item by ID

```http
GET /items/{item_id}
```

**Description:** Get a specific item by its ID.

**Authentication:** Not required

**Path Parameters:**
- `item_id` (string, required): Item ID (MongoDB ObjectId)

**Response:** `200 OK`

```json
{
  "id": "507f1f77bcf86cd799439012",
  "item_type": "movie",
  "title": "The Matrix",
  "description": "A computer hacker learns about the true nature of reality",
  "genres": ["action", "sci-fi", "thriller"],
  "tags": ["cyberpunk", "philosophy"],
  "metadata": {...},
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid item ID format
- `404 Not Found`: Item not found

#### Update Item

```http
PUT /items/{item_id}
```

**Description:** Update an existing item.

**Authentication:** Not required

**Path Parameters:**
- `item_id` (string, required): Item ID (MongoDB ObjectId)

**Request Body:**

```json
{
  "description": "Updated description",
  "genres": ["action", "sci-fi", "thriller", "drama"],
  "tags": ["cyberpunk", "philosophy", "virtual-reality"],
  "metadata": {
    "director": "Lana Wachowski, Lilly Wachowski",
    "duration_minutes": 136
  }
}
```

**Request Schema:**
- `description` (string, optional): Updated description
- `genres` (array of strings, optional): Updated genres list
- `tags` (array of strings, optional): Updated tags list
- `metadata` (object, optional): Updated metadata (merged with existing)

**Response:** `200 OK`

```json
{
  "id": "507f1f77bcf86cd799439012",
  "item_type": "movie",
  "title": "The Matrix",
  "description": "Updated description",
  "genres": ["action", "sci-fi", "thriller", "drama"],
  "tags": ["cyberpunk", "philosophy", "virtual-reality"],
  "metadata": {...},
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid item ID format
- `404 Not Found`: Item not found

#### Delete Item

```http
DELETE /items/{item_id}
```

**Description:** Delete an item.

**Authentication:** Not required

**Path Parameters:**
- `item_id` (string, required): Item ID (MongoDB ObjectId)

**Response:** `204 No Content`

**Error Responses:**
- `400 Bad Request`: Invalid item ID format
- `404 Not Found`: Item not found

---

### Ratings Endpoints

#### Create Rating

```http
POST /ratings
```

**Description:** Create or update a rating for an item. If a rating already exists for the user-item pair, it will be updated.

**Authentication:** Required (Bearer Token or Anonymous)

**Request Body:**

```json
{
  "item_id": "507f1f77bcf86cd799439012",
  "rating": 5
}
```

**Request Schema:**
- `item_id` (string, required): Item ID (MongoDB ObjectId)
- `rating` (integer, required): Rating value (1-5)

**Response:** `201 Created`

```json
{
  "id": "507f1f77bcf86cd799439015",
  "user_id": "507f1f77bcf86cd799439011",
  "item_id": "507f1f77bcf86cd799439012",
  "rating": 5,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid item ID or rating value
- `404 Not Found`: Item not found
- `401 Unauthorized`: Not authenticated

#### Get User Ratings

```http
GET /ratings/user/{user_id}
```

**Description:** Get all ratings by a specific user.

**Authentication:** Not required

**Path Parameters:**
- `user_id` (string, required): User ID (MongoDB ObjectId)

**Query Parameters:**
- `skip` (integer, optional, default: 0): Number of items to skip
- `limit` (integer, optional, default: 10, min: 1, max: 100): Maximum number of items to return

**Response:** `200 OK`

```json
[
  {
    "id": "507f1f77bcf86cd799439015",
    "user_id": "507f1f77bcf86cd799439011",
    "item_id": "507f1f77bcf86cd799439012",
    "rating": 5,
    "item_title": "The Matrix",
    "item_name": null,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

**Error Responses:**
- `400 Bad Request`: Invalid user ID format

#### Get Item Ratings

```http
GET /ratings/item/{item_id}
```

**Description:** Get all ratings for a specific item.

**Authentication:** Not required

**Path Parameters:**
- `item_id` (string, required): Item ID (MongoDB ObjectId)

**Query Parameters:**
- `skip` (integer, optional, default: 0): Number of items to skip
- `limit` (integer, optional, default: 10, min: 1, max: 100): Maximum number of items to return

**Response:** `200 OK`

```json
[
  {
    "id": "507f1f77bcf86cd799439015",
    "user_id": "507f1f77bcf86cd799439011",
    "item_id": "507f1f77bcf86cd799439012",
    "rating": 5,
    "username": "johndoe",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

**Error Responses:**
- `400 Bad Request`: Invalid item ID format

#### Get My Ratings

```http
GET /ratings/me
```

**Description:** Get all ratings by the current user.

**Authentication:** Required (Bearer Token or Anonymous)

**Query Parameters:**
- `skip` (integer, optional, default: 0): Number of items to skip
- `limit` (integer, optional, default: 10, min: 1, max: 100): Maximum number of items to return

**Response:** `200 OK`

```json
[
  {
    "id": "507f1f77bcf86cd799439015",
    "user_id": "507f1f77bcf86cd799439011",
    "item_id": "507f1f77bcf86cd799439012",
    "rating": 5,
    "item_title": "The Matrix",
    "item_name": null,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

#### Update Rating

```http
PUT /ratings/{rating_id}
```

**Description:** Update an existing rating. Users can only update their own ratings.

**Authentication:** Required (Bearer Token)

**Path Parameters:**
- `rating_id` (string, required): Rating ID (MongoDB ObjectId)

**Request Body:**

```json
{
  "rating": 4
}
```

**Request Schema:**
- `rating` (integer, required): Updated rating value (1-5)

**Response:** `200 OK`

```json
{
  "id": "507f1f77bcf86cd799439015",
  "user_id": "507f1f77bcf86cd799439011",
  "item_id": "507f1f77bcf86cd799439012",
  "rating": 4,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid rating ID or rating value
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not authorized to update this rating
- `404 Not Found`: Rating not found

#### Delete Rating

```http
DELETE /ratings/{rating_id}
```

**Description:** Delete a rating. Users can only delete their own ratings.

**Authentication:** Required (Bearer Token)

**Path Parameters:**
- `rating_id` (string, required): Rating ID (MongoDB ObjectId)

**Response:** `204 No Content`

**Error Responses:**
- `400 Bad Request`: Invalid rating ID format
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not authorized to delete this rating
- `404 Not Found`: Rating not found

---

### Recommendations Endpoints

#### Get Personalized Recommendations

```http
GET /recommendations/personalized
```

**Description:** Get personalized recommendations for the current user using the specified method. Falls back to popular items if no personalized recommendations are available.

**Authentication:** Required (Bearer Token or Anonymous)

**Query Parameters:**
- `method` (string, optional, default: "hybrid"): Recommendation method
  - `hybrid`: Combine collaborative and content-based filtering
  - `collaborative`: Use only collaborative filtering
  - `content`: Use only content-based filtering
- `limit` (integer, optional, default: 10, min: 1, max: 100): Maximum number of recommendations

**Example Request:**

```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/recommendations/personalized?method=hybrid&limit=20"
```

**Response:** `200 OK`

```json
[
  {
    "item_id": "507f1f77bcf86cd799439012",
    "item_type": "movie",
    "title": "The Matrix",
    "name": null,
    "description": "A computer hacker learns about the true nature of reality",
    "recommendation_score": 0.95,
    "recommendation_type": "hybrid",
    "genres": ["action", "sci-fi", "thriller"],
    "tags": ["cyberpunk", "philosophy"],
    "metadata": {...}
  }
]
```

**Error Responses:**
- `400 Bad Request`: Invalid method parameter
- `401 Unauthorized`: Not authenticated
- `500 Internal Server Error`: Error generating recommendations

#### Get Hybrid Recommendations

```http
GET /recommendations/hybrid
```

**Description:** Get hybrid recommendations combining collaborative and content-based filtering with customizable weights.

**Authentication:** Required (Bearer Token or Anonymous)

**Query Parameters:**
- `limit` (integer, optional, default: 10, min: 1, max: 100): Maximum number of recommendations
- `collaborative_weight` (float, optional, default: 0.6, min: 0.0, max: 1.0): Weight for collaborative filtering
- `content_weight` (float, optional, default: 0.4, min: 0.0, max: 1.0): Weight for content-based filtering

**Note:** `collaborative_weight` + `content_weight` must equal 1.0

**Example Request:**

```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/recommendations/hybrid?limit=20&collaborative_weight=0.7&content_weight=0.3"
```

**Response:** `200 OK`

```json
[
  {
    "item_id": "507f1f77bcf86cd799439012",
    "item_type": "movie",
    "title": "The Matrix",
    "recommendation_score": 0.92,
    "recommendation_type": "hybrid",
    ...
  }
]
```

**Error Responses:**
- `400 Bad Request`: Invalid weights (must sum to 1.0)
- `401 Unauthorized`: Not authenticated
- `500 Internal Server Error`: Error generating recommendations

#### Get Popular Recommendations

```http
GET /recommendations/popular
```

**Description:** Get popular items based on ratings. Items are ranked by average rating and number of ratings.

**Authentication:** Not required

**Query Parameters:**
- `item_type` (string, optional): Filter by item type (`movie`, `product`, `book`)
- `category` (string, optional): Filter by category (for products)
- `genre` (string, optional): Filter by genre
- `limit` (integer, optional, default: 10, min: 1, max: 100): Maximum number of recommendations
- `min_ratings` (integer, optional, default: 1, min: 1): Minimum number of ratings required

**Example Request:**

```bash
curl "http://localhost:8000/recommendations/popular?item_type=movie&limit=20&min_ratings=5"
```

**Response:** `200 OK`

```json
[
  {
    "item_id": "507f1f77bcf86cd799439012",
    "item_type": "movie",
    "title": "The Matrix",
    "recommendation_score": 4.8,
    "recommendation_type": "popular",
    "average_rating": 4.8,
    "rating_count": 1250,
    ...
  }
]
```

**Error Responses:**
- `500 Internal Server Error`: Error generating recommendations

#### Get Trending Recommendations

```http
GET /recommendations/trending
```

**Description:** Get trending items based on recent ratings within a specified time period.

**Authentication:** Not required

**Query Parameters:**
- `item_type` (string, optional): Filter by item type (`movie`, `product`, `book`)
- `days` (integer, optional, default: 7, min: 1, max: 30): Number of days to look back
- `limit` (integer, optional, default: 10, min: 1, max: 100): Maximum number of recommendations

**Example Request:**

```bash
curl "http://localhost:8000/recommendations/trending?item_type=book&days=14&limit=15"
```

**Response:** `200 OK`

```json
[
  {
    "item_id": "507f1f77bcf86cd799439014",
    "item_type": "book",
    "title": "1984",
    "recommendation_score": 4.5,
    "recommendation_type": "trending",
    "recent_rating_count": 45,
    ...
  }
]
```

**Error Responses:**
- `500 Internal Server Error`: Error generating recommendations

#### Get Collaborative Recommendations

```http
GET /recommendations/collaborative
```

**Description:** Get recommendations using collaborative filtering based on user similarity.

**Authentication:** Required (Bearer Token or Anonymous)

**Query Parameters:**
- `limit` (integer, optional, default: 10, min: 1, max: 100): Maximum number of recommendations
- `min_similarity` (float, optional, default: 0.3, min: 0.0, max: 1.0): Minimum similarity threshold

**Example Request:**

```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/recommendations/collaborative?limit=20&min_similarity=0.4"
```

**Response:** `200 OK`

```json
[
  {
    "item_id": "507f1f77bcf86cd799439012",
    "item_type": "movie",
    "title": "The Matrix",
    "recommendation_score": 0.88,
    "recommendation_type": "collaborative",
    ...
  }
]
```

**Error Responses:**
- `401 Unauthorized`: Not authenticated
- `500 Internal Server Error`: Error generating recommendations

#### Get Content-Based Recommendations

```http
GET /recommendations/content-based
```

**Description:** Get recommendations using content-based filtering based on item similarity to user's previously rated items.

**Authentication:** Required (Bearer Token or Anonymous)

**Query Parameters:**
- `limit` (integer, optional, default: 10, min: 1, max: 100): Maximum number of recommendations
- `min_similarity` (float, optional, default: 0.3, min: 0.0, max: 1.0): Minimum similarity threshold

**Example Request:**

```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/recommendations/content-based?limit=20&min_similarity=0.5"
```

**Response:** `200 OK`

```json
[
  {
    "item_id": "507f1f77bcf86cd799439012",
    "item_type": "movie",
    "title": "The Matrix",
    "recommendation_score": 0.85,
    "recommendation_type": "content",
    ...
  }
]
```

**Error Responses:**
- `401 Unauthorized`: Not authenticated
- `500 Internal Server Error`: Error generating recommendations

---

## Data Models

### User Models

#### User

```json
{
  "id": "string",
  "email": "string (email)",
  "username": "string",
  "is_active": "boolean",
  "created_at": "datetime (ISO 8601)",
  "is_anonymous": "boolean",
  "preferences": {
    "favorite_genres": ["string"],
    "preferred_item_types": ["string"]
  }
}
```

**Fields:**
- `id` (string, required): Unique user identifier (MongoDB ObjectId)
- `email` (string, required): User email address (valid email format)
- `username` (string, required): Unique username
- `is_active` (boolean, required): Whether the user account is active
- `created_at` (datetime, required): Account creation timestamp
- `is_anonymous` (boolean, optional, default: false): Whether the user is anonymous
- `preferences` (object, optional): User preferences dictionary

#### UserCreate

```json
{
  "email": "string (email)",
  "username": "string",
  "password": "string",
  "preferences": {}
}
```

**Fields:**
- `email` (string, required): Valid email address
- `username` (string, required): Username
- `password` (string, required): User password (min 8 characters recommended)
- `preferences` (object, optional): User preferences dictionary

#### UserUpdate

```json
{
  "username": "string",
  "preferences": {}
}
```

**Fields:**
- `username` (string, optional): New username
- `preferences` (object, optional): Updated preferences dictionary

#### Token

```json
{
  "access_token": "string",
  "token_type": "string"
}
```

**Fields:**
- `access_token` (string, required): JWT access token
- `token_type` (string, required, default: "bearer"): Token type

### Item Models

#### Item

```json
{
  "id": "string",
  "item_type": "movie | product | book",
  "title": "string | null",
  "name": "string | null",
  "description": "string",
  "genres": ["string"],
  "tags": ["string"],
  "metadata": {},
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

**Fields:**
- `id` (string, required): Unique item identifier (MongoDB ObjectId)
- `item_type` (enum, required): Type of item (`movie`, `product`, `book`)
- `title` (string, optional): Item title (for movies and books)
- `name` (string, optional): Item name (for products)
- `description` (string, required): Item description
- `genres` (array of strings, required): List of genres
- `tags` (array of strings, required): List of tags
- `metadata` (object, required): Item-specific metadata
- `created_at` (datetime, required): Creation timestamp
- `updated_at` (datetime, required): Last update timestamp

#### MovieCreate

```json
{
  "title": "string",
  "description": "string",
  "genres": ["string"],
  "tags": ["string"],
  "metadata": {
    "director": "string",
    "cast": ["string"],
    "release_date": "string",
    "poster_url": "string",
    "duration_minutes": "integer"
  }
}
```

#### ProductCreate

```json
{
  "name": "string",
  "category": "string",
  "description": "string",
  "genres": ["string"],
  "tags": ["string"],
  "metadata": {
    "brand": "string",
    "price": "float",
    "image_url": "string",
    "stock": "integer",
    "specifications": {}
  }
}
```

#### BookCreate

```json
{
  "title": "string",
  "description": "string",
  "genres": ["string"],
  "tags": ["string"],
  "metadata": {
    "author": "string",
    "isbn": "string",
    "publication_date": "string",
    "cover_url": "string",
    "pages": "integer",
    "publisher": "string"
  }
}
```

#### ItemUpdate

```json
{
  "description": "string",
  "genres": ["string"],
  "tags": ["string"],
  "metadata": {}
}
```

**Fields:** All fields are optional.

### Rating Models

#### Rating

```json
{
  "id": "string",
  "user_id": "string",
  "item_id": "string",
  "rating": "integer (1-5)",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

**Fields:**
- `id` (string, required): Unique rating identifier (MongoDB ObjectId)
- `user_id` (string, required): User ID who created the rating
- `item_id` (string, required): Item ID being rated
- `rating` (integer, required): Rating value (1-5)
- `created_at` (datetime, required): Creation timestamp
- `updated_at` (datetime, required): Last update timestamp

#### RatingCreate

```json
{
  "item_id": "string",
  "rating": "integer (1-5)"
}
```

#### RatingUpdate

```json
{
  "rating": "integer (1-5)"
}
```

#### UserRating

```json
{
  "id": "string",
  "user_id": "string",
  "item_id": "string",
  "rating": "integer (1-5)",
  "item_title": "string | null",
  "item_name": "string | null",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

**Additional Fields:**
- `item_title` (string, optional): Item title (for movies and books)
- `item_name` (string, optional): Item name (for products)

#### ItemRating

```json
{
  "id": "string",
  "user_id": "string",
  "item_id": "string",
  "rating": "integer (1-5)",
  "username": "string | null",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

**Additional Fields:**
- `username` (string, optional): Username of the user who created the rating

### Recommendation Models

#### Recommendation Response

```json
{
  "item_id": "string",
  "item_type": "movie | product | book",
  "title": "string | null",
  "name": "string | null",
  "description": "string",
  "recommendation_score": "float",
  "recommendation_type": "string",
  "genres": ["string"],
  "tags": ["string"],
  "metadata": {}
}
```

**Fields:**
- `item_id` (string, required): Item ID
- `item_type` (enum, required): Type of item
- `title` (string, optional): Item title
- `name` (string, optional): Item name
- `description` (string, required): Item description
- `recommendation_score` (float, required): Recommendation score (0.0-1.0 or average rating)
- `recommendation_type` (string, required): Type of recommendation (`hybrid`, `collaborative`, `content`, `popular`, `trending`)
- `genres` (array of strings, required): Item genres
- `tags` (array of strings, required): Item tags
- `metadata` (object, required): Item metadata

---

## Error Handling

### Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message or error details"
}
```

### HTTP Status Codes

| Status Code | Description | Common Scenarios |
|------------|-------------|------------------|
| `200 OK` | Request successful | Successful GET, PUT requests |
| `201 Created` | Resource created | Successful POST requests |
| `204 No Content` | Request successful, no content | Successful DELETE requests |
| `400 Bad Request` | Invalid request | Invalid parameters, malformed data |
| `401 Unauthorized` | Authentication required | Missing or invalid token |
| `403 Forbidden` | Access denied | User not authorized for the action |
| `404 Not Found` | Resource not found | Item, user, or rating not found |
| `409 Conflict` | Resource conflict | Email or username already exists |
| `422 Unprocessable Entity` | Validation error | Invalid input data format |
| `500 Internal Server Error` | Server error | Unexpected server errors |

### Common Error Scenarios

#### 400 Bad Request

**Invalid ObjectId:**
```json
{
  "detail": "Invalid item ID"
}
```

**Invalid Rating Value:**
```json
{
  "detail": [
    {
      "loc": ["body", "rating"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

#### 401 Unauthorized

**Missing Token:**
```json
{
  "detail": "Not authenticated"
}
```

**Invalid Token:**
```json
{
  "detail": "Not authenticated"
}
```

#### 403 Forbidden

**Unauthorized Action:**
```json
{
  "detail": "Not authorized to update this rating"
}
```

#### 404 Not Found

**Item Not Found:**
```json
{
  "detail": "Item not found"
}
```

#### 422 Unprocessable Entity

**Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ],
  "body": {
    "email": "invalid-email"
  }
}
```

#### 500 Internal Server Error

**Server Error:**
```json
{
  "detail": "Internal server error: <error message>"
}
```

**Recommendation Error:**
```json
{
  "detail": "Error generating recommendations: <error message>"
}
```

---

## Usage Examples

### Common Use Cases

#### 1. User Registration and Login Flow

```bash
# 1. Register a new user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword123",
    "preferences": {
      "favorite_genres": ["action", "drama"],
      "preferred_item_types": ["movie"]
    }
  }'

# 2. Login to get access token
curl -X POST "http://localhost:8000/auth/login?email=user@example.com&password=securepassword123"

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }

# 3. Use token for authenticated requests
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  "http://localhost:8000/users/me"
```

#### 2. Create and Rate Items

```bash
# 1. Create a movie
curl -X POST "http://localhost:8000/items/movies" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Inception",
    "description": "A thief who steals corporate secrets through dream-sharing technology",
    "genres": ["action", "sci-fi", "thriller"],
    "tags": ["dreams", "heist", "mind-bending"],
    "metadata": {
      "director": "Christopher Nolan",
      "cast": ["Leonardo DiCaprio", "Marion Cotillard", "Tom Hardy"],
      "release_date": "2010-07-16",
      "duration_minutes": 148
    }
  }'

# Response includes item_id: "507f1f77bcf86cd799439016"

# 2. Rate the movie
curl -X POST "http://localhost:8000/ratings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "item_id": "507f1f77bcf86cd799439016",
    "rating": 5
  }'
```

#### 3. Get Personalized Recommendations

```bash
# Get hybrid recommendations (default)
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/recommendations/personalized?method=hybrid&limit=20"

# Get collaborative filtering recommendations
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/recommendations/collaborative?limit=15&min_similarity=0.4"

# Get content-based recommendations
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/recommendations/content-based?limit=15&min_similarity=0.5"
```

#### 4. Browse and Filter Items

```bash
# Get all action movies
curl "http://localhost:8000/items/movies?genre=action&limit=20&skip=0"

# Get products in a specific category
curl "http://localhost:8000/items/products?category=electronics&limit=10"

# Get popular books
curl "http://localhost:8000/recommendations/popular?item_type=book&limit=20&min_ratings=5"
```

#### 5. Update User Profile

```bash
curl -X PUT "http://localhost:8000/users/me" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "username": "newusername",
    "preferences": {
      "favorite_genres": ["action", "comedy", "sci-fi"],
      "preferred_item_types": ["movie", "book"]
    }
  }'
```

### Python Client Examples

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Register and Login
def register_and_login(email, username, password):
    # Register
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password,
            "preferences": {"favorite_genres": ["action", "drama"]}
        }
    )
    print(f"Registration: {response.status_code}")
    
    # Login
    response = requests.post(
        f"{BASE_URL}/auth/login",
        params={"email": email, "password": password}
    )
    token = response.json()["access_token"]
    return token

# 2. Create Movie
def create_movie(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/items/movies",
        json={
            "title": "The Matrix",
            "description": "A computer hacker learns about the true nature of reality",
            "genres": ["action", "sci-fi", "thriller"],
            "tags": ["cyberpunk", "philosophy"],
            "metadata": {
                "director": "Lana Wachowski, Lilly Wachowski",
                "cast": ["Keanu Reeves", "Laurence Fishburne"],
                "release_date": "1999-03-31",
                "duration_minutes": 136
            }
        },
        headers=headers
    )
    return response.json()

# 3. Rate Item
def rate_item(token, item_id, rating):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/ratings",
        json={"item_id": item_id, "rating": rating},
        headers=headers
    )
    return response.json()

# 4. Get Recommendations
def get_recommendations(token, method="hybrid", limit=10):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/recommendations/personalized",
        params={"method": method, "limit": limit},
        headers=headers
    )
    return response.json()

# Usage
token = register_and_login("user@example.com", "johndoe", "password123")
movie = create_movie(token)
rate_item(token, movie["id"], 5)
recommendations = get_recommendations(token, method="hybrid", limit=20)
print(recommendations)
```

### JavaScript/TypeScript Client Examples

```typescript
const BASE_URL = "http://localhost:8000";

// 1. Register and Login
async function registerAndLogin(email: string, username: string, password: string): Promise<string> {
  // Register
  await fetch(`${BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email,
      username,
      password,
      preferences: { favorite_genres: ["action", "drama"] }
    })
  });

  // Login
  const loginResponse = await fetch(
    `${BASE_URL}/auth/login?email=${email}&password=${password}`,
    { method: "POST" }
  );
  const { access_token } = await loginResponse.json();
  return access_token;
}

// 2. Create Movie
async function createMovie(token: string) {
  const response = await fetch(`${BASE_URL}/items/movies`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({
      title: "The Matrix",
      description: "A computer hacker learns about the true nature of reality",
      genres: ["action", "sci-fi", "thriller"],
      tags: ["cyberpunk", "philosophy"],
      metadata: {
        director: "Lana Wachowski, Lilly Wachowski",
        cast: ["Keanu Reeves", "Laurence Fishburne"],
        release_date: "1999-03-31",
        duration_minutes: 136
      }
    })
  });
  return await response.json();
}

// 3. Rate Item
async function rateItem(token: string, itemId: string, rating: number) {
  const response = await fetch(`${BASE_URL}/ratings`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ item_id: itemId, rating })
  });
  return await response.json();
}

// 4. Get Recommendations
async function getRecommendations(token: string, method: string = "hybrid", limit: number = 10) {
  const response = await fetch(
    `${BASE_URL}/recommendations/personalized?method=${method}&limit=${limit}`,
    {
      headers: { "Authorization": `Bearer ${token}` }
    }
  );
  return await response.json();
}

// Usage
(async () => {
  const token = await registerAndLogin("user@example.com", "johndoe", "password123");
  const movie = await createMovie(token);
  await rateItem(token, movie.id, 5);
  const recommendations = await getRecommendations(token, "hybrid", 20);
  console.log(recommendations);
})();
```

### Error Handling Examples

```python
import requests

def safe_api_call(url, method="GET", **kwargs):
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()  # Raises an exception for bad status codes
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            print("Authentication required. Please login.")
        elif response.status_code == 404:
            print("Resource not found.")
        elif response.status_code == 400:
            error_detail = response.json().get("detail", "Bad request")
            print(f"Bad request: {error_detail}")
        else:
            print(f"HTTP Error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Usage with error handling
token = "your-token"
result = safe_api_call(
    f"{BASE_URL}/recommendations/personalized",
    headers={"Authorization": f"Bearer {token}"},
    params={"method": "hybrid", "limit": 10}
)
if result:
    print(result)
```

---

## Additional Notes

### Anonymous Users

The API supports anonymous users for read-only operations. When a request is made without authentication or with an invalid token, an anonymous user is automatically created. This allows:

- Browsing items
- Viewing ratings
- Getting popular/trending recommendations
- Accessing public endpoints

Anonymous users cannot:
- Create ratings (they can but will be associated with anonymous user)
- Update their profile
- Access certain personalized features

### Recommendation Algorithms

The API uses multiple recommendation strategies:

1. **Collaborative Filtering**: Finds users with similar preferences and recommends items they liked
2. **Content-Based Filtering**: Recommends items similar to those the user has previously rated
3. **Hybrid Approach**: Combines collaborative and content-based filtering with customizable weights
4. **Popular Items**: Ranks items by average rating and number of ratings
5. **Trending Items**: Identifies items with recent high activity

### Best Practices

1. **Token Management**: Store tokens securely and refresh before expiration
2. **Error Handling**: Always implement proper error handling for API calls
3. **Rate Limiting**: Be mindful of API usage (rate limiting may be implemented in production)
4. **Pagination**: Use `skip` and `limit` parameters for large result sets
5. **Filtering**: Use appropriate filters (`genre`, `category`, `item_type`) to reduce response sizes
6. **Validation**: Validate data on the client side before sending requests

### Database

The API uses MongoDB for data storage. All IDs are MongoDB ObjectIds converted to strings.

### Environment Variables

Required environment variables (configure in `.env` file):

```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=recommendation_db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Support

For issues, questions, or contributions, please refer to the project repository or contact the development team.

---

**Document Version:** 1.0.0  
**Last Updated:** 2024-01-15  
**API Version:** 1.0.0


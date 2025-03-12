Below is the final, polished architectural document for the News Aggregator project. This document is formatted in Markdown and serves as the "architect's guide" to the entire system. It explains the overall project structure, describes the purpose of each file and directory, and details the flow of data throughout the system.

# NewsFeast Project Architecture

This document provides an overview of the system architecture for the NewsFeast project. It describes each layer and component, explains how the files are connected, and outlines the overall data flow. Detailed diagrams and further documentation will be added as the project evolves.

## System Overview
- **Data Ingestion & Integration Layer:**
  Scrapers, API connectors, and RSS readers collect raw news data from diverse sources.
- **Data Processing & Storage Layer:**
  Data cleaning, deduplication, and storage configuration ensure that raw input is normalized and reliably stored.
- **Summarization & Story Tracking Engine:**
  LLM-based summarization generates concise news summaries, while NLP techniques cluster articles to track evolving stories.
- **Backend & API Layer:**
  Microservices encapsulate business logic, an API gateway exposes these services via REST, and real-time communication delivers live updates.
- **Frontend & User Experience:**
  Web and mobile interfaces present the aggregated, summarized news content in an engaging, user-friendly manner.
- **Monitoring, DevOps & Analytics:**
  CI/CD pipelines, logging configurations, and container orchestration (via Docker and Kubernetes) ensure scalable, reliable, and observable deployments.

## System Architecture Diagrams

### High-Level System Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  News Sources   │────▶│  Data Ingestion │────▶│ Data Processing │
│  (APIs, RSS)    │     │     Layer       │     │     Layer       │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│    Frontend     │◀───▶│   API Gateway   │◀───▶│    Database     │
│     Layer       │     │                 │     │   (Supabase)    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │
                  ┌─────────────┴─────────────┐
                  │                           │
        ┌─────────▼────────┐        ┌─────────▼────────┐
        │                  │        │                  │
        │  Summarization   │        │  Story Tracking  │
        │     Service      │        │     Service      │
        │                  │        │                  │
        └──────────────────┘        └──────────────────┘
```

### Component Interaction Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend Application                        │
└───────────────┬─────────────────────────────────────────────────┘
                │
                │ HTTP/REST
                │
┌───────────────▼─────────────────────────────────────────────────┐
│                         API Gateway                             │
└───┬─────────────┬──────────────────┬───────────────┬────────────┘
    │             │                  │               │
    │             │                  │               │
┌───▼────┐   ┌────▼───┐   ┌─────────▼───────┐   ┌───▼───────────┐
│ Auth    │   │ News   │   │ Summarization  │   │ Story Tracking│
│ Service │   │ Service│   │ Service        │   │ Service       │
└─────────┘   └────────┘   └─────────────────┘   └───────────────┘
```

## Overall Project Structure

The following tree illustrates the complete file structure of the project with inline comments explaining the purpose of each file or directory:

```
news-aggregator/
├── .env                      # Environment variables (sensitive configuration: DB credentials, API keys, etc.)
├── Dockerfile                # Container build configuration for backend services
├── Makefile                  # Common commands (run server, tests, Docker build, etc.)
├── README.md                 # High-level project overview, setup instructions, and usage guidelines
├── requirements.txt          # List of Python dependencies for the project
├── start-polling-worker.sh   # Script to start the polling worker for story tracking
├── start-services.sh         # Script to start all backend services
├── docs/
│   ├── architecture.md       # Detailed documentation of the system architecture
│   ├── Steps.md              # Project roadmap and implementation steps
│   └── story-tracking-documentation.md # Documentation for the story tracking feature
├── backend/                  # Backend & API Layer
│   ├── api_gateway/          # Single entry point exposing REST endpoints for clients
│   │   ├── API_Documentation.md # API documentation
│   │   ├── api_gateway.py    # Flask-based API gateway that routes requests to microservices
│   │   ├── routes/           # API route definitions
│   │   │   ├── auth.py       # Authentication routes
│   │   │   ├── bookmark.py   # Bookmark management routes
│   │   │   ├── health.py     # Health check endpoint
│   │   │   ├── news.py       # News fetching and processing routes
│   │   │   ├── story_tracking.py # Story tracking operation routes
│   │   │   ├── summarize.py  # Summarization routes
│   │   │   └── user.py       # User profile management routes
│   │   └── utils/            # Utilities for the API gateway
│   │       ├── auth.py       # Authentication utilities
│   │       └── ...           # Other utility modules
│   ├── core/                 # Core configuration and utilities
│   │   ├── config.py         # Configuration settings for the application
│   │   └── utils.py          # Common utility functions shared across services
│   ├── data/                 # Data schemas and sample data
│   │   ├── story_tracking_schema.sql # SQL schema for story tracking tables
│   │   └── users.txt         # Sample user data
│   └── microservices/        # Microservices implementing distinct business logic
│       ├── auth_service.py   # Handles user authentication and authorization
│       ├── ingestion_service.py # Orchestrates data ingestion from various sources
│       ├── news_fetcher.py   # Compatibility module redirecting to data_services.news_fetcher
│       ├── news_storage.py   # Handles storage of news articles
│       ├── polling_worker.py # Background worker that checks for stories due for polling
│       ├── story_tracking_service.py # Manages story tracking functionality
│       ├── summarization_service.py # Provides article summarization functionality
│       ├── data_services/    # Services for data acquisition
│       │   ├── news_fetcher.py # Fetches news articles from external sources
│       │   └── ...           # Other data service modules
│       ├── storage/          # Data storage modules
│       │   └── ...           # Storage service implementations
│       ├── story_tracking/   # Story tracking components
│       │   ├── article_matcher.py # Finds related articles for a story
│       │   ├── polling_service.py # Handles polling for story updates
│       │   └── ...           # Other story tracking modules
│       └── summarization/    # Summarization components
│           ├── article_processor.py # Processes articles for summarization
│           ├── content_fetcher.py # Fetches article content
│           └── ...           # Other summarization modules
└── monitoring/               # Monitoring, DevOps & Analytics
    ├── autoscaling/
    │   └── news_aggregator_deployment.yaml  # Kubernetes deployment manifest
    └── logging/
        └── log_config.yml    # YAML configuration for logging across the project

news-aggregator-frontend/     # Frontend application
├── index.html                # Main HTML entry point
├── package.json              # NPM dependencies and scripts
├── tsconfig.json             # TypeScript configuration
├── vite.config.ts            # Vite build configuration
├── docs/                     # Frontend documentation
│   ├── architecture.md       # Frontend architecture documentation
│   ├── feature-specifications.md # Feature specifications
│   └── story-tracking/       # Story tracking feature documentation
│       └── technical-specification.md # Technical details of story tracking feature
├── public/                   # Static assets
├── src/                      # Source code for the React application
│   ├── App.tsx               # Main application component
│   ├── main.tsx              # Application entry point
│   ├── components/           # React components
│   │   ├── ArticleView.tsx   # Article viewing component
│   │   ├── LandingPage.tsx   # Landing page component
│   │   ├── NewsCard.tsx      # News card component
│   │   ├── auth/             # Authentication components
│   │   ├── common/           # Common UI components
│   │   ├── layout/           # Layout components
│   │   ├── news/             # News display components
│   │   ├── story-tracking/   # Story tracking components
│   │   └── ui/               # UI components
│   ├── context/              # React context providers
│   │   ├── AuthContext.tsx   # Authentication context
│   │   ├── NewsContext.tsx   # News data context
│   │   ├── PollingContext.tsx # Polling management context
│   │   └── StoryTrackingContext.tsx # Story tracking context
│   ├── lib/                  # Utility libraries
│   │   ├── supabase.ts       # Supabase client configuration
│   │   └── utils.ts          # Utility functions
│   ├── pages/                # Page components
│   │   ├── AuthPage.tsx      # Authentication page
│   │   ├── BookmarksPage.tsx # Bookmarks management page
│   │   ├── NewsApp.tsx       # Main news application page
│   │   ├── ProfilePage.tsx   # User profile page
│   │   └── StoryTrackingPage.tsx # Story tracking page
│   └── services/             # API service clients
│       ├── bookmarkService.ts # Bookmark API client
│       ├── sessionService.ts  # Session management service
│       └── storyTrackingService.ts # Story tracking API client
└── startscripts/             # Scripts for starting the application
    ├── start-backend.sh      # Script to start the backend
    ├── start-frontend.sh     # Script to start the frontend
    └── start.sh              # Script to start both backend and frontend
```

## Detailed File Descriptions & Data Flow

### 1. Root-Level Files
- **Dockerfile**
  - Purpose: Defines how to package backend services into containers.
  - Usage: Used for building a deployable container image.
- **Makefile**
  - Purpose: Provides simple commands to run the project (e.g., starting the API gateway, running tests, building Docker images).
  - Usage: Developers can execute commands like `make run` or `make test` to perform common tasks.
- **README.md**
  - Purpose: Offers an overview of the project, architectural details, setup instructions, and usage guidelines.
  - Usage: Serves as the primary reference document for both developers and end-users.
- **requirements.txt**
  - Purpose: Lists all Python dependencies required by the project.
  - Usage: Ensures consistency in the development, testing, and production environments.
- **start-polling-worker.sh**
  - Purpose: Script to start the background polling worker for story tracking.
  - Usage: Starts the polling worker that checks for stories due for updates.
- **start-services.sh**
  - Purpose: Script to start all backend services.
  - Usage: Starts the API gateway and polling worker in the proper sequence.

### 2. Backend & API Layer
- **backend/api_gateway/api_gateway.py**
  - Purpose: Provides a unified REST interface (using Flask) to route client requests to the appropriate microservice.
  - Usage: Exposes endpoints so that external clients can interact with backend services.
- **backend/api_gateway/routes/**
  - Purpose: Contains route definitions for different API endpoints.
  - Usage: Organizes API endpoints by functionality (auth, news, bookmarks, etc.).
- **backend/core/config.py**
  - Purpose: Contains configuration parameters for the application.
  - Usage: Modules refer to these settings for configuration values.
- **backend/core/utils.py**
  - Purpose: Provides common utility functions used throughout the application.
  - Usage: Shared functions like logging setup, error handling, etc.
- **backend/microservices/auth_service.py**
  - Purpose: Handles user authentication and authorization.
  - Usage: Validates user credentials and issues JWT tokens.
- **backend/microservices/news_fetcher.py**
  - Purpose: Compatibility module that redirects to the news_fetcher in data_services.
  - Usage: Maintains backward compatibility for existing code.
- **backend/microservices/news_storage.py**
  - Purpose: Handles storage of news articles in the database.
  - Usage: Stores and retrieves news articles from Supabase.
- **backend/microservices/polling_worker.py**
  - Purpose: Background worker that periodically checks for stories that need updates.
  - Usage: Fetches new articles for tracked stories and updates the database.
- **backend/microservices/story_tracking_service.py**
  - Purpose: Manages story tracking functionality.
  - Usage: Creates, updates, and retrieves tracked stories.
- **backend/microservices/summarization_service.py**
  - Purpose: Provides article summarization functionality.
  - Usage: Generates summaries on demand for articles using LLM models.
- **backend/microservices/data_services/news_fetcher.py**
  - Purpose: Fetches news articles from external sources like News API.
  - Usage: Retrieves articles based on keywords and manages storage.

### 3. Summarization & Story Tracking Components
- **backend/microservices/summarization/article_processor.py**
  - Purpose: Processes articles for summarization.
  - Usage: Extracts content, generates summaries, and stores results.
- **backend/microservices/summarization/content_fetcher.py**
  - Purpose: Fetches article content from URLs.
  - Usage: Extracts the main content from article web pages.
- **backend/microservices/summarization/keyword_extractor.py**
  - Purpose: Extracts keywords from article text.
  - Usage: Identifies important keywords for better article matching.
- **backend/microservices/story_tracking/article_matcher.py**
  - Purpose: Finds related articles for a tracked story.
  - Usage: Matches new articles to existing stories based on content similarity.
- **backend/microservices/story_tracking/polling_service.py**
  - Purpose: Handles polling for story updates.
  - Usage: Controls when stories are due for polling and updates.

### 4. Frontend & User Experience Layer
- **news-aggregator-frontend/index.html**
  - Purpose: Serves as the main entry point for the web interface.
  - Usage: Loads the page structure and includes references to JavaScript files.
- **news-aggregator-frontend/src/App.tsx**
  - Purpose: Main application component that sets up routing and layout.
  - Usage: Defines the overall structure of the React application.
- **news-aggregator-frontend/src/components/**
  - Purpose: Contains reusable React components.
  - Usage: Building blocks for creating the user interface.
- **news-aggregator-frontend/src/context/**
  - Purpose: React context providers for state management.
  - Usage: Manages application state like authentication, news data, and story tracking.
- **news-aggregator-frontend/src/pages/**
  - Purpose: Page components that represent different views of the application.
  - Usage: Defines the UI and behavior for each page in the app.
- **news-aggregator-frontend/src/services/**
  - Purpose: API service clients to communicate with the backend.
  - Usage: Makes HTTP requests to the API gateway for data operations.

### 5. Monitoring & DevOps
- **monitoring/autoscaling/news_aggregator_deployment.yaml**
  - Purpose: A Kubernetes deployment manifest.
  - Usage: Facilitates load balancing and auto-scaling in a production environment.
- **monitoring/logging/log_config.yml**
  - Purpose: Provides a standardized logging configuration.
  - Usage: Ensures consistent log output for debugging and monitoring.

## Database Schema

### Main Tables

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    name TEXT,
    preferences JSONB DEFAULT '{}'::jsonb
);
```

#### Articles Table
```sql
CREATE TABLE articles (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    source TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    author TEXT,
    content TEXT,
    summary TEXT,
    keywords TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    image_url TEXT
);
```

#### Stories Table
```sql
CREATE TABLE stories (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status TEXT DEFAULT 'active',
    keywords TEXT[],
    last_polled_at TIMESTAMP WITH TIME ZONE,
    poll_frequency_hours INTEGER DEFAULT 24
);
```

#### Story Articles Table
```sql
CREATE TABLE story_articles (
    story_id UUID REFERENCES stories(id),
    article_id UUID REFERENCES articles(id),
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (story_id, article_id)
);
```

#### Bookmarks Table
```sql
CREATE TABLE bookmarks (
    user_id UUID REFERENCES users(id),
    article_id UUID REFERENCES articles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,
    PRIMARY KEY (user_id, article_id)
);
```

### Entity Relationship Diagram
```
┌─────────┐     ┌───────────┐     ┌─────────┐
│         │     │           │     │         │
│  Users  │◀───▶│ Bookmarks │◀───▶│Articles │
│         │     │           │     │         │
└─────────┘     └───────────┘     └────┬────┘
                                       │
                                       │
                                  ┌────▼────┐     ┌────────┐
                                  │         │     │        │
                                  │Story    │◀───▶│Stories │
                                  │Articles │     │        │
                                  │         │     │        │
                                  └─────────┘     └────────┘
```

## API Specifications

The NewsFeast application exposes a comprehensive REST API through its API Gateway. The following sections document all available endpoints, organized by functionality.

### API Versioning Policy
- **Versioning Strategy**: All endpoints are versioned using a URL prefix (e.g., `/api/v1/...`).
- **Backward Compatibility**: Deprecated endpoints will be supported for at least one major version release.
- **Deprecation Policy**: Deprecated endpoints will return a warning header and will be removed in the next major release.

### WebSocket/Real-time API Documentation

#### WebSocket Connection
- **URL**: `wss://api.newsfeast.com/realtime`
- **Authentication**: JWT token must be provided in the connection query parameters.
- **Message Format**: JSON

#### Events
- **`story_update`**: Notifies clients of updates to tracked stories.
  ```json
  {
    "event": "story_update",
    "data": {
      "story_id": "uuid",
      "title": "Updated Story Title",
      "updated_at": "2023-05-15T14:30:00Z"
    }
  }
  ```
- **`new_article`**: Notifies clients of new articles added to a story.
  ```json
  {
    "event": "new_article",
    "data": {
      "story_id": "uuid",
      "article": {
        "id": "uuid",
        "title": "New Article Title",
        "url": "https://example.com/article",
        "published_at": "2023-05-15T10:30:00Z"
      }
    }
  }
  ```

### Error Handling Standards

#### Error Response Format
All error responses follow a standard format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "status": 400,
    "message": "Error message",
    "details": "Additional error details"
  }
}
```

#### Common Error Codes
- `INVALID_REQUEST`: The request parameters are invalid.
- `UNAUTHORIZED`: Authentication is required and has failed or has not been provided.
- `FORBIDDEN`: The user does not have permission to perform this action.
- `NOT_FOUND`: The requested resource could not be found.
- `INTERNAL_SERVER_ERROR`: An unexpected error occurred on the server.

### Search & Filtering Parameters

#### GET /api/news
- **Description**: Fetches news articles with optional filtering
- **Query Parameters**: 
  - `q`: Search query (supports AND, OR, NOT operators)
  - `category`: News category
  - `source`: News source
  - `from`: Start date for articles (ISO 8601 format)
  - `to`: End date for articles (ISO 8601 format)
  - `sort`: Sort field (e.g., `published_at`)
  - `order`: Sort order (`asc` or `desc`)
  - `page`: Page number (default: 1)
  - `pageSize`: Number of results per page (default: 10)
- **Response**: 
  ```json
  {
    "articles": [
      {
        "id": "uuid",
        "title": "Article title",
        "url": "https://example.com/article",
        "source": "Source Name",
        "published_at": "2023-05-15T10:30:00Z",
        "author": "Author Name",
        "summary": "Brief summary of the article",
        "image_url": "https://example.com/image.jpg"
      }
    ],
    "total": 100,
    "page": 1,
    "pageSize": 10
  }
  ```

### Analytics Endpoints

#### GET /api/analytics/user-activity
- **Description**: Fetches user activity analytics
- **Headers**: Authorization: Bearer {admin_token}
- **Query Parameters**: 
  - `from`: Start date for analytics (ISO 8601 format)
  - `to`: End date for analytics (ISO 8601 format)
- **Response**: 
  ```json
  {
    "total_users": 1500,
    "active_users": 300,
    "new_users": 50,
    "user_activity": [
      {
        "date": "2023-05-15",
        "active_users": 300,
        "new_users": 50
      }
    ]
  }
  ```

#### GET /api/analytics/article-engagement
- **Description**: Fetches article engagement analytics
- **Headers**: Authorization: Bearer {admin_token}
- **Query Parameters**: 
  - `from`: Start date for analytics (ISO 8601 format)
  - `to`: End date for analytics (ISO 8601 format)
- **Response**: 
  ```json
  {
    "total_articles": 5000,
    "total_views": 20000,
    "total_bookmarks": 1500,
    "article_engagement": [
      {
        "article_id": "uuid",
        "title": "Article title",
        "views": 100,
        "bookmarks": 10
      }
    ]
  }
  ```

### Additional Story Tracking Endpoints

#### POST /api/story_tracking/start
- **Description**: Starts polling for story updates
- **Headers**: Authorization: Bearer {admin_token}
- **Response**: 
  ```json
  {
    "message": "Polling started successfully"
  }
  ```

#### POST /api/story_tracking/stop
- **Description**: Stops polling for story updates
- **Headers**: Authorization: Bearer {admin_token}
- **Response**: 
  ```json
  {
    "message": "Polling stopped successfully"
  }
  ```

### External Service Integration APIs

#### POST /api/integrations/webhooks
- **Description**: Configures a new webhook for external service integration
- **Headers**: Authorization: Bearer {admin_token}
- **Request Body**: 
  ```json
  {
    "url": "https://example.com/webhook",
    "events": ["story_update", "new_article"]
  }
  ```
- **Response**: 
  ```json
  {
    "id": "uuid",
    "url": "https://example.com/webhook",
    "events": ["story_update", "new_article"],
    "created_at": "2023-05-15T10:30:00Z"
  }
  ```

#### GET /api/integrations/webhooks
- **Description**: Fetches all configured webhooks
- **Headers**: Authorization: Bearer {admin_token}
- **Response**: 
  ```json
  {
    "webhooks": [
      {
        "id": "uuid",
        "url": "https://example.com/webhook",
        "events": ["story_update", "new_article"],
        "created_at": "2023-05-15T10:30:00Z"
      }
    ]
  }
  ```

#### DELETE /api/integrations/webhooks/{webhook_id}
- **Description**: Deletes a configured webhook
- **Headers**: Authorization: Bearer {admin_token}
- **Response**: 
  ```json
  {
    "message": "Webhook deleted successfully"
  }
  ```

### Authentication Endpoints

#### POST /api/auth/register
- **Description**: Registers a new user
- **Request Body**: 
  ```json
  {
    "email": "user@example.com",
    "password": "securePassword123",
    "name": "John Doe"
  }
  ```
- **Response**: 
  ```json
  {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "token": "jwt-token"
  }
  ```

#### POST /api/auth/login
- **Description**: Authenticates a user
- **Request Body**: 
  ```json
  {
    "email": "user@example.com",
    "password": "securePassword123"
  }
  ```
- **Response**: 
  ```json
  {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "token": "jwt-token"
  }
  ```

#### POST /api/auth/logout
- **Description**: Logs out a user
- **Headers**: Authorization: Bearer {token}
- **Response**: 
  ```json
  {
    "message": "Successfully logged out"
  }
  ```

#### GET /api/auth/me
- **Description**: Returns the current user's profile
- **Headers**: Authorization: Bearer {token}
- **Response**: 
  ```json
  {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "preferences": {}
  }
  ```

### User Management Endpoints

#### GET /api/user/profile
- **Description**: Gets the user's profile
- **Headers**: Authorization: Bearer {token}
- **Response**: 
  ```json
  {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2023-05-15T10:30:00Z",
    "preferences": {
      "favorite_categories": ["technology", "politics"],
      "theme": "dark"
    }
  }
  ```

#### PUT /api/user/profile
- **Description**: Updates the user's profile
- **Headers**: Authorization: Bearer {token}
- **Request Body**: 
  ```json
  {
    "name": "John Smith",
    "preferences": {
      "favorite_categories": ["science", "politics"],
      "theme": "light"
    }
  }
  ```
- **Response**: 
  ```json
  {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Smith",
    "preferences": {
      "favorite_categories": ["science", "politics"],
      "theme": "light"
    }
  }
  ```

### News Endpoints

#### GET /api/news
- **Description**: Fetches news articles with optional filtering
- **Query Parameters**: 
  - `q`: Search query (supports AND, OR, NOT operators)
  - `category`: News category
  - `source`: News source
  - `from`: Start date for articles (ISO 8601 format)
  - `to`: End date for articles (ISO 8601 format)
  - `sort`: Sort field (e.g., `published_at`)
  - `order`: Sort order (`asc` or `desc`)
  - `page`: Page number (default: 1)
  - `pageSize`: Number of results per page (default: 10)
- **Response**: 
  ```json
  {
    "articles": [
      {
        "id": "uuid",
        "title": "Article title",
        "url": "https://example.com/article",
        "source": "Source Name",
        "published_at": "2023-05-15T10:30:00Z",
        "author": "Author Name",
        "summary": "Brief summary of the article",
        "image_url": "https://example.com/image.jpg"
      }
    ],
    "total": 100,
    "page": 1,
    "pageSize": 10
  }
  ```

#### GET /api/news/{article_id}
- **Description**: Fetches a specific news article by ID
- **Response**: 
  ```json
  {
    "id": "uuid",
    "title": "Article title",
    "url": "https://example.com/article",
    "source": "Source Name",
    "published_at": "2023-05-15T10:30:00Z",
    "author": "Author Name",
    "content": "Full content of the article",
    "summary": "Brief summary of the article",
    "keywords": ["keyword1", "keyword2"],
    "image_url": "https://example.com/image.jpg"
  }
  ```

#### GET /api/news/categories
- **Description**: Fetches available news categories
- **Response**: 
  ```json
  {
    "categories": ["business", "entertainment", "general", "health", "science", "sports", "technology"]
  }
  ```

#### GET /api/news/sources
- **Description**: Fetches available news sources
- **Response**: 
  ```json
  {
    "sources": [
      {
        "id": "source-id",
        "name": "Source Name",
        "description": "Source description",
        "category": "technology"
      }
    ]
  }
  ```

### Summarization Endpoints

#### POST /api/summarize/url
- **Description**: Generates a summary for a provided URL
- **Headers**: Authorization: Bearer {token}
- **Request Body**: 
  ```json
  {
    "url": "https://example.com/article"
  }
  ```
- **Response**: 
  ```json
  {
    "original_url": "https://example.com/article",
    "title": "Original article title",
    "summary": "Generated summary of the article content",
    "keywords": ["keyword1", "keyword2"],
    "processing_time_ms": 1200
  }
  ```

#### POST /api/summarize/text
- **Description**: Generates a summary for provided text content
- **Headers**: Authorization: Bearer {token}
- **Request Body**: 
  ```json
  {
    "title": "Article title",
    "text": "Full article content to summarize"
  }
  ```
- **Response**: 
  ```json
  {
    "title": "Article title",
    "summary": "Generated summary of the article content",
    "keywords": ["keyword1", "keyword2"],
    "processing_time_ms": 800
  }
  ```

### Story Tracking Endpoints

#### GET /api/stories
- **Description**: Fetches all tracked stories for the current user
- **Headers**: Authorization: Bearer {token}
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `pageSize`: Number of results per page (default: 10)
- **Response**: 
  ```json
  {
    "stories": [
      {
        "id": "uuid",
        "title": "Story Title",
        "created_at": "2023-05-15T10:30:00Z",
        "updated_at": "2023-05-15T14:30:00Z",
        "status": "active",
        "keywords": ["keyword1", "keyword2"],
        "article_count": 5,
        "last_polled_at": "2023-05-15T14:30:00Z",
        "poll_frequency_hours": 24
      }
    ],
    "total": 15,
    "page": 1,
    "pageSize": 10
  }
  ```

#### GET /api/stories/{story_id}
- **Description**: Fetches a specific story by ID
- **Headers**: Authorization: Bearer {token}
- **Response**: 
  ```json
  {
    "id": "uuid",
    "title": "Story Title",
    "created_at": "2023-05-15T10:30:00Z",
    "updated_at": "2023-05-15T14:30:00Z",
    "status": "active",
    "keywords": ["keyword1", "keyword2"],
    "poll_frequency_hours": 24,
    "last_polled_at": "2023-05-15T14:30:00Z",
    "articles": [
      {
        "id": "uuid",
        "title": "Article title",
        "url": "https://example.com/article",
        "source": "Source Name",
        "published_at": "2023-05-15T10:30:00Z",
        "summary": "Brief summary of the article",
        "image_url": "https://example.com/image.jpg"
      }
    ]
  }
  ```

#### POST /api/stories
- **Description**: Creates a new tracked story
- **Headers**: Authorization: Bearer {token}
- **Request Body**: 
  ```json
  {
    "title": "Story Title",
    "keywords": ["keyword1", "keyword2"],
    "poll_frequency_hours": 24
  }
  ```
- **Response**: 
  ```json
  {
    "id": "uuid",
    "title": "Story Title",
    "created_at": "2023-05-15T10:30:00Z",
    "keywords": ["keyword1", "keyword2"],
    "poll_frequency_hours": 24,
    "status": "active"
  }
  ```

#### PUT /api/stories/{story_id}
- **Description**: Updates an existing story
- **Headers**: Authorization: Bearer {token}
- **Request Body**: 
  ```json
  {
    "title": "Updated Story Title",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "poll_frequency_hours": 12,
    "status": "active"
  }
  ```
- **Response**: 
  ```json
  {
    "id": "uuid",
    "title": "Updated Story Title",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "poll_frequency_hours": 12,
    "status": "active",
    "updated_at": "2023-05-16T10:30:00Z"
  }
  ```

#### DELETE /api/stories/{story_id}
- **Description**: Deletes a story
- **Headers**: Authorization: Bearer {token}
- **Response**: 
  ```json
  {
    "message": "Story deleted successfully"
  }
  ```

#### POST /api/stories/{story_id}/poll
- **Description**: Manually triggers polling for new articles for a story
- **Headers**: Authorization: Bearer {token}
- **Response**: 
  ```json
  {
    "message": "Story polling initiated",
    "job_id": "uuid",
    "estimated_completion_time": "2023-05-15T10:35:00Z"
  }
  ```

#### GET /api/stories/{story_id}/articles
- **Description**: Gets all articles associated with a story
- **Headers**: Authorization: Bearer {token}
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `pageSize`: Number of results per page (default: 10)
  - `sort`: Sort field (default: "published_at")
  - `order`: Sort order (default: "desc")
- **Response**: 
  ```json
  {
    "story_id": "uuid",
    "articles": [
      {
        "id": "uuid",
        "title": "Article title",
        "url": "https://example.com/article",
        "source": "Source Name",
        "published_at": "2023-05-15T10:30:00Z",
        "added_at": "2023-05-15T11:00:00Z",
        "summary": "Brief summary of the article",
        "image_url": "https://example.com/image.jpg"
      }
    ],
    "total": 25,
    "page": 1,
    "pageSize": 10
  }
  ```

### Bookmark Endpoints

#### GET /api/bookmarks
- **Description**: Fetches all bookmarks for the current user
- **Headers**: Authorization: Bearer {token}
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `pageSize`: Number of results per page (default: 10)
- **Response**: 
  ```json
  {
    "bookmarks": [
      {
        "id": "uuid",
        "article_id": "uuid",
        "title": "Article title",
        "url": "https://example.com/article",
        "created_at": "2023-05-15T10:30:00Z",
        "notes": "User's notes about this article",
        "summary": "Brief summary of the article",
        "image_url": "https://example.com/image.jpg"
      }
    ],
    "total": 42,
    "page": 1,
    "pageSize": 10
  }
  ```

#### POST /api/bookmarks
- **Description**: Creates a new bookmark
- **Headers**: Authorization: Bearer {token}
- **Request Body**: 
  ```json
  {
    "article_id": "uuid",
    "notes": "Optional notes about this bookmark"
  }
  ```
- **Response**: 
  ```json
  {
    "id": "uuid",
    "article_id": "uuid",
    "created_at": "2023-05-15T10:30:00Z",
    "notes": "Optional notes about this bookmark"
  }
  ```

#### PUT /api/bookmarks/{bookmark_id}
- **Description**: Updates a bookmark's notes
- **Headers**: Authorization: Bearer {token}
- **Request Body**: 
  ```json
  {
    "notes": "Updated notes for this bookmark"
  }
  ```
- **Response**: 
  ```json
  {
    "id": "uuid",
    "article_id": "uuid",
    "notes": "Updated notes for this bookmark",
    "updated_at": "2023-05-15T11:30:00Z"
  }
  ```

#### DELETE /api/bookmarks/{bookmark_id}
- **Description**: Deletes a bookmark
- **Headers**: Authorization: Bearer {token}
- **Response**: 
  ```json
  {
    "message": "Bookmark deleted successfully"
  }
  ```

### Health & Monitoring Endpoints

#### GET /api/health
- **Description**: Checks the health of the API and its dependencies
- **Response**: 
  ```json
  {
    "status": "healthy",
    "version": "1.0.0",
    "dependencies": {
      "database": "connected",
      "news_api": "available",
      "summarization_service": "available"
    },
    "timestamp": "2023-05-15T10:30:00Z"
  }
  ```

#### GET /api/health/detailed
- **Description**: Returns detailed health metrics (admin only)
- **Headers**: Authorization: Bearer {admin_token}
- **Response**: 
  ```json
  {
    "status": "healthy",
    "version": "1.0.0",
    "uptime_seconds": 86400,
    "memory_usage_mb": 256,
    "api_requests_last_hour": 1250,
    "average_response_time_ms": 120,
    "dependencies": {
      "database": {
        "status": "connected",
        "latency_ms": 3,
        "connections_open": 5
      },
      "news_api": {
        "status": "available",
        "rate_limit_remaining": 980,
        "rate_limit_reset_at": "2023-05-15T11:00:00Z"
      },
      "summarization_service": {
        "status": "available",
        "queue_length": 0,
        "processing_time_avg_ms": 850
      }
    }
  }
  ```

## Technical Decision Records

### TDR-001: Using Supabase for Backend Storage
- **Context**: We needed a database solution that could handle user authentication, data storage, and real-time updates.
- **Decision**: We chose Supabase for its comprehensive features including PostgreSQL database, authentication services, and real-time capabilities.
- **Consequences**: This simplifies our backend infrastructure but ties us to the Supabase ecosystem.

### TDR-002: Microservices Architecture
- **Context**: The system needs to handle multiple distinct responsibilities (news fetching, summarization, story tracking).
- **Decision**: We adopted a microservices architecture to separate concerns and allow independent scaling.
- **Consequences**: This increases deployment complexity but provides better scalability and maintainability.

### TDR-003: LLM for Summarization
- **Context**: News articles need to be summarized effectively.
- **Decision**: We use OpenAI's models for summarization due to their high quality and reliability.
- **Consequences**: This creates an external dependency and ongoing API costs, but provides superior summarization quality.

## Deployment Architecture

### Production Environment
- **Cloud Provider**: Google Cloud Platform
- **Container Orchestration**: Google Kubernetes Engine (GKE)
- **CI/CD**: Cloud Build

### Deployment Workflow
1. Code is pushed to the main branch
2. Cloud Build triggers a new build
3. Docker images are built and pushed to Container Registry
4. Kubernetes manifests are updated with new image tags
5. Kubernetes applies the changes, rolling out new versions

### Scale Strategy
- **Horizontal Pod Autoscaling**: Based on CPU and memory metrics
- **Node Autoscaling**: GKE Cluster Autoscaler adjusts node count based on pod demand

## Security Considerations

### Authentication & Authorization
- JWT-based authentication for API endpoints
- Role-based access control for administrative functions
- Secure token storage in frontend using HTTP-only cookies

### Data Protection
- All data in transit encrypted using TLS
- Sensitive configuration stored in environment variables
- Database access restricted through Supabase security policies

### API Security
- Rate limiting to prevent abuse
- Input validation on all endpoints
- CORS policy to restrict origins

## Performance Optimization

### Caching Strategy
- Redis cache for frequently accessed news data
- Browser caching for static assets
- In-memory caching for API responses

### Lazy Loading
- Frontend implements lazy loading for images and components
- Dynamic imports for code splitting

### Database Optimization
- Indexes on frequently queried columns
- Connection pooling for database access
- Query optimization for complex joins

## Monitoring & Observability

### Logging
- Structured logging using JSON format
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Log shipping to centralized storage

### Metrics
- Prometheus for metrics collection
- Custom metrics for business KPIs
- Dashboard using Grafana

### Alerting
- Alert on high error rates
- Alert on service unavailability
- Alert on unusual traffic patterns

## Future Roadmap

### Short-term Improvements
- Enhanced mobile responsiveness
- User preference personalization
- Additional news sources integration

### Mid-term Goals
- Advanced sentiment analysis
- Topic classification using ML
- Recommendation engine

### Long-term Vision
- Multi-language support
- Audio summaries
- Community features (comments, sharing)

## Key Architecture Principles

This architecture follows a microservices paradigm where each module is dedicated to a specific responsibility:

- **Modular Design**: Each component focuses on a specific task and can be developed, tested, and scaled independently.
- **API Gateway Pattern**: A unified entry point for all client requests simplifies the client-server interaction.
- **Context-Based Organization**: Frontend code is organized by feature contexts (auth, news, story tracking) for better maintainability.
- **Stateless Services**: Backend services are designed to be stateless, improving scalability and fault tolerance.
- **Database as Integration Point**: Supabase serves as the central data store, connecting different services.

## Final Summary

The NewsFeast project architecture enables efficient news aggregation, summarization, and story tracking through a well-organized microservices backend and a modern React frontend. The design prioritizes maintainability, scalability, and user experience, allowing for future feature additions and improvements without disrupting the overall architecture.

Key components work together seamlessly:
- **News Fetching**: Retrieves articles from external sources
- **Summarization**: Generates concise article summaries
- **Story Tracking**: Groups related articles and tracks evolving stories
- **User Management**: Handles authentication and user preferences
- **Web Interface**: Presents information in an engaging, user-friendly manner

This architectural guide ensures that any developer can understand the system's design, extend its functionality, or integrate new components with confidence.
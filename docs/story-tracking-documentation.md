# Story Tracking Documentation

## Overview

Story Tracking is a feature in the News Aggregator application that allows users to track specific news topics over time. The system works by:

1. Enabling users to select keywords to track
2. Backend polling for new articles related to these keywords
3. Real-time frontend updates using Supabase subscriptions
4. Providing users control over which stories are tracked and when polling occurs

## Architecture

The Story Tracking feature follows a backend-first, frontend-next approach:

### Backend Components

1. **Story Tracking Service** (`story_tracking_service.py`)
   - Core functionality for tracking stories by keyword
   - Manages tracked stories in the database
   - Handles polling logic for finding new articles
   - Provides functions for story management (create, get, delete, etc.)

2. **API Gateway** (`api_gateway.py`)
   - Exposes RESTful endpoints for frontend interaction
   - Routes for creating, retrieving, and deleting tracked stories
   - Special endpoints for controlling polling (`/start` and `/stop`)
   - Authentication middleware to secure operations

3. **Polling Worker**
   - Background process that checks for stories due for polling
   - Fetches new articles for tracked stories
   - Updates the database with new articles

### Frontend Components

1. **StoryTrackingContext** (`StoryTrackingContext.tsx`)
   - Provides app-wide state management for tracked stories
   - Handles API calls to the backend for story operations
   - Exposes functions for starting/stopping tracking and polling

2. **StoryTrackingPage** (`StoryTrackingPage.tsx`)
   - UI for viewing and managing a tracked story
   - Controls for toggling automatic updates (polling)
   - Displays real-time updates of new articles

3. **StoryTrackingTabContext** (`StoryTrackingTabContext.tsx`)
   - Manages real-time subscription to Supabase for updates
   - Displays articles for a specific tracked story
   - Handles formatting and sorting of article data

4. **ArticleView** (`ArticleView.tsx`)
   - Provides tracking button in article view
   - Allows users to track stories from individual articles

### Database Schema

The feature uses three main tables in Supabase:

1. `tracked_stories`
   - `id`: Unique identifier for each tracked story
   - `user_id`: The user tracking the story
   - `keyword`: The keyword/phrase being tracked
   - `created_at`: When tracking started
   - `is_polling`: Whether automatic polling is enabled
   - `last_polled_at`: When the story was last checked for updates

2. `tracked_story_articles`
   - `id`: Unique identifier for the tracked article association
   - `tracked_story_id`: Foreign key to tracked_stories
   - `news_id`: Foreign key to news_articles
   - `added_at`: When this article was added to the tracked story

3. `news_articles`
   - Contains all article data
   - Used by the tracking system to store and retrieve articles

## API Endpoints

The API Gateway provides the following endpoints for story tracking:

1. **GET `/api/story_tracking`**
   - Gets news articles for a keyword
   - Query params: `keyword`
   - No authentication required

2. **POST `/api/story_tracking`**
   - Creates a new tracked story
   - Body: `{ keyword, sourceArticleId? }`
   - Requires authentication

3. **GET `/api/story_tracking/user`**
   - Gets all tracked stories for the authenticated user
   - Requires authentication

4. **GET `/api/story_tracking/{story_id}`**
   - Gets details for a specific story including articles
   - Requires authentication

5. **DELETE `/api/story_tracking/{story_id}`**
   - Deletes a tracked story
   - Requires authentication

6. **POST `/api/story_tracking/start`**
   - Starts polling for a tracked story
   - Body: `{ story_id }`
   - Requires authentication

7. **POST `/api/story_tracking/stop`**
   - Stops polling for a tracked story
   - Body: `{ story_id }`
   - Requires authentication

## Frontend Service Layer

The `storyTrackingService.ts` provides a clean interface for the frontend to interact with the backend:

1. `createTrackedStory(keyword, sourceArticleId?)`: Create a new tracked story
2. `getTrackedStories()`: Retrieve all tracked stories for the user
3. `getTrackedStory(id)`: Get details for a specific story
4. `deleteTrackedStory(id)`: Stop tracking a story
5. `startPolling(storyId)`: Enable automatic updates for a story
6. `stopPolling(storyId)`: Disable automatic updates for a story

## Data Flow

### Creating and Tracking a Story

1. User clicks on the tracking button in ArticleView
2. Frontend navigates to `/story-tracking/{keyword}`
3. StoryTrackingPage mounts and calls `startTracking(keyword)`
4. StoryTrackingContext makes a POST call to `/api/story_tracking` with the keyword
5. API Gateway creates a tracked story in the database using `create_tracked_story()`
6. Backend searches for and associates relevant articles with the story
7. Response with story details is sent back to the frontend
8. StoryTrackingContext updates its state with the new story
9. StoryTrackingPage displays the story details

### Real-time Updates

1. StoryTrackingTabContext sets up a Supabase subscription when a story page is opened
2. The subscription listens for INSERT events on the `tracked_story_articles` table
3. When an article is added by the backend polling process:
   - Supabase sends a real-time notification to the frontend
   - Frontend receives the article ID and fetches full details
   - New article is added to the UI without page refresh

### Controlling Polling

1. User clicks "Auto-update" button on StoryTrackingPage
2. Frontend calls `togglePolling(storyId, true/false)`
3. StoryTrackingContext calls either `startPolling()` or `stopPolling()`
4. Request is sent to `/api/story_tracking/start` or `/api/story_tracking/stop`
5. Backend updates the `is_polling` flag on the tracked story
6. Polling Worker recognizes the change and includes/excludes the story from polling

## Polling Logic (Backend)

1. The Polling Worker runs as a background process
2. It periodically checks for stories with `is_polling = true`
3. For each polling-enabled story:
   - Check if it's due for polling (based on `last_polled_at` and polling frequency)
   - Fetch new articles using the story's keyword
   - Associate new articles with the story in `tracked_story_articles`
   - Update `last_polled_at` timestamp

## Error Handling

- Frontend shows loading states during API calls
- Timeout detection for long-running operations
- Error messages displayed to users
- Fallbacks for when real-time subscriptions fail

## Authentication Flow

All story tracking operations (except initial keyword search) require authentication:

1. Frontend gets the current session token from Supabase Auth
2. Token is included in all API requests as a Bearer token
3. Backend validates the token using the JWT middleware
4. Operations are only performed for the authenticated user

## Code Relationships

- `StoryTrackingContext.tsx` is the central connector that:
  - Provides state to all story tracking components
  - Makes API calls through `storyTrackingService.ts`
  - Updates state based on API responses

- `StoryTrackingPage.tsx` uses the context to:
  - Display a specific tracked story
  - Control polling status
  - Remove tracking when requested

- `StoryTrackingTabContext.tsx` handles:
  - Real-time subscriptions to story updates
  - Rendering and formatting articles

## Future Improvements

- Enhanced error recovery for polling processes
- Improved article relevance through better keyword matching
- User preferences for polling frequency
- Support for more complex tracking queries beyond simple keywords
- Email or push notifications for important story updates
<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Piano Simulator Backend - FastAPI Project

## Project Context
This is a FastAPI backend for a piano simulator web application. The backend provides:
- User authentication and authorization with JWT tokens
- Composition storage and retrieval
- Keyboard mapping configuration synchronization
- User management and profiles
- Audio processing capabilities

## Technologies Used
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Primary database
- **JWT**: Authentication tokens
- **Pydantic**: Data validation using Python type annotations
- **Alembic**: Database migration tool

## Code Patterns
- Use dependency injection for database sessions and authentication
- Follow RESTful API design principles
- Implement proper error handling with HTTP status codes
- Use Pydantic models for request/response validation
- Follow async/await patterns for database operations
- Implement proper logging and monitoring

## Database Models
- User: Authentication and profile information
- Composition: Musical compositions with metadata
- KeyMap: Keyboard configuration mappings
- SharedComposition: Public compositions that can be shared

## API Structure
- `/auth/` - Authentication endpoints (login, register, refresh)
- `/users/` - User management
- `/compositions/` - Composition CRUD operations
- `/keymaps/` - Keyboard configuration sync
- `/shared/` - Public composition sharing
- `/health/` - Health check endpoints

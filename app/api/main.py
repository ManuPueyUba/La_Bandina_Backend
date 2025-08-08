from fastapi import APIRouter

from app.api.routes import auth, users, songs

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(songs.router, tags=["songs", "recordings", "midi"])

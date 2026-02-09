# backend/app/api/dependencies.py
from backend.app.db.session import get_connection, release_connection
from backend.app.services.database_service import DatabaseService

def get_db():
    """Provide DatabaseService with connection pool functions."""
    yield DatabaseService(get_connection, release_connection)
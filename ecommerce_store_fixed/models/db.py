"""
Database module implementing Singleton pattern for database connection management
"""
from flask_sqlalchemy import SQLAlchemy

class DatabaseManager:
    """
    Singleton class to manage database connections
    Ensures only one database instance exists throughout the application
    """
    _instance = None
    _db = None
    
    def __new__(cls):
        """
        Singleton implementation - ensures only one instance exists
        """
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._db = SQLAlchemy()
        return cls._instance
    
    @property
    def db(self):
        """Get the database instance"""
        return self._db
    
    def init_app(self, app):
        """Initialize the database with Flask app"""
        self._db.init_app(app)
    
    def create_all(self, app):
        """Create all database tables"""
        with app.app_context():
            self._db.create_all()
    
    def drop_all(self, app):
        """Drop all database tables (use with caution!)"""
        with app.app_context():
            self._db.drop_all()

# Get the singleton instance
db_manager = DatabaseManager()
db = db_manager.db

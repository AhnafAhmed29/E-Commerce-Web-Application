"""
Strategy Pattern implementation for different authentication strategies
This demonstrates the Strategy (Behavioral) design pattern
"""
from abc import ABC, abstractmethod
from models.user import User

class AuthenticationStrategy(ABC):
    """
    Abstract Strategy interface for authentication
    Defines the interface for authentication algorithms
    """
    
    @abstractmethod
    def authenticate(self, identifier, password):
        """
        Authenticate user with given credentials
        
        Args:
            identifier: Username or email
            password: User password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        pass
    
    @abstractmethod
    def can_access_admin(self, user):
        """
        Check if user can access admin areas
        
        Args:
            user: User object
            
        Returns:
            bool: True if user can access admin areas
        """
        pass


class UserAuthenticationStrategy(AuthenticationStrategy):
    """
    Concrete Strategy for regular user authentication
    """
    
    def authenticate(self, identifier, password):
        """
        Authenticate regular user by email or username
        """
        # Try to find user by email or username
        user = User.query.filter(
            (User.email == identifier) | (User.username == identifier)
        ).first()
        
        if user and user.check_password(password):
            return user
        
        return None
    
    def can_access_admin(self, user):
        """
        Regular users cannot access admin areas
        """
        return False


class AdminAuthenticationStrategy(AuthenticationStrategy):
    """
    Concrete Strategy for admin authentication
    """
    
    def authenticate(self, identifier, password):
        """
        Authenticate admin user - must have admin privileges
        """
        # Try to find user by email or username
        user = User.query.filter(
            (User.email == identifier) | (User.username == identifier)
        ).first()
        
        # Check password and admin status
        if user and user.check_password(password) and user.is_admin():
            return user
        
        return None
    
    def can_access_admin(self, user):
        """
        Check if user has admin privileges
        """
        return user and user.is_admin()


class AuthenticationContext:
    """
    Context class that uses an authentication strategy
    This allows switching between different authentication strategies at runtime
    """
    
    def __init__(self, strategy=None):
        """
        Initialize with a strategy
        
        Args:
            strategy: AuthenticationStrategy instance
        """
        self._strategy = strategy or UserAuthenticationStrategy()
    
    def set_strategy(self, strategy):
        """
        Change authentication strategy at runtime
        
        Args:
            strategy: AuthenticationStrategy instance
        """
        self._strategy = strategy
    
    def authenticate(self, identifier, password):
        """
        Authenticate using the current strategy
        
        Args:
            identifier: Username or email
            password: User password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        return self._strategy.authenticate(identifier, password)
    
    def can_access_admin(self, user):
        """
        Check admin access using current strategy
        
        Args:
            user: User object
            
        Returns:
            bool: True if user can access admin areas
        """
        return self._strategy.can_access_admin(user)


# Convenience functions for easy usage
def authenticate_user(identifier, password):
    """
    Authenticate a regular user
    
    Usage:
        user = authenticate_user('user@example.com', 'password123')
    """
    context = AuthenticationContext(UserAuthenticationStrategy())
    return context.authenticate(identifier, password)


def authenticate_admin(identifier, password):
    """
    Authenticate an admin user
    
    Usage:
        admin = authenticate_admin('admin@example.com', 'admin123')
    """
    context = AuthenticationContext(AdminAuthenticationStrategy())
    return context.authenticate(identifier, password)


def verify_admin_access(user):
    """
    Verify if a user has admin access
    
    Usage:
        if verify_admin_access(current_user):
            # Allow admin access
    """
    context = AuthenticationContext(AdminAuthenticationStrategy())
    return context.can_access_admin(user)

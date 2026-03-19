"""
Factory Pattern implementation for creating different types of users
This demonstrates the Factory Method (Creational) design pattern
"""
from models.user import User
from abc import ABC, abstractmethod

class UserFactory(ABC):
    """
    Abstract Factory for creating users
    This is the Factory Method pattern - defines interface for creating objects
    """
    
    @abstractmethod
    def create_user(self, email, username, password, **kwargs):
        """
        Factory method that must be implemented by concrete factories
        """
        pass
    
    def _validate_email(self, email):
        """Common validation logic"""
        if not email or '@' not in email:
            raise ValueError("Invalid email address")
        return True
    
    def _validate_password(self, password):
        """Common validation logic"""
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        return True


class CustomerFactory(UserFactory):
    """
    Concrete Factory for creating customer users
    """
    
    def create_user(self, email, username, password, **kwargs):
        """
        Creates a customer user with customer-specific defaults
        """
        self._validate_email(email)
        self._validate_password(password)
        
        # Create customer with default customer privileges
        user = User(
            email=email,
            username=username,
            password=password,
            user_type='customer',
            first_name=kwargs.get('first_name', ''),
            last_name=kwargs.get('last_name', ''),
            phone=kwargs.get('phone', '')
        )
        
        return user


class AdminFactory(UserFactory):
    """
    Concrete Factory for creating admin users
    """
    
    def create_user(self, email, username, password, **kwargs):
        """
        Creates an admin user with admin-specific defaults
        """
        self._validate_email(email)
        self._validate_password(password)
        
        # Create admin with admin privileges
        user = User(
            email=email,
            username=username,
            password=password,
            user_type='admin',
            first_name=kwargs.get('first_name', ''),
            last_name=kwargs.get('last_name', ''),
            phone=kwargs.get('phone', '')
        )
        
        return user


class UserFactoryProvider:
    """
    Provides the appropriate factory based on user type
    This is a simple factory that returns other factories
    """
    
    @staticmethod
    def get_factory(user_type='customer'):
        """
        Returns the appropriate user factory
        
        Args:
            user_type: 'customer' or 'admin'
            
        Returns:
            UserFactory: The appropriate factory instance
        """
        factories = {
            'customer': CustomerFactory(),
            'admin': AdminFactory()
        }
        
        factory = factories.get(user_type.lower())
        if not factory:
            raise ValueError(f"Unknown user type: {user_type}")
        
        return factory


# Convenience function for easy usage
def create_user(email, username, password, user_type='customer', **kwargs):
    """
    Convenience function to create a user using the factory pattern
    
    Usage:
        user = create_user('user@example.com', 'username', 'password123', user_type='customer')
        admin = create_user('admin@example.com', 'admin', 'admin123', user_type='admin')
    """
    factory = UserFactoryProvider.get_factory(user_type)
    return factory.create_user(email, username, password, **kwargs)

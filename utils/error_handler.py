import logging
import traceback
import time
import functools
from typing import Type, Tuple, Optional, Any, Callable, Union, TypeVar

from .logger import AdvancedLogger

T = TypeVar('T')

class ErrorHandler:
    """
    Advanced error handling and management utility
    """
    
    def __init__(
        self, 
        log_level: str = 'ERROR',
        exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        """
        Initialize ErrorHandler with logging and exception tracking
        
        :param log_level: Logging level for error handling
        :param exceptions: Tuple of exception types to handle
        """
        self.logger = AdvancedLogger(log_level=log_level)
        self.tracked_exceptions = exceptions
    
    @classmethod
    def retry(
        cls, 
        max_attempts: int = 3, 
        delay: float = 1.0, 
        backoff: float = 2.0,
        exceptions: Optional[Tuple[Type[Exception], ...]] = None
    ):
        """
        Decorator for retrying a function with exponential backoff
        
        :param max_attempts: Maximum number of retry attempts
        :param delay: Initial delay between retries
        :param backoff: Exponential backoff factor
        :param exceptions: Exceptions to catch and retry
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> T:
                error_handler = cls()
                current_delay = delay
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        # Determine if the exception should trigger a retry
                        retry_exceptions = exceptions or (Exception,)
                        if not isinstance(e, retry_exceptions):
                            raise
                        
                        # Log retry attempt
                        error_handler.logger.log_debug(
                            f"Retry attempt {attempt + 1} for {func.__name__}",
                            error_type=type(e).__name__,
                            error_message=str(e)
                        )
                        
                        # Last attempt, raise the exception
                        if attempt == max_attempts - 1:
                            raise
                        
                        # Wait before next retry with exponential backoff
                        time.sleep(current_delay)
                        current_delay *= backoff
            
            return wrapper
        return decorator
    
    def handle_error(
        self, 
        error: Exception, 
        context: Optional[dict] = None,
        additional_info: Optional[str] = None
    ) -> dict:
        """
        Comprehensive error handling and logging
        
        :param error: Exception to handle
        :param context: Additional context about the error
        :param additional_info: Extra information about the error
        :return: Error report dictionary
        """
        error_report = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {},
            'additional_info': additional_info
        }
        
        # Log the error with detailed information
        self.logger.log_error(
            f"Error occurred: {error_report['error_type']}", 
            error=error,
            **error_report
        )
        
        return error_report
    
    def retry_operation(
        self, 
        operation: Callable[..., Any], 
        max_retries: int = 3,
        retry_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
        *args: Any, 
        **kwargs: Any
    ) -> Any:
        """
        Retry an operation with configurable retry mechanism
        
        :param operation: Function to retry
        :param max_retries: Maximum number of retry attempts
        :param retry_exceptions: Exceptions that trigger a retry
        :param args: Positional arguments for the operation
        :param kwargs: Keyword arguments for the operation
        :return: Result of the operation
        """
        retry_exceptions = retry_exceptions or self.tracked_exceptions
        
        for attempt in range(max_retries):
            try:
                return operation(*args, **kwargs)
            except retry_exceptions as e:
                if attempt == max_retries - 1:
                    # Last attempt, raise the exception
                    raise
                
                self.logger.log_debug(
                    f"Retry attempt {attempt + 1} for operation",
                    operation_name=operation.__name__,
                    error_type=type(e).__name__
                )
    
    def safe_execute(
        self, 
        operation: Callable[..., Any], 
        default_return: Optional[Any] = None,
        *args: Any, 
        **kwargs: Any
    ) -> Union[Any, None]:
        """
        Execute an operation safely with optional default return
        
        :param operation: Function to execute
        :param default_return: Value to return if operation fails
        :param args: Positional arguments for the operation
        :param kwargs: Keyword arguments for the operation
        :return: Operation result or default value
        """
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            error_report = self.handle_error(
                e, 
                context={
                    'operation': operation.__name__,
                    'args': args,
                    'kwargs': kwargs
                }
            )
            
            return default_return
    
    def validate_input(
        self, 
        input_data: Any, 
        validation_func: Optional[Callable[[Any], bool]] = None,
        error_message: str = "Invalid input"
    ) -> bool:
        """
        Validate input data with optional custom validation function
        
        :param input_data: Data to validate
        :param validation_func: Optional custom validation function
        :param error_message: Custom error message
        :return: Whether input is valid
        """
        try:
            # Default validation if no custom function provided
            if validation_func is None:
                validation_func = lambda x: x is not None
            
            is_valid = validation_func(input_data)
            
            if not is_valid:
                raise ValueError(error_message)
            
            return True
        except Exception as e:
            self.handle_error(
                e, 
                context={
                    'input_data': input_data,
                    'validation_func': validation_func.__name__ if validation_func else 'default'
                }
            )
            return False

def main():
    """
    Demonstration of error handling capabilities
    """
    error_handler = ErrorHandler()
    
    # Demonstrate error handling
    def divide(a: int, b: int) -> float:
        return a / b
    
    # Safe execution
    result = error_handler.safe_execute(divide, default_return=0, a=10, b=2)
    print("Safe division result:", result)
    
    # Retry mechanism
    def flaky_operation():
        import random
        if random.random() < 0.7:
            raise ValueError("Random failure")
        return "Success"
    
    try:
        result = error_handler.retry_operation(flaky_operation, max_retries=3)
        print("Retry operation result:", result)
    except Exception as e:
        print("Operation failed after retries")
    
    # Input validation
    is_valid = error_handler.validate_input(
        "test_input", 
        validation_func=lambda x: len(x) > 5
    )
    print("Input validation result:", is_valid)

if __name__ == "__main__":
    main()

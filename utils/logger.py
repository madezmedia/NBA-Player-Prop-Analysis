import logging
import sys
import json
from typing import Dict, Any, Optional

try:
    import structlog
    USE_STRUCTLOG = True
except ImportError:
    USE_STRUCTLOG = False

class AdvancedLogger:
    """
    Advanced logging utility with support for structured logging
    """
    
    def __init__(
        self, 
        log_level: str = 'INFO', 
        use_structlog: bool = True
    ):
        """
        Initialize logger
        
        :param log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        :param use_structlog: Whether to use structured logging
        """
        # Convert log level string to logging constant
        log_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Configure base logger
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('basketball_ai.log', encoding='utf-8')
            ]
        )
        
        # Structured logging configuration
        if use_structlog and USE_STRUCTLOG:
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.JSONRenderer()
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
            self.logger = structlog.get_logger()
        else:
            # Fallback to standard logging
            self.logger = logging.getLogger('BasketballAILogger')
    
    def log_event(
        self, 
        message: str, 
        level: str = 'info', 
        **kwargs
    ):
        """
        Log an event with optional additional context
        
        :param message: Log message
        :param level: Logging level
        :param kwargs: Additional context information
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        
        if USE_STRUCTLOG and hasattr(self.logger, 'bind'):
            # Structured logging
            log_method = log_method.bind(**kwargs)
            log_method(message)
        else:
            # Standard logging
            context_str = json.dumps(kwargs) if kwargs else ''
            log_method(f"{message} {context_str}")
    
    def log_error(
        self, 
        message: str, 
        error: Optional[Exception] = None, 
        **kwargs
    ):
        """
        Log an error with optional exception details
        
        :param message: Error message
        :param error: Exception object
        :param kwargs: Additional context information
        """
        if error:
            kwargs['error_type'] = type(error).__name__
            kwargs['error_details'] = str(error)
        
        self.log_event(message, level='error', **kwargs)
    
    def log_debug(
        self, 
        message: str, 
        **kwargs
    ):
        """
        Log a debug message
        
        :param message: Debug message
        :param kwargs: Additional context information
        """
        self.log_event(message, level='debug', **kwargs)

def main():
    """
    Demonstration of logger functionality
    """
    logger = AdvancedLogger()
    
    # Log different types of events
    logger.log_event("Application started", level='info')
    logger.log_debug("Debugging information", extra_context="Test")
    
    try:
        # Simulate an error
        1 / 0
    except Exception as e:
        logger.log_error("Division by zero error", error=e)

if __name__ == "__main__":
    main()

# Basketball AI Utilities

## Overview
This directory contains utility modules that provide essential functionality for the Basketball AI Performance Analyst application.

## Modules

### `config_manager.py`
Centralized configuration management for the application.
- Load and validate configuration
- Manage environment variables
- Merge configuration settings

### `data_processor.py`
Advanced data processing and caching utility for basketball statistics.
- Cache player statistics
- Process player comparisons
- Export player data in various formats

### `logger.py`
Advanced logging utility with structured logging capabilities.
- Configurable logging levels
- Console and file logging
- Performance and audit logging
- Structured log formatting

### `error_handler.py`
Comprehensive error handling and reporting utility.
- Exception handling and formatting
- Retry mechanism with exponential backoff
- Input validation decorators
- Optional Sentry integration for error tracking

## Usage Examples

### Configuration Management
```python
from utils.config_manager import ConfigManager

config = ConfigManager()
api_config = config.get_api_config('groq')
```

### Data Processing
```python
from utils.data_processor import DataProcessor

processor = DataProcessor()
lebron_stats = processor.get_cached_player_stats("LeBron James")
comparison = processor.process_player_comparison("LeBron James", "Stephen Curry")
```

### Logging
```python
from utils.logger import AdvancedLogger

logger = AdvancedLogger(log_level='DEBUG')
logger.log_event("Application started")
logger.performance_log("data_fetch", duration=0.5)
```

### Error Handling
```python
from utils.error_handler import ErrorHandler

error_handler = ErrorHandler()

@error_handler.retry(max_attempts=3)
@error_handler.validate_input(lambda x: x > 0)
def divide_numbers(a, b):
    return a / b
```

## Best Practices
- Use configuration management for centralized settings
- Leverage caching in data processing
- Implement comprehensive logging
- Use error handling decorators for robust code

## Contributing
Please ensure that any modifications maintain the existing design principles and add appropriate tests.

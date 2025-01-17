import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

class ConfigManager:
    """
    Centralized configuration management for the Basketball AI Analyst
    """
    
    def __init__(self, env_path: str = None):
        """
        Initialize configuration manager
        
        :param env_path: Optional path to .env file
        """
        # Load environment variables
        if env_path and os.path.exists(env_path):
            load_dotenv(env_path)
        else:
            load_dotenv()

        # Default configuration
        self._default_config = {
            'api': {
                'groq': {
                    'model': 'mixtral-8x7b-32768',
                    'max_tokens': 300,
                    'temperature': 0.7
                },
                'rapidapi': {
                    'host': 'basketball-head.p.rapidapi.com',
                    'endpoints': {
                        'player_search': '/players/searchv2'
                    }
                }
            },
            'performance': {
                'cache_size': 100,
                'prediction_confidence_threshold': 0.7
            },
            'logging': {
                'level': 'INFO',
                'file': 'basketball_ai.log'
            }
        }

        # Custom configuration file path
        self._config_file = os.path.join(os.getcwd(), 'config.json')

    def get_env_variable(self, key: str, default: str = None) -> str:
        """
        Retrieve an environment variable
        
        :param key: Environment variable name
        :param default: Default value if not found
        :return: Environment variable value
        """
        return os.getenv(key, default)

    def get_api_config(self, service: str) -> Dict[str, Any]:
        """
        Retrieve API configuration for a specific service
        
        :param service: API service name (e.g., 'groq', 'rapidapi')
        :return: API configuration dictionary
        """
        return self._default_config['api'].get(service, {})

    def get_performance_config(self) -> Dict[str, Any]:
        """
        Retrieve performance-related configuration
        
        :return: Performance configuration dictionary
        """
        return self._default_config['performance']

    def load_custom_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        Load custom configuration from a JSON file
        
        :param config_path: Path to custom configuration file
        :return: Loaded configuration
        """
        if config_path:
            self._config_file = config_path

        if os.path.exists(self._config_file):
            with open(self._config_file, 'r') as f:
                custom_config = json.load(f)
            
            # Merge custom config with default config
            self._merge_configs(self._default_config, custom_config)
        
        return self._default_config

    def save_custom_config(self, config: Dict[str, Any]) -> None:
        """
        Save custom configuration to JSON file
        
        :param config: Configuration dictionary to save
        """
        with open(self._config_file, 'w') as f:
            json.dump(config, f, indent=2)

    @staticmethod
    def _merge_configs(base_config: Dict[str, Any], update_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two configuration dictionaries
        
        :param base_config: Base configuration
        :param update_config: Configuration to update with
        :return: Merged configuration
        """
        for key, value in update_config.items():
            if isinstance(value, dict):
                base_config[key] = ConfigManager._merge_configs(
                    base_config.get(key, {}), value
                )
            else:
                base_config[key] = value
        return base_config

    def validate_config(self) -> bool:
        """
        Validate the current configuration
        
        :return: Whether the configuration is valid
        """
        required_keys = [
            'api.groq.model',
            'api.rapidapi.host',
            'performance.cache_size',
            'logging.level'
        ]
        
        for key in required_keys:
            try:
                # Attempt to access nested keys
                value = self._get_nested_key(self._default_config, key)
                if value is None:
                    return False
            except KeyError:
                return False
        
        return True

    @staticmethod
    def _get_nested_key(config: Dict[str, Any], key: str) -> Any:
        """
        Retrieve a nested key from a dictionary
        
        :param config: Configuration dictionary
        :param key: Dot-separated key path
        :return: Value of the nested key
        """
        keys = key.split('.')
        for k in keys:
            config = config[k]
        return config

# Example usage
if __name__ == "__main__":
    config_manager = ConfigManager()
    
    # Get API configuration
    groq_config = config_manager.get_api_config('groq')
    print("Groq API Config:", groq_config)
    
    # Get environment variables
    api_key = config_manager.get_env_variable('GROQ_API_KEY')
    print("Groq API Key:", api_key)
    
    # Load and validate custom configuration
    custom_config = config_manager.load_custom_config()
    is_valid = config_manager.validate_config()
    print("Configuration Valid:", is_valid)

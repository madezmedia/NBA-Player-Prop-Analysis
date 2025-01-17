import os
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from utils.logger import AdvancedLogger
from utils.error_handler import ErrorHandler

@dataclass
class ValidationResult:
    """
    Dataclass to represent data validation results
    """
    is_valid: bool
    errors: List[str]
    summary: Dict[str, Any]

class BasketballDataValidator:
    """
    Advanced data validation utility for basketball performance data
    """
    
    def __init__(
        self, 
        logger: Optional[AdvancedLogger] = None,
        error_handler: Optional[ErrorHandler] = None
    ):
        """
        Initialize data validator
        
        :param logger: Optional logging utility
        :param error_handler: Optional error handling utility
        """
        self.logger = logger or AdvancedLogger()
        self.error_handler = error_handler or ErrorHandler()
        
        # Validation rules
        self.validation_rules = {
            'player_stats': {
                'required_columns': [
                    'points_per_game', 
                    'rebounds_per_game', 
                    'assists_per_game'
                ],
                'numeric_columns': [
                    'points_per_game', 
                    'rebounds_per_game', 
                    'assists_per_game',
                    'field_goal_percentage',
                    'three_point_percentage'
                ],
                'range_constraints': {
                    'points_per_game': (0, 50),
                    'rebounds_per_game': (0, 20),
                    'assists_per_game': (0, 15),
                    'field_goal_percentage': (0, 1),
                    'three_point_percentage': (0, 1)
                }
            }
        }
    
    def validate_player_data(
        self, 
        data: Union[Dict[str, Any], pd.DataFrame]
    ) -> ValidationResult:
        """
        Validate player performance data
        
        :param data: Player data to validate
        :return: Validation result
        """
        try:
            # Convert dictionary to DataFrame if needed
            if isinstance(data, dict):
                data = self._dict_to_dataframe(data)
            
            # Initialize validation errors
            validation_errors = []
            validation_summary = {}
            
            # Check required columns
            missing_columns = [
                col for col in self.validation_rules['player_stats']['required_columns']
                if col not in data.columns
            ]
            if missing_columns:
                validation_errors.append(
                    f"Missing required columns: {missing_columns}"
                )
            
            # Validate numeric columns
            for column in self.validation_rules['player_stats']['numeric_columns']:
                if column in data.columns:
                    # Check for non-numeric values
                    if not np.issubdtype(data[column].dtype, np.number):
                        validation_errors.append(
                            f"Non-numeric values in column: {column}"
                        )
                    
                    # Check range constraints
                    if column in self.validation_rules['player_stats']['range_constraints']:
                        min_val, max_val = self.validation_rules['player_stats']['range_constraints'][column]
                        out_of_range = data[
                            (data[column] < min_val) | (data[column] > max_val)
                        ]
                        
                        if not out_of_range.empty:
                            validation_errors.append(
                                f"Values out of range in {column}: "
                                f"Min={min_val}, Max={max_val}"
                            )
            
            # Compute validation summary
            validation_summary = {
                'total_records': len(data),
                'numeric_columns': self.validation_rules['player_stats']['numeric_columns'],
                'range_constraints': self.validation_rules['player_stats']['range_constraints']
            }
            
            # Determine overall validation status
            is_valid = len(validation_errors) == 0
            
            # Log validation results
            log_method = (
                self.logger.log_event if is_valid 
                else self.logger.log_error
            )
            log_method(
                "Player data validation", 
                level='info' if is_valid else 'error',
                is_valid=is_valid,
                errors=validation_errors
            )
            
            return ValidationResult(
                is_valid=is_valid,
                errors=validation_errors,
                summary=validation_summary
            )
        
        except Exception as e:
            error_details = self.error_handler.handle_exception(
                e, 
                context={'operation': 'player_data_validation'}
            )
            
            self.logger.log_error(
                "Error during player data validation", 
                error=e, 
                **error_details
            )
            
            return ValidationResult(
                is_valid=False,
                errors=[str(e)],
                summary={}
            )
    
    def _dict_to_dataframe(
        self, 
        player_data: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Convert dictionary to DataFrame
        
        :param player_data: Player performance dictionary
        :return: DataFrame representation
        """
        # Flatten nested dictionaries
        flat_data = {}
        for player, data in player_data.items():
            player_features = {}
            
            # Extract basic stats
            stats = data.get('stats', {})
            advanced_metrics = data.get('advanced_metrics', {})
            
            player_features.update({
                'name': player,
                'points_per_game': stats.get('points_per_game', 0),
                'rebounds_per_game': stats.get('rebounds_per_game', 0),
                'assists_per_game': stats.get('assists_per_game', 0),
                'field_goal_percentage': stats.get('field_goal_percentage', 0),
                'three_point_percentage': stats.get('three_point_percentage', 0),
                'player_efficiency_rating': advanced_metrics.get('player_efficiency_rating', 0),
                'true_shooting_percentage': advanced_metrics.get('true_shooting_percentage', 0)
            })
            
            flat_data[player] = player_features
        
        return pd.DataFrame.from_dict(flat_data, orient='index')
    
    def detect_outliers(
        self, 
        data: Union[Dict[str, Any], pd.DataFrame], 
        method: str = 'iqr'
    ) -> Dict[str, List[str]]:
        """
        Detect outliers in player data
        
        :param data: Player data to analyze
        :param method: Outlier detection method ('iqr' or 'zscore')
        :return: Dictionary of outliers by feature
        """
        try:
            # Convert dictionary to DataFrame if needed
            if isinstance(data, dict):
                data = self._dict_to_dataframe(data)
            
            outliers = {}
            
            # Numeric columns for outlier detection
            numeric_columns = [
                col for col in self.validation_rules['player_stats']['numeric_columns']
                if col in data.columns
            ]
            
            for column in numeric_columns:
                if method == 'iqr':
                    Q1 = data[column].quantile(0.25)
                    Q3 = data[column].quantile(0.75)
                    IQR = Q3 - Q1
                    
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    column_outliers = data[
                        (data[column] < lower_bound) | 
                        (data[column] > upper_bound)
                    ]['name'].tolist()
                
                elif method == 'zscore':
                    z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
                    column_outliers = data[z_scores > 3]['name'].tolist()
                
                else:
                    raise ValueError(f"Unsupported outlier detection method: {method}")
                
                outliers[column] = column_outliers
            
            # Log outlier detection results
            self.logger.log_event(
                "Outlier detection completed", 
                level='info', 
                outlier_method=method
            )
            
            return outliers
        
        except Exception as e:
            self.logger.log_error(
                "Error during outlier detection", 
                error=e
            )
            
            return {}

# Example usage and demonstration
def main():
    # Sample player data
    player_data = {
        'LeBron James': {
            'stats': {
                'points_per_game': 25.5,
                'rebounds_per_game': 7.8,
                'assists_per_game': 7.2,
                'field_goal_percentage': 0.54,
                'three_point_percentage': 0.35
            },
            'advanced_metrics': {
                'player_efficiency_rating': 22.5,
                'true_shooting_percentage': 0.62
            }
        },
        'Stephen Curry': {
            'stats': {
                'points_per_game': 27.3,
                'rebounds_per_game': 5.2,
                'assists_per_game': 6.3,
                'field_goal_percentage': 0.48,
                'three_point_percentage': 0.42
            },
            'advanced_metrics': {
                'player_efficiency_rating': 24.0,
                'true_shooting_percentage': 0.65
            }
        }
    }
    
    # Initialize Data Validator
    validator = BasketballDataValidator()
    
    # Validate Player Data
    validation_result = validator.validate_player_data(player_data)
    print("Validation Result:", validation_result)
    
    # Detect Outliers
    outliers = validator.detect_outliers(player_data)
    print("Outliers:", outliers)

if __name__ == "__main__":
    main()

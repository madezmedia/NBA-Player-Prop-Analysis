import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_selection import mutual_info_regression
from sklearn.decomposition import PCA

class BasketballFeatureEngineer:
    """
    Advanced feature engineering utility for basketball performance data
    """
    
    def __init__(self, scaling_method: str = 'standard'):
        """
        Initialize feature engineering utility
        
        :param scaling_method: Scaling method ('standard' or 'minmax')
        """
        self.scaling_method = scaling_method
        self.scaler = (
            StandardScaler() if scaling_method == 'standard' 
            else MinMaxScaler()
        )
    
    def extract_features(
        self, 
        player_data: Union[Dict[str, Any], pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Extract and transform raw player data into feature matrix
        
        :param player_data: Player performance data
        :return: Processed feature DataFrame
        """
        # Convert dictionary to DataFrame if needed
        if isinstance(player_data, dict):
            player_data = self._dict_to_dataframe(player_data)
        
        # Feature extraction
        features = self._compute_derived_features(player_data)
        
        return features
    
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
    
    def _compute_derived_features(
        self, 
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Compute additional derived features
        
        :param df: Input DataFrame
        :return: DataFrame with derived features
        """
        # Compute interaction features
        df['scoring_efficiency'] = (
            df['points_per_game'] / 
            (df['field_goal_percentage'] + df['three_point_percentage'] + 1e-5)
        )
        
        df['playmaking_score'] = (
            df['assists_per_game'] * 
            (1 + df['points_per_game'] / 20)
        )
        
        df['versatility_index'] = (
            df['points_per_game'] + 
            df['rebounds_per_game'] + 
            df['assists_per_game']
        )
        
        return df
    
    def scale_features(
        self, 
        features: pd.DataFrame, 
        columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Scale features using selected scaling method
        
        :param features: Input feature DataFrame
        :param columns: Columns to scale (optional)
        :return: Scaled feature DataFrame
        """
        # Use all numeric columns if not specified
        if columns is None:
            columns = features.select_dtypes(include=[np.number]).columns
        
        # Create a copy to avoid modifying original
        scaled_features = features.copy()
        
        # Fit and transform selected columns
        scaled_features[columns] = self.scaler.fit_transform(
            features[columns]
        )
        
        return scaled_features
    
    def feature_importance(
        self, 
        features: pd.DataFrame, 
        target_column: str
    ) -> Dict[str, float]:
        """
        Compute feature importance using mutual information
        
        :param features: Input feature DataFrame
        :param target_column: Target variable for importance calculation
        :return: Dictionary of feature importances
        """
        # Separate features and target
        X = features.drop(columns=[target_column, 'name'])
        y = features[target_column]
        
        # Compute mutual information
        importances = mutual_info_regression(X, y)
        
        # Create importance dictionary
        importance_dict = dict(zip(X.columns, importances))
        
        return dict(
            sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        )
    
    def dimensionality_reduction(
        self, 
        features: pd.DataFrame, 
        n_components: int = 3
    ) -> pd.DataFrame:
        """
        Perform dimensionality reduction using PCA
        
        :param features: Input feature DataFrame
        :param n_components: Number of components to retain
        :return: Reduced dimensionality DataFrame
        """
        # Prepare data for PCA
        X = features.select_dtypes(include=[np.number]).drop(columns=['name'])
        
        # Perform PCA
        pca = PCA(n_components=n_components)
        reduced_features = pca.fit_transform(X)
        
        # Create DataFrame with reduced features
        pca_df = pd.DataFrame(
            reduced_features, 
            columns=[f'PC{i+1}' for i in range(n_components)],
            index=features.index
        )
        
        # Add player names back
        pca_df['name'] = features['name']
        
        return pca_df
    
    def detect_outliers(
        self, 
        features: pd.DataFrame, 
        method: str = 'iqr'
    ) -> Dict[str, List[str]]:
        """
        Detect outliers in feature space
        
        :param features: Input feature DataFrame
        :param method: Outlier detection method ('iqr' or 'zscore')
        :return: Dictionary of outliers by feature
        """
        outliers = {}
        
        # Numeric columns for outlier detection
        numeric_columns = features.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            if method == 'iqr':
                Q1 = features[column].quantile(0.25)
                Q3 = features[column].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                column_outliers = features[
                    (features[column] < lower_bound) | 
                    (features[column] > upper_bound)
                ]['name'].tolist()
            
            elif method == 'zscore':
                z_scores = np.abs((features[column] - features[column].mean()) / features[column].std())
                column_outliers = features[z_scores > 3]['name'].tolist()
            
            else:
                raise ValueError(f"Unsupported outlier detection method: {method}")
            
            outliers[column] = column_outliers
        
        return outliers

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
    
    # Initialize Feature Engineer
    feature_engineer = BasketballFeatureEngineer()
    
    # Extract Features
    features = feature_engineer.extract_features(player_data)
    print("Extracted Features:\n", features)
    
    # Scale Features
    scaled_features = feature_engineer.scale_features(features)
    print("\nScaled Features:\n", scaled_features)
    
    # Feature Importance
    importance = feature_engineer.feature_importance(
        features, 
        target_column='points_per_game'
    )
    print("\nFeature Importance:", importance)
    
    # Dimensionality Reduction
    reduced_features = feature_engineer.dimensionality_reduction(features)
    print("\nReduced Features:\n", reduced_features)
    
    # Outlier Detection
    outliers = feature_engineer.detect_outliers(features)
    print("\nOutliers:", outliers)

if __name__ == "__main__":
    main()

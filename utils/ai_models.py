import os
import numpy as np
import joblib
from typing import Dict, Any, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class BasketballPerformancePredictor:
    """
    Advanced machine learning model for predicting basketball player performance
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the performance predictor
        
        :param model_path: Optional path to pre-trained model
        """
        self.model_path = model_path or os.path.join('models', 'basketball_predictor.pkl')
        
        # Ensure models directory exists
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # Model configurations
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        
        self.scaler = StandardScaler()
        self.current_model = None
        
        # Load existing model if available
        self.load_model()
    
    def prepare_training_data(self, player_data: Dict[str, Any]) -> tuple:
        """
        Prepare and preprocess training data
        
        :param player_data: Dictionary of player performance data
        :return: Tuple of (X_train, X_test, y_train, y_test)
        """
        # Extract relevant features
        features = [
            'age', 'games_played', 'minutes_played', 
            'field_goal_percentage', 'three_point_percentage', 
            'free_throw_percentage', 'rebounds', 'assists'
        ]
        
        # Simulate data extraction (replace with actual data retrieval)
        X = np.array([
            [player['age'], player['games_played'], player['minutes_played'], 
             player['field_goal_percentage'], player['three_point_percentage'], 
             player['free_throw_percentage'], player['rebounds'], player['assists']]
            for player in player_data
        ])
        
        # Target variable (points per game)
        y = np.array([player['points_per_game'] for player in player_data])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def train_model(self, player_data: Dict[str, Any], model_type: str = 'random_forest'):
        """
        Train a machine learning model for performance prediction
        
        :param player_data: Dictionary of player performance data
        :param model_type: Type of model to train
        """
        # Prepare training data
        X_train, X_test, y_train, y_test = self.prepare_training_data(player_data)
        
        # Select model
        self.current_model = self.models.get(model_type, self.models['random_forest'])
        
        # Train model
        self.current_model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.current_model.predict(X_test)
        
        metrics = {
            'mean_absolute_error': mean_absolute_error(y_test, y_pred),
            'mean_squared_error': mean_squared_error(y_test, y_pred),
            'r2_score': r2_score(y_test, y_pred)
        }
        
        # Save model
        self.save_model()
        
        return metrics
    
    def predict_performance(self, player_features: np.ndarray) -> float:
        """
        Predict player performance
        
        :param player_features: Numpy array of player features
        :return: Predicted points per game
        """
        if self.current_model is None:
            raise ValueError("No trained model available. Train a model first.")
        
        # Scale features
        scaled_features = self.scaler.transform(player_features.reshape(1, -1))
        
        # Predict
        prediction = self.current_model.predict(scaled_features)[0]
        
        return prediction
    
    def save_model(self):
        """Save trained model and scaler"""
        if self.current_model:
            joblib.dump({
                'model': self.current_model,
                'scaler': self.scaler
            }, self.model_path)
    
    def load_model(self):
        """Load pre-trained model if available"""
        if os.path.exists(self.model_path):
            try:
                saved_data = joblib.load(self.model_path)
                self.current_model = saved_data['model']
                self.scaler = saved_data['scaler']
                print("✅ Pre-trained model loaded successfully")
            except Exception as e:
                print(f"❌ Error loading model: {e}")
    
    def generate_synthetic_player_data(self, num_players: int = 1000) -> Dict[str, Any]:
        """
        Generate synthetic player performance data for training
        
        :param num_players: Number of synthetic players to generate
        :return: List of player dictionaries
        """
        np.random.seed(42)
        
        synthetic_data = []
        for _ in range(num_players):
            player = {
                'age': np.random.uniform(19, 40),
                'games_played': np.random.randint(10, 82),
                'minutes_played': np.random.uniform(10, 40),
                'field_goal_percentage': np.random.uniform(0.4, 0.6),
                'three_point_percentage': np.random.uniform(0.3, 0.45),
                'free_throw_percentage': np.random.uniform(0.7, 0.9),
                'rebounds': np.random.uniform(2, 15),
                'assists': np.random.uniform(1, 10),
                'points_per_game': np.random.uniform(5, 30)
            }
            synthetic_data.append(player)
        
        return synthetic_data

# Example usage and demonstration
def main():
    predictor = BasketballPerformancePredictor()
    
    # Generate synthetic training data
    synthetic_data = predictor.generate_synthetic_player_data()
    
    # Train model
    metrics = predictor.train_model(synthetic_data)
    print("Training Metrics:", metrics)
    
    # Example prediction
    lebron_features = np.array([
        29,  # age
        70,  # games played
        35,  # minutes played
        0.54,  # field goal %
        0.35,  # 3-point %
        0.75,  # free throw %
        7.5,  # rebounds
        7.2   # assists
    ])
    
    predicted_ppg = predictor.predict_performance(lebron_features)
    print(f"Predicted Points Per Game: {predicted_ppg:.2f}")

if __name__ == "__main__":
    main()

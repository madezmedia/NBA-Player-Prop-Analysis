import os
import json
import pickle
import joblib
import mlflow
import mlflow.pyfunc
from typing import Dict, Any, Optional, Union
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

from utils.logger import AdvancedLogger
from utils.error_handler import ErrorHandler
from utils.config_manager import ConfigManager

class PlayerPerformanceInput(BaseModel):
    """
    Pydantic model for player performance prediction input
    """
    age: float = Field(..., gt=0, le=50)
    games_played: int = Field(..., gt=0, le=100)
    minutes_played: float = Field(..., gt=0, le=48)
    field_goal_percentage: float = Field(..., ge=0, le=1)
    three_point_percentage: float = Field(..., ge=0, le=1)
    free_throw_percentage: float = Field(..., ge=0, le=1)
    rebounds: float = Field(..., ge=0, le=20)
    assists: float = Field(..., ge=0, le=15)

class ModelDeploymentManager:
    """
    Advanced model deployment and serving utility
    """
    
    def __init__(
        self, 
        config_manager: Optional[ConfigManager] = None,
        logger: Optional[AdvancedLogger] = None,
        error_handler: Optional[ErrorHandler] = None
    ):
        """
        Initialize model deployment manager
        
        :param config_manager: Configuration management utility
        :param logger: Logging utility
        :param error_handler: Error handling utility
        """
        self.config_manager = config_manager or ConfigManager()
        self.logger = logger or AdvancedLogger()
        self.error_handler = error_handler or ErrorHandler()
        
        # Deployment configuration
        self.deployment_config = {
            'models_dir': os.path.join(os.getcwd(), 'deployed_models'),
            'serving_dir': os.path.join(os.getcwd(), 'model_serving')
        }
        
        # Create necessary directories
        for dir_path in self.deployment_config.values():
            os.makedirs(dir_path, exist_ok=True)
    
    def save_model(
        self, 
        model, 
        model_name: str, 
        model_version: Optional[str] = None
    ) -> str:
        """
        Save a machine learning model with versioning
        
        :param model: Model to save
        :param model_name: Name of the model
        :param model_version: Optional version identifier
        :return: Path to saved model
        """
        try:
            # Generate model filename
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            version = model_version or timestamp
            
            # Create model-specific directory
            model_dir = os.path.join(
                self.deployment_config['models_dir'], 
                model_name
            )
            os.makedirs(model_dir, exist_ok=True)
            
            # Save model paths
            model_filename = f"{model_name}_v{version}.pkl"
            model_path = os.path.join(model_dir, model_filename)
            
            # Save model using joblib
            joblib.dump(model, model_path)
            
            # Log model metadata
            metadata = {
                'model_name': model_name,
                'version': version,
                'timestamp': timestamp,
                'path': model_path
            }
            
            metadata_path = os.path.join(model_dir, f"{model_name}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.log_event(
                "Model saved", 
                level='info', 
                model_name=model_name, 
                version=version
            )
            
            return model_path
        
        except Exception as e:
            error_details = self.error_handler.handle_exception(
                e, 
                context={'operation': 'save_model', 'model_name': model_name}
            )
            
            self.logger.log_error(
                "Error saving model", 
                error=e, 
                **error_details
            )
            
            return None
    
    def load_model(
        self, 
        model_name: str, 
        version: Optional[str] = None
    ) -> Any:
        """
        Load a saved model
        
        :param model_name: Name of the model
        :param version: Optional version identifier
        :return: Loaded model
        """
        try:
            # Find the most recent model if no version specified
            model_dir = os.path.join(
                self.deployment_config['models_dir'], 
                model_name
            )
            
            if not os.path.exists(model_dir):
                raise FileNotFoundError(f"No models found for {model_name}")
            
            # List model files
            model_files = [
                f for f in os.listdir(model_dir) 
                if f.endswith('.pkl') and model_name in f
            ]
            
            if not model_files:
                raise FileNotFoundError(f"No model files found for {model_name}")
            
            # Sort files to get the most recent if no version specified
            if version:
                model_file = f"{model_name}_v{version}.pkl"
            else:
                model_file = sorted(model_files)[-1]
            
            model_path = os.path.join(model_dir, model_file)
            
            # Load model
            model = joblib.load(model_path)
            
            self.logger.log_event(
                "Model loaded", 
                level='info', 
                model_name=model_name, 
                version=version or 'latest'
            )
            
            return model
        
        except Exception as e:
            error_details = self.error_handler.handle_exception(
                e, 
                context={'operation': 'load_model', 'model_name': model_name}
            )
            
            self.logger.log_error(
                "Error loading model", 
                error=e, 
                **error_details
            )
            
            return None
    
    def create_model_serving_app(
        self, 
        model_name: str, 
        version: Optional[str] = None
    ) -> FastAPI:
        """
        Create a FastAPI application for model serving
        
        :param model_name: Name of the model to serve
        :param version: Optional model version
        :return: FastAPI application
        """
        try:
            # Load the model
            model = self.load_model(model_name, version)
            
            if model is None:
                raise ValueError(f"Could not load model {model_name}")
            
            # Create FastAPI app
            app = FastAPI(
                title=f"{model_name.replace('_', ' ').title()} Prediction Service",
                description="Basketball Performance Prediction API"
            )
            
            @app.post("/predict")
            async def predict(input_data: PlayerPerformanceInput):
                """
                Endpoint for making predictions
                
                :param input_data: Player performance input data
                :return: Prediction result
                """
                try:
                    # Convert input to numpy array
                    input_array = np.array([
                        input_data.age,
                        input_data.games_played,
                        input_data.minutes_played,
                        input_data.field_goal_percentage,
                        input_data.three_point_percentage,
                        input_data.free_throw_percentage,
                        input_data.rebounds,
                        input_data.assists
                    ]).reshape(1, -1)
                    
                    # Make prediction
                    prediction = model.predict(input_array)[0]
                    
                    return {
                        "predicted_points_per_game": float(prediction),
                        "model_name": model_name,
                        "model_version": version or "latest"
                    }
                
                except Exception as e:
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Prediction error: {str(e)}"
                    )
            
            self.logger.log_event(
                "Model serving app created", 
                level='info', 
                model_name=model_name
            )
            
            return app
        
        except Exception as e:
            error_details = self.error_handler.handle_exception(
                e, 
                context={'operation': 'create_model_serving_app', 'model_name': model_name}
            )
            
            self.logger.log_error(
                "Error creating model serving app", 
                error=e, 
                **error_details
            )
            
            return None
    
    def start_model_server(
        self, 
        model_name: str, 
        version: Optional[str] = None, 
        host: str = "0.0.0.0", 
        port: int = 8000
    ):
        """
        Start a model serving server
        
        :param model_name: Name of the model to serve
        :param version: Optional model version
        :param host: Server host
        :param port: Server port
        """
        try:
            # Create serving app
            app = self.create_model_serving_app(model_name, version)
            
            if app is None:
                raise ValueError("Could not create model serving app")
            
            # Start server
            uvicorn.run(
                app, 
                host=host, 
                port=port
            )
        
        except Exception as e:
            error_details = self.error_handler.handle_exception(
                e, 
                context={'operation': 'start_model_server', 'model_name': model_name}
            )
            
            self.logger.log_error(
                "Error starting model server", 
                error=e, 
                **error_details
            )

# Example usage and demonstration
def main():
    # Initialize Model Deployment Manager
    deployment_manager = ModelDeploymentManager()
    
    # Simulate model training
    from utils.ai_models import BasketballPerformancePredictor
    predictor = BasketballPerformancePredictor()
    synthetic_data = predictor.generate_synthetic_player_data()
    
    # Train model
    predictor.train_model(synthetic_data)
    
    # Save model
    model_path = deployment_manager.save_model(
        predictor.current_model, 
        "basketball_performance_predictor"
    )
    
    # Load model
    loaded_model = deployment_manager.load_model(
        "basketball_performance_predictor"
    )
    
    # Optional: Start model server
    # deployment_manager.start_model_server(
    #     "basketball_performance_predictor"
    # )

if __name__ == "__main__":
    main()

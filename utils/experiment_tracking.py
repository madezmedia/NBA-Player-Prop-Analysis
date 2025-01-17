import os
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import mlflow
import joblib
from utils.logger import AdvancedLogger
from utils.error_handler import ErrorHandler

class ExperimentTracker:
    """
    Advanced experiment tracking and model registry utility
    """
    
    def __init__(
        self, 
        experiment_name: str = 'BasketballAIAnalysis',
        base_dir: Optional[str] = None,
        logger: Optional[AdvancedLogger] = None,
        error_handler: Optional[ErrorHandler] = None
    ):
        """
        Initialize experiment tracking
        
        :param experiment_name: Name of the experiment
        :param base_dir: Base directory for experiment storage
        :param logger: Optional logging utility
        :param error_handler: Optional error handling utility
        """
        # Logging and Error Handling
        self.logger = logger or AdvancedLogger()
        self.error_handler = error_handler or ErrorHandler()
        
        # Experiment Configuration
        self.experiment_name = experiment_name
        self.base_dir = base_dir or os.path.join(os.getcwd(), 'experiments')
        os.makedirs(self.base_dir, exist_ok=True)
        
        # MLflow Configuration
        mlflow.set_tracking_uri(f"file:{self.base_dir}")
        mlflow.set_experiment(experiment_name)
    
    def start_run(
        self, 
        run_name: Optional[str] = None, 
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Start a new experiment run
        
        :param run_name: Optional name for the run
        :param tags: Optional tags for the run
        :return: Run ID
        """
        try:
            # Generate unique run name if not provided
            run_name = run_name or f"run_{uuid.uuid4().hex[:8]}"
            
            # Start MLflow run
            mlflow.start_run(run_name=run_name)
            
            # Log tags if provided
            if tags:
                for key, value in tags.items():
                    mlflow.set_tag(key, value)
            
            # Log run metadata
            run = mlflow.active_run()
            run_id = run.info.run_id
            
            self.logger.log_event(
                "Experiment run started", 
                level='info', 
                run_id=run_id, 
                run_name=run_name
            )
            
            return run_id
        
        except Exception as e:
            error_details = self.error_handler.handle_exception(
                e, 
                context={'operation': 'start_run'}
            )
            
            self.logger.log_error(
                "Error starting experiment run", 
                error=e, 
                **error_details
            )
            
            return None
    
    def log_metrics(
        self, 
        metrics: Dict[str, float], 
        step: Optional[int] = None
    ):
        """
        Log metrics for the current run
        
        :param metrics: Dictionary of metrics to log
        :param step: Optional step number for tracking
        """
        try:
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value, step=step)
            
            self.logger.log_event(
                "Metrics logged", 
                level='info', 
                metrics=list(metrics.keys())
            )
        
        except Exception as e:
            self.logger.log_error(
                "Error logging metrics", 
                error=e
            )
    
    def log_parameters(self, parameters: Dict[str, Any]):
        """
        Log parameters for the current run
        
        :param parameters: Dictionary of parameters to log
        """
        try:
            for param_name, param_value in parameters.items():
                mlflow.log_param(param_name, param_value)
            
            self.logger.log_event(
                "Parameters logged", 
                level='info', 
                parameters=list(parameters.keys())
            )
        
        except Exception as e:
            self.logger.log_error(
                "Error logging parameters", 
                error=e
            )
    
    def log_artifact(
        self, 
        local_path: str, 
        artifact_path: Optional[str] = None
    ):
        """
        Log an artifact for the current run
        
        :param local_path: Path to the local artifact
        :param artifact_path: Optional path within the artifact store
        """
        try:
            mlflow.log_artifact(local_path, artifact_path)
            
            self.logger.log_event(
                "Artifact logged", 
                level='info', 
                local_path=local_path, 
                artifact_path=artifact_path
            )
        
        except Exception as e:
            self.logger.log_error(
                "Error logging artifact", 
                error=e
            )
    
    def end_run(self, status: str = 'FINISHED'):
        """
        End the current experiment run
        
        :param status: Run status (FINISHED, FAILED, etc.)
        """
        try:
            mlflow.end_run(status)
            
            self.logger.log_event(
                "Experiment run ended", 
                level='info', 
                status=status
            )
        
        except Exception as e:
            self.logger.log_error(
                "Error ending experiment run", 
                error=e
            )
    
    def save_model(
        self, 
        model, 
        model_name: str, 
        model_path: Optional[str] = None
    ):
        """
        Save a machine learning model
        
        :param model: Model to save
        :param model_name: Name of the model
        :param model_path: Optional custom save path
        """
        try:
            # Generate default path if not provided
            if model_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                model_path = os.path.join(
                    self.base_dir, 
                    'models', 
                    f"{model_name}_{timestamp}.pkl"
                )
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            # Save model
            joblib.dump(model, model_path)
            
            # Log model as MLflow artifact
            mlflow.log_artifact(model_path)
            
            self.logger.log_event(
                "Model saved", 
                level='info', 
                model_name=model_name, 
                model_path=model_path
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
    
    def list_experiments(self) -> List[Dict[str, Any]]:
        """
        List all experiments
        
        :return: List of experiment details
        """
        try:
            client = mlflow.tracking.MlflowClient()
            experiments = client.list_experiments()
            
            return [
                {
                    'experiment_id': exp.experiment_id,
                    'name': exp.name,
                    'artifact_location': exp.artifact_location,
                    'lifecycle_stage': exp.lifecycle_stage
                }
                for exp in experiments
            ]
        
        except Exception as e:
            self.logger.log_error(
                "Error listing experiments", 
                error=e
            )
            
            return []

# Example usage and demonstration
def main():
    # Initialize Experiment Tracker
    tracker = ExperimentTracker()
    
    # Start a new run
    run_id = tracker.start_run(
        run_name="basketball_model_training", 
        tags={"model_type": "performance_predictor"}
    )
    
    try:
        # Simulate model training
        from utils.ai_models import BasketballPerformancePredictor
        predictor = BasketballPerformancePredictor()
        synthetic_data = predictor.generate_synthetic_player_data()
        
        # Train model
        metrics = predictor.train_model(synthetic_data)
        
        # Log metrics and parameters
        tracker.log_metrics(metrics)
        tracker.log_parameters({
            "model_type": "random_forest",
            "n_estimators": 100,
            "random_state": 42
        })
        
        # Save model
        model_path = tracker.save_model(
            predictor.current_model, 
            "basketball_performance_predictor"
        )
        
        # End run
        tracker.end_run()
        
        # List experiments
        experiments = tracker.list_experiments()
        print("Experiments:", experiments)
    
    except Exception as e:
        tracker.end_run(status='FAILED')
        print(f"Error in experiment tracking demonstration: {e}")

if __name__ == "__main__":
    main()

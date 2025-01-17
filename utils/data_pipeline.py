import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from utils.api_integration import BasketballAPIIntegration
from utils.statistical_analysis import BasketballStatisticalAnalyzer
from utils.data_processor import DataProcessor
from utils.logger import AdvancedLogger
from utils.error_handler import ErrorHandler

class BasketballDataPipeline:
    """
    Advanced data pipeline for comprehensive basketball performance data processing
    """
    
    def __init__(
        self, 
        api_integration: Optional[BasketballAPIIntegration] = None,
        data_processor: Optional[DataProcessor] = None,
        logger: Optional[AdvancedLogger] = None,
        error_handler: Optional[ErrorHandler] = None
    ):
        """
        Initialize the data pipeline
        
        :param api_integration: Optional API integration utility
        :param data_processor: Optional data processing utility
        :param logger: Optional logging utility
        :param error_handler: Optional error handling utility
        """
        self.api_integration = api_integration or BasketballAPIIntegration()
        self.data_processor = data_processor or DataProcessor()
        self.logger = logger or AdvancedLogger()
        self.error_handler = error_handler or ErrorHandler()
        
        # Pipeline configuration
        self.pipeline_config = {
            'cache_dir': os.path.join(os.getcwd(), 'data_cache'),
            'raw_data_dir': os.path.join(os.getcwd(), 'raw_data'),
            'processed_data_dir': os.path.join(os.getcwd(), 'processed_data')
        }
        
        # Create necessary directories
        for dir_path in self.pipeline_config.values():
            os.makedirs(dir_path, exist_ok=True)
    
    def fetch_player_data(
        self, 
        players: Union[str, List[str]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch and process player data
        
        :param players: Single player name or list of player names
        :return: Processed player data dictionary
        """
        try:
            # Handle single player or multiple players
            if isinstance(players, str):
                players = [players]
            
            # Fetch player data asynchronously
            async def get_player_stats():
                return await self.api_integration.fetch_player_stats_async(players)
            
            import asyncio
            player_stats = asyncio.run(get_player_stats())
            
            # Process and enrich player data
            processed_stats = {}
            for player, stats in player_stats.items():
                # Add statistical analysis
                stats['statistical_analysis'] = self._analyze_player_stats(stats)
                
                # Cache processed data
                self._cache_player_data(player, stats)
                
                processed_stats[player] = stats
            
            self.logger.log_event(
                f"Processed data for {len(players)} players", 
                level='info', 
                players=players
            )
            
            return processed_stats
        
        except Exception as e:
            error_details = self.error_handler.handle_exception(
                e, 
                context={'players': players}
            )
            
            self.logger.log_error(
                "Error in player data pipeline", 
                error=e, 
                **error_details
            )
            
            return {}
    
    def _analyze_player_stats(
        self, 
        player_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform advanced statistical analysis on player data
        
        :param player_stats: Player statistics dictionary
        :return: Statistical analysis results
        """
        try:
            # Extract relevant metrics for analysis
            metrics = [
                player_stats['stats'].get('points_per_game', 0),
                player_stats['stats'].get('rebounds_per_game', 0),
                player_stats['stats'].get('assists_per_game', 0)
            ]
            
            return {
                'z_scores': [
                    BasketballStatisticalAnalyzer.calculate_z_score(metrics, metric) 
                    for metric in metrics
                ],
                'percentiles': BasketballStatisticalAnalyzer.calculate_percentiles(metrics),
                'consistency': BasketballStatisticalAnalyzer.performance_consistency(metrics),
                'outliers': BasketballStatisticalAnalyzer.outlier_detection(metrics)
            }
        
        except Exception as e:
            self.logger.log_error(
                "Error analyzing player stats", 
                error=e
            )
            return {}
    
    def _cache_player_data(
        self, 
        player_name: str, 
        player_data: Dict[str, Any]
    ):
        """
        Cache processed player data
        
        :param player_name: Name of the player
        :param player_data: Processed player data
        """
        try:
            # Create player-specific cache file
            cache_filename = f"{player_name.replace(' ', '_')}_stats.json"
            cache_path = os.path.join(
                self.pipeline_config['cache_dir'], 
                cache_filename
            )
            
            # Use data processor to export data
            self.data_processor.export_player_data(
                player_name, 
                export_format='json', 
                output_path=cache_path
            )
            
            self.logger.log_event(
                f"Cached data for {player_name}", 
                level='info', 
                player=player_name, 
                cache_path=cache_path
            )
        
        except Exception as e:
            self.logger.log_error(
                f"Error caching data for {player_name}", 
                error=e
            )
    
    def compare_players(
        self, 
        players: List[str]
    ) -> Dict[str, Any]:
        """
        Compare multiple players' performance
        
        :param players: List of player names
        :return: Comparative analysis results
        """
        try:
            # Fetch player data
            player_data = self.fetch_player_data(players)
            
            # Prepare comparison data
            comparison_results = {
                'basic_stats': {},
                'advanced_metrics': {},
                'statistical_analysis': {}
            }
            
            for player, stats in player_data.items():
                comparison_results['basic_stats'][player] = stats.get('stats', {})
                comparison_results['advanced_metrics'][player] = stats.get('advanced_metrics', {})
                comparison_results['statistical_analysis'][player] = stats.get('statistical_analysis', {})
            
            return comparison_results
        
        except Exception as e:
            error_details = self.error_handler.handle_exception(
                e, 
                context={'players': players}
            )
            
            self.logger.log_error(
                "Error comparing players", 
                error=e, 
                **error_details
            )
            
            return {}
    
    def generate_performance_report(
        self, 
        players: List[str]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive performance report
        
        :param players: List of player names
        :return: Detailed performance report
        """
        try:
            # Fetch and compare player data
            comparison_data = self.compare_players(players)
            
            # Generate report
            performance_report = {
                'players': players,
                'comparison': comparison_data,
                'report_timestamp': pd.Timestamp.now().isoformat()
            }
            
            # Export report
            report_filename = f"performance_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path = os.path.join(
                self.pipeline_config['processed_data_dir'], 
                report_filename
            )
            
            # Save report
            import json
            with open(report_path, 'w') as f:
                json.dump(performance_report, f, indent=2)
            
            self.logger.log_event(
                "Generated performance report", 
                level='info', 
                players=players, 
                report_path=report_path
            )
            
            return performance_report
        
        except Exception as e:
            error_details = self.error_handler.handle_exception(
                e, 
                context={'players': players}
            )
            
            self.logger.log_error(
                "Error generating performance report", 
                error=e, 
                **error_details
            )
            
            return {}

# Example usage and demonstration
def main():
    # Initialize Data Pipeline
    pipeline = BasketballDataPipeline()
    
    # Fetch Player Data
    players = ["LeBron James", "Stephen Curry", "Kevin Durant"]
    player_data = pipeline.fetch_player_data(players)
    print("Player Data:", player_data)
    
    # Compare Players
    comparison = pipeline.compare_players(players)
    print("Player Comparison:", comparison)
    
    # Generate Performance Report
    performance_report = pipeline.generate_performance_report(players)
    print("Performance Report:", performance_report)

if __name__ == "__main__":
    main()

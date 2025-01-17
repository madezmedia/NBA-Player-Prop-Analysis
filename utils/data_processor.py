import os
import json
import hashlib
from functools import lru_cache
from typing import Dict, Any
import cachetools

class DataProcessor:
    """
    Utility class for processing and caching basketball data
    """
    
    def __init__(self, cache_size: int = 100):
        """
        Initialize DataProcessor with configurable cache
        
        :param cache_size: Maximum number of items to cache
        """
        # Create a LRU cache for player statistics
        self.player_stats_cache = cachetools.LRUCache(maxsize=cache_size)
    
    def get_cached_player_stats(self, player_name: str) -> Dict[str, Any]:
        """
        Cached method to retrieve player statistics
        
        :param player_name: Name of the player
        :return: Dictionary of player statistics
        """
        # Check if stats are already in cache
        cache_key = self.generate_cache_key({'player': player_name})
        
        if cache_key in self.player_stats_cache:
            return self.player_stats_cache[cache_key]
        
        # In a real implementation, this would fetch from an API or database
        player_stats = {
            'name': player_name,
            'ppg': 25.0,
            'rpg': 7.5,
            'apg': 6.2,
            'advanced_metrics': {
                'PER': 22.5,
                'win_shares': 7.2,
                'box_plus_minus': 6.5
            }
        }
        
        # Store in cache
        self.player_stats_cache[cache_key] = player_stats
        return player_stats
    
    @staticmethod
    def generate_cache_key(data: Dict[str, Any]) -> str:
        """
        Generate a unique cache key based on input data
        
        :param data: Dictionary of data to generate key for
        :return: Hashed cache key
        """
        # Convert dictionary to a sorted, hashable representation
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def process_player_comparison(self, player1: str, player2: str) -> Dict[str, Any]:
        """
        Process and compare two players' statistics
        
        :param player1: Name of first player
        :param player2: Name of second player
        :return: Comparison dictionary
        """
        # Retrieve stats for both players
        player1_stats = self.get_cached_player_stats(player1)
        player2_stats = self.get_cached_player_stats(player2)
        
        return {
            'basic_stats': {
                'points_per_game': [
                    player1_stats.get('ppg', 0),
                    player2_stats.get('ppg', 0)
                ],
                'rebounds_per_game': [
                    player1_stats.get('rpg', 0),
                    player2_stats.get('rpg', 0)
                ],
                'assists_per_game': [
                    player1_stats.get('apg', 0),
                    player2_stats.get('apg', 0)
                ]
            },
            'advanced_metrics': {
                'PER': [
                    player1_stats.get('advanced_metrics', {}).get('PER', 0),
                    player2_stats.get('advanced_metrics', {}).get('PER', 0)
                ],
                'win_shares': [
                    player1_stats.get('advanced_metrics', {}).get('win_shares', 0),
                    player2_stats.get('advanced_metrics', {}).get('win_shares', 0)
                ]
            }
        }
    
    def export_player_data(self, player_name: str, export_format: str = 'json') -> str:
        """
        Export player data to a specified format
        
        :param player_name: Name of the player
        :param export_format: Format to export data (json, csv)
        :return: Path to exported file
        """
        # Retrieve player stats
        player_stats = self.get_cached_player_stats(player_name)
        
        # Create export directory if it doesn't exist
        export_dir = os.path.join(os.getcwd(), 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        # Export based on format
        if export_format == 'json':
            export_path = os.path.join(export_dir, f"{player_name.replace(' ', '_')}_stats.json")
            with open(export_path, 'w') as f:
                json.dump(player_stats, f, indent=2)
            return export_path
        
        elif export_format == 'csv':
            export_path = os.path.join(export_dir, f"{player_name.replace(' ', '_')}_stats.csv")
            import csv
            
            with open(export_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value'])
                
                # Flatten and write stats
                for key, value in player_stats.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            writer.writerow([f"{key}_{sub_key}", sub_value])
                    else:
                        writer.writerow([key, value])
            
            return export_path
        
        else:
            raise ValueError(f"Unsupported export format: {export_format}")

# Example usage
if __name__ == "__main__":
    processor = DataProcessor()
    
    # Retrieve and cache player stats
    lebron_stats = processor.get_cached_player_stats("LeBron James")
    print("LeBron James Stats:", lebron_stats)
    
    # Compare players
    comparison = processor.process_player_comparison("LeBron James", "Stephen Curry")
    print("Player Comparison:", comparison)
    
    # Export player data
    json_export = processor.export_player_data("LeBron James", 'json')
    csv_export = processor.export_player_data("LeBron James", 'csv')
    print(f"Exported to JSON: {json_export}")
    print(f"Exported to CSV: {csv_export}")

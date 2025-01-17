import os
import requests
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from utils.error_handler import ErrorHandler
from utils.logger import AdvancedLogger

class BasketballAPIIntegration:
    """
    Advanced API integration utility for retrieving basketball performance data
    """
    
    def __init__(self, 
                 rapidapi_key: Optional[str] = None, 
                 logger: Optional[AdvancedLogger] = None,
                 error_handler: Optional[ErrorHandler] = None
    ):
        """
        Initialize API integration
        
        :param rapidapi_key: RapidAPI key for authentication
        :param logger: Optional logger for tracking API interactions
        :param error_handler: Optional error handling utility
        """
        # Load environment variables
        load_dotenv()
        
        # API Configuration
        self.rapidapi_key = rapidapi_key or os.getenv('RAPIDAPI_KEY')
        self.headers = {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": "basketball-head.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        
        # Base URLs
        self.base_urls = {
            'players': "https://basketball-head.p.rapidapi.com/players/searchv2",
            'team_stats': "https://basketball-head.p.rapidapi.com/teams/stats",
            'game_stats': "https://basketball-head.p.rapidapi.com/games/stats"
        }
        
        # Logging and Error Handling
        self.logger = logger or AdvancedLogger()
        self.error_handler = error_handler or ErrorHandler()
    
    @ErrorHandler.retry(max_attempts=3, delay=1.0, backoff=2.0)
    def fetch_player_stats(self, player_name: str) -> Dict[str, Any]:
        """
        Fetch detailed player statistics
        
        :param player_name: Name of the player
        :return: Dictionary of player statistics
        """
        try:
            response = requests.post(
                self.base_urls['players'], 
                json={"query": player_name}, 
                headers=self.headers
            )
            
            response.raise_for_status()
            player_data = response.json()
            
            # Log successful API call
            self.logger.log_event(
                f"Player stats retrieved for {player_name}", 
                level='info', 
                player=player_name
            )
            
            return self._process_player_data(player_data)
        
        except requests.exceptions.RequestException as e:
            # Handle and log API errors
            error_details = self.error_handler.handle_exception(
                e, 
                context={'player': player_name, 'api_endpoint': 'players'}
            )
            
            self.logger.log_error(
                f"Error fetching player stats for {player_name}", 
                error=e, 
                **error_details
            )
            
            return {}
    
    async def fetch_player_stats_async(
        self, 
        player_names: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Asynchronously fetch player statistics
        
        :param player_names: List of player names
        :return: Dictionary of player statistics
        """
        async def fetch_player(session: aiohttp.ClientSession, name: str):
            try:
                async with session.post(
                    self.base_urls['players'], 
                    json={"query": name}, 
                    headers=self.headers
                ) as response:
                    response.raise_for_status()
                    player_data = await response.json()
                    return name, self._process_player_data(player_data)
            except Exception as e:
                self.logger.log_error(
                    f"Async player stats error for {name}", 
                    error=e
                )
                return name, {}
        
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_player(session, name) for name in player_names]
            results = await asyncio.gather(*tasks)
            
            return dict(results)
    
    def _process_player_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and standardize player data
        
        :param raw_data: Raw API response
        :return: Processed player data
        """
        try:
            # Extract and transform relevant data
            processed_data = {
                'name': raw_data.get('name', 'Unknown'),
                'team': raw_data.get('team', 'Unknown'),
                'stats': {
                    'points_per_game': raw_data.get('ppg', 0),
                    'rebounds_per_game': raw_data.get('rpg', 0),
                    'assists_per_game': raw_data.get('apg', 0),
                    'field_goal_percentage': raw_data.get('fg_pct', 0),
                    'three_point_percentage': raw_data.get('three_pct', 0)
                },
                'advanced_metrics': {
                    'player_efficiency_rating': raw_data.get('per', 0),
                    'true_shooting_percentage': raw_data.get('ts_pct', 0)
                }
            }
            
            return processed_data
        
        except Exception as e:
            self.logger.log_error(
                "Error processing player data", 
                error=e
            )
            return {}
    
    def fetch_team_stats(self, team_name: str) -> Dict[str, Any]:
        """
        Fetch team statistics
        
        :param team_name: Name of the team
        :return: Dictionary of team statistics
        """
        try:
            response = requests.get(
                self.base_urls['team_stats'], 
                params={"team": team_name}, 
                headers=self.headers
            )
            
            response.raise_for_status()
            team_data = response.json()
            
            self.logger.log_event(
                f"Team stats retrieved for {team_name}", 
                level='info', 
                team=team_name
            )
            
            return team_data
        
        except requests.exceptions.RequestException as e:
            error_details = self.error_handler.handle_exception(
                e, 
                context={'team': team_name, 'api_endpoint': 'team_stats'}
            )
            
            self.logger.log_error(
                f"Error fetching team stats for {team_name}", 
                error=e, 
                **error_details
            )
            
            return {}

# Example usage and demonstration
def main():
    # Initialize API Integration
    api_integration = BasketballAPIIntegration()
    
    # Synchronous Player Stats Retrieval
    lebron_stats = api_integration.fetch_player_stats("LeBron James")
    print("LeBron James Stats:", lebron_stats)
    
    # Asynchronous Player Stats Retrieval
    async def async_demo():
        players = ["LeBron James", "Stephen Curry", "Kevin Durant"]
        async_stats = await api_integration.fetch_player_stats_async(players)
        print("Async Player Stats:", async_stats)
    
    # Run async demo
    asyncio.run(async_demo())
    
    # Team Stats Retrieval
    lakers_stats = api_integration.fetch_team_stats("Los Angeles Lakers")
    print("Lakers Team Stats:", lakers_stats)

if __name__ == "__main__":
    main()

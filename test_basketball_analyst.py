import unittest
import sys
import os
import pytest

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import BasketballAnalyst

class TestBasketballAnalyst(unittest.TestCase):
    def setUp(self):
        """Initialize the BasketballAnalyst before each test"""
        self.analyst = BasketballAnalyst()

    def test_fetch_player_stats(self):
        """Test fetching player statistics"""
        # Test with a known player
        player_name = "LeBron James"
        player_data = self.analyst.fetch_player_stats(player_name)
        
        # Assertions
        self.assertIsNotNone(player_data, f"Failed to fetch stats for {player_name}")
        
        # Check for expected keys or data structure
        expected_keys = ['ppg', 'rpg', 'apg']
        for key in expected_keys:
            self.assertIn(key, player_data, f"Missing {key} in player data")

    def test_analyze_screenshot(self):
        """Test screenshot analysis method"""
        # Note: This would typically use a test image
        # For now, we'll just check the method exists and handles errors
        from PIL import Image
        import numpy as np
        
        # Create a dummy image
        dummy_image = Image.fromarray(np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8))
        
        result = self.analyst.analyze_screenshot(dummy_image)
        self.assertIsNotNone(result, "Screenshot analysis returned None")

    def test_create_prediction_crew(self):
        """Test CrewAI prediction crew creation"""
        # Mock player data
        mock_player_data = {
            'name': 'Test Player',
            'ppg': 25.0,
            'rpg': 7.5,
            'apg': 6.2
        }
        
        prediction_result = self.analyst.create_prediction_crew(mock_player_data)
        self.assertIsNotNone(prediction_result, "Prediction crew failed to generate output")

    def test_generate_response(self):
        """Test AI response generation"""
        test_prompt = "What are LeBron James' career achievements?"
        
        response = self.analyst.generate_response(test_prompt)
        self.assertIsNotNone(response, "Failed to generate AI response")

    def test_create_performance_chart(self):
        """Test performance chart creation"""
        # Mock stats data
        mock_stats = {
            'dates': ['2022-01-01', '2022-02-01', '2022-03-01'],
            'points': [25, 28, 30]
        }
        
        chart = self.analyst.create_performance_chart(mock_stats, 'points')
        self.assertIsNotNone(chart, "Failed to create performance chart")

    def test_compare_players(self):
        """Test player comparison method"""
        comparison = self.analyst.compare_players("LeBron James", "Stephen Curry")
        
        self.assertIsNotNone(comparison, "Player comparison failed")
        
        # Check basic structure of comparison
        self.assertIn('basic_stats', comparison)
        self.assertIn('advanced_metrics', comparison)

def test_environment_variables():
    """Verify required environment variables are set"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    assert os.getenv('GROQ_API_KEY'), "GROQ_API_KEY is not set"
    assert os.getenv('RAPIDAPI_KEY'), "RAPIDAPI_KEY is not set"

if __name__ == '__main__':
    # Use pytest for more detailed test running
    pytest.main([__file__])

import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional

class BasketballVisualizer:
    """
    Advanced visualization utility for basketball performance data
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the visualizer
        
        :param output_dir: Directory to save generated visualizations
        """
        self.output_dir = output_dir or os.path.join(os.getcwd(), 'visualizations')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def player_performance_radar_chart(
        self, 
        player_data: Dict[str, float], 
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Create a radar chart for player performance metrics
        
        :param player_data: Dictionary of performance metrics
        :param title: Optional chart title
        :return: Plotly radar chart figure
        """
        # Default metrics if not all provided
        default_metrics = {
            'Points per Game': 0,
            'Rebounds per Game': 0,
            'Assists per Game': 0,
            'Steals per Game': 0,
            'Blocks per Game': 0,
            'Field Goal %': 0,
            'Three-Point %': 0
        }
        
        # Update with provided data
        default_metrics.update(player_data)
        
        # Prepare data for radar chart
        categories = list(default_metrics.keys())
        values = list(default_metrics.values())
        
        # Normalize values for better visualization
        max_values = [30, 15, 15, 3, 3, 1, 1]
        normalized_values = [
            min(val / max_val * 100, 100) 
            for val, max_val in zip(values, max_values)
        ]
        
        fig = go.Figure(data=go.Scatterpolar(
            r=normalized_values,
            theta=categories,
            fill='toself'
        ))
        
        fig.update_layout(
            title=title or 'Player Performance Metrics',
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False
        )
        
        return fig
    
    def player_comparison_bar_chart(
        self, 
        players_data: Dict[str, Dict[str, float]], 
        metrics: Optional[List[str]] = None
    ) -> go.Figure:
        """
        Create a grouped bar chart comparing players across metrics
        
        :param players_data: Dictionary of player performance data
        :param metrics: List of metrics to compare
        :return: Plotly bar chart figure
        """
        # Default metrics if not specified
        default_metrics = [
            'Points per Game', 
            'Rebounds per Game', 
            'Assists per Game', 
            'Field Goal %'
        ]
        
        metrics = metrics or default_metrics
        
        # Prepare data for plotting
        player_names = list(players_data.keys())
        data = []
        
        for metric in metrics:
            metric_values = [
                players_data[player].get(metric, 0) 
                for player in player_names
            ]
            
            data.append(
                go.Bar(
                    name=metric, 
                    x=player_names, 
                    y=metric_values
                )
            )
        
        fig = go.Figure(data=data)
        
        fig.update_layout(
            title='Player Performance Comparison',
            xaxis_title='Players',
            yaxis_title='Performance Value',
            barmode='group'
        )
        
        return fig
    
    def career_trajectory_line_chart(
        self, 
        player_stats: List[Dict[str, Any]], 
        metric: str = 'Points per Game'
    ) -> go.Figure:
        """
        Create a line chart showing a player's performance over time
        
        :param player_stats: List of player statistics over seasons
        :param metric: Metric to track over time
        :return: Plotly line chart figure
        """
        # Ensure data is sorted by season
        sorted_stats = sorted(player_stats, key=lambda x: x.get('season', 0))
        
        seasons = [str(stat.get('season', '')) for stat in sorted_stats]
        values = [stat.get(metric, 0) for stat in sorted_stats]
        
        fig = go.Figure(data=go.Scatter(
            x=seasons, 
            y=values, 
            mode='lines+markers',
            name=metric
        ))
        
        fig.update_layout(
            title=f'{metric} Over Career',
            xaxis_title='Season',
            yaxis_title=metric
        )
        
        return fig
    
    def save_figure(
        self, 
        figure: go.Figure, 
        filename: str, 
        format: str = 'html'
    ) -> str:
        """
        Save a Plotly figure to a file
        
        :param figure: Plotly figure to save
        :param filename: Output filename
        :param format: File format (html, png, svg)
        :return: Path to saved file
        """
        # Ensure filename has correct extension
        if not filename.endswith(f'.{format}'):
            filename = f'{filename}.{format}'
        
        filepath = os.path.join(self.output_dir, filename)
        
        if format == 'html':
            figure.write_html(filepath)
        elif format == 'png':
            figure.write_image(filepath)
        elif format == 'svg':
            figure.write_image(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return filepath

# Example usage and demonstration
def main():
    visualizer = BasketballVisualizer()
    
    # Player Performance Radar Chart
    lebron_data = {
        'Points per Game': 25.5,
        'Rebounds per Game': 7.8,
        'Assists per Game': 7.2,
        'Steals per Game': 1.5,
        'Blocks per Game': 0.6,
        'Field Goal %': 0.54,
        'Three-Point %': 0.35
    }
    
    radar_chart = visualizer.player_performance_radar_chart(
        lebron_data, 
        title="LeBron James Performance Metrics"
    )
    visualizer.save_figure(radar_chart, 'lebron_radar_chart')
    
    # Player Comparison Bar Chart
    players_comparison = {
        'LeBron James': {
            'Points per Game': 25.5,
            'Rebounds per Game': 7.8,
            'Assists per Game': 7.2,
            'Field Goal %': 0.54
        },
        'Stephen Curry': {
            'Points per Game': 27.3,
            'Rebounds per Game': 5.2,
            'Assists per Game': 6.3,
            'Field Goal %': 0.48
        }
    }
    
    comparison_chart = visualizer.player_comparison_bar_chart(players_comparison)
    visualizer.save_figure(comparison_chart, 'player_comparison')
    
    # Career Trajectory Line Chart
    lebron_career_stats = [
        {'season': 2003, 'Points per Game': 20.9},
        {'season': 2004, 'Points per Game': 21.1},
        {'season': 2005, 'Points per Game': 22.5},
        # Add more seasons
    ]
    
    trajectory_chart = visualizer.career_trajectory_line_chart(
        lebron_career_stats, 
        metric='Points per Game'
    )
    visualizer.save_figure(trajectory_chart, 'lebron_career_trajectory')

if __name__ == "__main__":
    main()

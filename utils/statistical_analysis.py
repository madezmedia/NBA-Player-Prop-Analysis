import numpy as np
import pandas as pd
import scipy.stats as stats
from typing import Dict, List, Any, Optional, Tuple

class BasketballStatisticalAnalyzer:
    """
    Advanced statistical analysis utility for basketball performance data
    """
    
    @staticmethod
    def calculate_z_score(
        data: List[float], 
        value: float
    ) -> float:
        """
        Calculate Z-score for a given value in a dataset
        
        :param data: List of numerical values
        :param value: Value to calculate Z-score for
        :return: Z-score
        """
        mean = np.mean(data)
        std_dev = np.std(data)
        
        # Avoid division by zero
        if std_dev == 0:
            return 0
        
        return (value - mean) / std_dev
    
    @staticmethod
    def perform_t_test(
        group1: List[float], 
        group2: List[float]
    ) -> Dict[str, float]:
        """
        Perform independent t-test between two groups
        
        :param group1: First group of numerical values
        :param group2: Second group of numerical values
        :return: Dictionary of t-test results
        """
        t_statistic, p_value = stats.ttest_ind(group1, group2)
        
        return {
            't_statistic': t_statistic,
            'p_value': p_value,
            'statistically_significant': p_value < 0.05
        }
    
    @staticmethod
    def calculate_percentiles(
        data: List[float]
    ) -> Dict[str, float]:
        """
        Calculate key percentiles for a dataset
        
        :param data: List of numerical values
        :return: Dictionary of percentile values
        """
        return {
            '25th_percentile': np.percentile(data, 25),
            '50th_percentile': np.percentile(data, 50),  # Median
            '75th_percentile': np.percentile(data, 75),
            '90th_percentile': np.percentile(data, 90)
        }
    
    @staticmethod
    def correlation_analysis(
        x: List[float], 
        y: List[float]
    ) -> Dict[str, float]:
        """
        Perform correlation analysis between two variables
        
        :param x: First variable
        :param y: Second variable
        :return: Correlation metrics
        """
        # Pearson correlation
        pearson_corr, pearson_p = stats.pearsonr(x, y)
        
        # Spearman rank correlation
        spearman_corr, spearman_p = stats.spearmanr(x, y)
        
        return {
            'pearson_correlation': pearson_corr,
            'pearson_p_value': pearson_p,
            'spearman_correlation': spearman_corr,
            'spearman_p_value': spearman_p
        }
    
    @staticmethod
    def confidence_interval(
        data: List[float], 
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval for a dataset
        
        :param data: List of numerical values
        :param confidence_level: Confidence level (default 95%)
        :return: Tuple of (lower_bound, upper_bound)
        """
        mean = np.mean(data)
        std_error = stats.sem(data)
        
        # Calculate confidence interval
        interval = std_error * stats.t.ppf(
            (1 + confidence_level) / 2, 
            len(data) - 1
        )
        
        return (mean - interval, mean + interval)
    
    @staticmethod
    def performance_consistency(
        player_stats: List[float]
    ) -> Dict[str, float]:
        """
        Analyze performance consistency
        
        :param player_stats: List of performance values
        :return: Consistency metrics
        """
        return {
            'mean': np.mean(player_stats),
            'standard_deviation': np.std(player_stats),
            'coefficient_of_variation': (
                np.std(player_stats) / np.mean(player_stats) * 100 
                if np.mean(player_stats) != 0 else 0
            )
        }
    
    @staticmethod
    def outlier_detection(
        data: List[float], 
        method: str = 'iqr'
    ) -> Dict[str, Any]:
        """
        Detect outliers in a dataset
        
        :param data: List of numerical values
        :param method: Method for outlier detection ('iqr' or 'zscore')
        :return: Outlier detection results
        """
        if method == 'iqr':
            # Interquartile Range (IQR) method
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = [x for x in data if x < lower_bound or x > upper_bound]
            
            return {
                'method': 'IQR',
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'outliers': outliers,
                'outlier_count': len(outliers)
            }
        
        elif method == 'zscore':
            # Z-score method
            mean = np.mean(data)
            std_dev = np.std(data)
            
            z_scores = [(x - mean) / std_dev for x in data]
            outliers = [x for x, z in zip(data, z_scores) if abs(z) > 3]
            
            return {
                'method': 'Z-Score',
                'outliers': outliers,
                'outlier_count': len(outliers)
            }
        
        else:
            raise ValueError(f"Unsupported outlier detection method: {method}")

# Example usage and demonstration
def main():
    # Example player performance data
    lebron_points = [25.3, 27.1, 26.8, 24.6, 28.2, 26.5, 25.9]
    curry_points = [30.1, 29.5, 32.3, 27.8, 31.2, 28.7, 30.5]
    
    # Z-score calculation
    lebron_z_score = BasketballStatisticalAnalyzer.calculate_z_score(
        lebron_points, 
        26.5
    )
    print("LeBron Points Z-Score:", lebron_z_score)
    
    # T-test between players
    t_test_result = BasketballStatisticalAnalyzer.perform_t_test(
        lebron_points, 
        curry_points
    )
    print("T-Test Results:", t_test_result)
    
    # Percentiles
    lebron_percentiles = BasketballStatisticalAnalyzer.calculate_percentiles(
        lebron_points
    )
    print("LeBron Percentiles:", lebron_percentiles)
    
    # Correlation Analysis
    correlation = BasketballStatisticalAnalyzer.correlation_analysis(
        lebron_points, 
        curry_points
    )
    print("Player Performance Correlation:", correlation)
    
    # Confidence Interval
    conf_interval = BasketballStatisticalAnalyzer.confidence_interval(
        lebron_points
    )
    print("Performance Confidence Interval:", conf_interval)
    
    # Performance Consistency
    consistency = BasketballStatisticalAnalyzer.performance_consistency(
        lebron_points
    )
    print("Performance Consistency:", consistency)
    
    # Outlier Detection
    outliers_iqr = BasketballStatisticalAnalyzer.outlier_detection(
        lebron_points, 
        method='iqr'
    )
    print("Outliers (IQR Method):", outliers_iqr)

if __name__ == "__main__":
    main()

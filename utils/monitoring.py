import os
import time
import json
import platform
import psutil
import threading
import queue
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import sentry_sdk
from utils.logger import AdvancedLogger
from utils.error_handler import ErrorHandler

@dataclass
class SystemMetrics:
    """
    Dataclass to capture system performance metrics
    """
    timestamp: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    process_memory: float

class PerformanceMonitor:
    """
    Advanced performance monitoring and telemetry utility
    """
    
    def __init__(
        self, 
        logger: Optional[AdvancedLogger] = None,
        error_handler: Optional[ErrorHandler] = None,
        sentry_dsn: Optional[str] = None
    ):
        """
        Initialize performance monitoring
        
        :param logger: Optional logging utility
        :param error_handler: Optional error handling utility
        :param sentry_dsn: Optional Sentry DSN for error tracking
        """
        # Logging and Error Handling
        self.logger = logger or AdvancedLogger()
        self.error_handler = error_handler or ErrorHandler()
        
        # Sentry Integration
        if sentry_dsn:
            sentry_sdk.init(dsn=sentry_dsn)
        
        # Monitoring Configuration
        self.monitoring_dir = os.path.join(os.getcwd(), 'monitoring')
        os.makedirs(self.monitoring_dir, exist_ok=True)
        
        # Performance Tracking
        self.metrics_queue = queue.Queue()
        self.monitoring_thread = None
        self.is_monitoring = False
    
    def _capture_system_metrics(self) -> SystemMetrics:
        """
        Capture current system performance metrics
        
        :return: SystemMetrics dataclass
        """
        try:
            # CPU Usage
            cpu_usage = psutil.cpu_percent()
            
            # Memory Usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk Usage
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            
            # Network I/O
            net_io = psutil.net_io_counters()
            network_io = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv
            }
            
            # Process Memory
            process = psutil.Process()
            process_memory = process.memory_percent()
            
            return SystemMetrics(
                timestamp=time.time(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io,
                process_memory=process_memory
            )
        
        except Exception as e:
            self.error_handler.handle_exception(
                e, 
                context={'operation': 'system_metrics_capture'}
            )
            return None
    
    def start_monitoring(self, interval: float = 1.0):
        """
        Start continuous system performance monitoring
        
        :param interval: Monitoring interval in seconds
        """
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        
        def monitoring_worker():
            while self.is_monitoring:
                metrics = self._capture_system_metrics()
                if metrics:
                    self.metrics_queue.put(metrics)
                time.sleep(interval)
        
        self.monitoring_thread = threading.Thread(
            target=monitoring_worker, 
            daemon=True
        )
        self.monitoring_thread.start()
        
        self.logger.log_event(
            "Performance monitoring started", 
            level='info', 
            interval=interval
        )
    
    def stop_monitoring(self):
        """
        Stop continuous system performance monitoring
        """
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join()
        
        self.logger.log_event(
            "Performance monitoring stopped", 
            level='info'
        )
    
    def export_metrics(
        self, 
        output_format: str = 'json'
    ) -> str:
        """
        Export captured performance metrics
        
        :param output_format: Export file format
        :return: Path to exported metrics file
        """
        try:
            # Collect metrics from queue
            metrics_list = []
            while not self.metrics_queue.empty():
                metrics = self.metrics_queue.get()
                metrics_list.append(asdict(metrics))
            
            # Generate filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"performance_metrics_{timestamp}.{output_format}"
            filepath = os.path.join(self.monitoring_dir, filename)
            
            # Export based on format
            if output_format == 'json':
                with open(filepath, 'w') as f:
                    json.dump(metrics_list, f, indent=2)
            elif output_format == 'csv':
                import pandas as pd
                df = pd.DataFrame(metrics_list)
                df.to_csv(filepath, index=False)
            else:
                raise ValueError(f"Unsupported export format: {output_format}")
            
            self.logger.log_event(
                "Performance metrics exported", 
                level='info', 
                filepath=filepath
            )
            
            return filepath
        
        except Exception as e:
            error_details = self.error_handler.handle_exception(
                e, 
                context={'operation': 'metrics_export'}
            )
            
            self.logger.log_error(
                "Error exporting performance metrics", 
                error=e, 
                **error_details
            )
            
            return None
    
    def analyze_performance(
        self, 
        metrics: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze performance metrics
        
        :param metrics: Optional list of metrics to analyze
        :return: Performance analysis results
        """
        try:
            # Use queued metrics if not provided
            if metrics is None:
                metrics = []
                while not self.metrics_queue.empty():
                    metrics.append(asdict(self.metrics_queue.get()))
            
            if not metrics:
                return {}
            
            # Convert to DataFrame for analysis
            import pandas as pd
            df = pd.DataFrame(metrics)
            
            analysis_results = {
                'cpu_usage': {
                    'mean': df['cpu_usage'].mean(),
                    'max': df['cpu_usage'].max(),
                    'min': df['cpu_usage'].min()
                },
                'memory_usage': {
                    'mean': df['memory_usage'].mean(),
                    'max': df['memory_usage'].max(),
                    'min': df['memory_usage'].min()
                },
                'disk_usage': {
                    'mean': df['disk_usage'].mean(),
                    'max': df['disk_usage'].max(),
                    'min': df['disk_usage'].min()
                },
                'process_memory': {
                    'mean': df['process_memory'].mean(),
                    'max': df['process_memory'].max(),
                    'min': df['process_memory'].min()
                }
            }
            
            self.logger.log_event(
                "Performance metrics analyzed", 
                level='info'
            )
            
            return analysis_results
        
        except Exception as e:
            error_details = self.error_handler.handle_exception(
                e, 
                context={'operation': 'performance_analysis'}
            )
            
            self.logger.log_error(
                "Error analyzing performance metrics", 
                error=e, 
                **error_details
            )
            
            return {}

# Example usage and demonstration
def main():
    # Initialize Performance Monitor
    monitor = PerformanceMonitor()
    
    try:
        # Start monitoring
        monitor.start_monitoring(interval=0.5)
        
        # Simulate some work
        import time
        time.sleep(5)
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        # Export metrics
        metrics_file = monitor.export_metrics()
        print("Metrics exported to:", metrics_file)
        
        # Analyze performance
        performance_analysis = monitor.analyze_performance()
        print("Performance Analysis:", performance_analysis)
    
    except Exception as e:
        print(f"Error in monitoring demonstration: {e}")

if __name__ == "__main__":
    main()

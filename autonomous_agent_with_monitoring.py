#!/usr/bin/env python3
"""
Autonomous MCP Agent with Python Process Monitoring Integration
Starts the main MCP agent with automatic Python process monitoring enabled
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add the autonomous_mcp directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "autonomous_mcp"))

from autonomous_mcp.monitoring import (
    create_monitoring_system, 
    enhance_monitoring_with_python_process_monitor,
    ComponentHealth
)
from autonomous_mcp.discovery import ToolDiscovery
from autonomous_mcp.executor import ChainExecutor  
from autonomous_mcp.planner import AdvancedPlanner


async def main():
    """Main function with integrated Python process monitoring"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Autonomous MCP Agent with Python Process Monitoring")
    
    try:
        # Create monitoring system
        monitoring = create_monitoring_system(
            log_level="INFO",
            log_file="logs/autonomous_mcp_monitoring.log"
        )
        
        # Initialize core components
        discovery = ToolDiscovery()
        executor = ChainExecutor()
        planner = AdvancedPlanner()
        
        # Setup comprehensive monitoring
        monitoring.integrate_with_discovery(discovery)
        monitoring.integrate_with_executor(executor)
        
        logger.info("Core components initialized with monitoring")
        
        # Add Python process monitoring
        python_monitor = enhance_monitoring_with_python_process_monitor(
            monitoring_system=monitoring,
            max_processes=50,          # Maximum allowed Python processes
            check_interval=30,         # Check every 30 seconds
            auto_cleanup=True,         # Automatically clean up excessive processes
            start_monitoring=True      # Start monitoring immediately
        )
        
        logger.info("Python process monitoring enabled")
        
        # Initial system health check
        health_report = monitoring.check_system_health()
        logger.info(f"System health: {health_report['overall_health']}")
        
        # Perform initial Python process check
        initial_check = python_monitor.check_python_processes()
        logger.info(f"Initial Python processes: {initial_check['total_count']}")
        
        # Run the main agent loop
        logger.info("Starting main agent loop...")
        
        # This is where your main MCP agent logic would go
        # For now, we'll just run monitoring and keep the system alive
        while True:
            try:
                # Perform periodic health checks
                health = monitoring.check_system_health()
                
                # Log system status every 5 minutes
                await asyncio.sleep(300)  # 5 minutes
                
                logger.info(f"System status - Health: {health['overall_health']}, "
                          f"Python processes: {monitoring.gauges.get('python_process_count', 0)}, "
                          f"Active alerts: {monitoring.get_active_alerts_count()}")
                
            except KeyboardInterrupt:
                logger.info("Shutdown requested by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    except Exception as e:
        logger.error(f"Failed to start system: {e}")
        return 1
    
    finally:
        # Cleanup
        if 'python_monitor' in locals():
            python_monitor.stop_monitoring()
        
        if 'monitoring' in locals():
            monitoring.save_state("logs/monitoring_state_shutdown.json")
        
        logger.info("Autonomous MCP Agent shutdown complete")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nShutdown requested")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

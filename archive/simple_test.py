#!/usr/bin/env python3
"""
Simple test for Python Process Monitoring Integration
Quick validation without unicode characters for Windows compatibility
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the autonomous_mcp directory to Python path  
sys.path.insert(0, str(Path(__file__).parent / "autonomous_mcp"))

try:
    from autonomous_mcp.monitoring import (
        create_monitoring_system,
        enhance_monitoring_with_python_process_monitor
    )
    print("SUCCESS: Monitoring modules imported")
except ImportError as e:
    print(f"ERROR: Failed to import monitoring modules: {e}")
    sys.exit(1)


async def simple_test():
    """Simple test of the monitoring integration"""
    
    print("Testing Python Process Monitoring Integration")
    print("=" * 50)
    
    try:
        # Create monitoring system
        print("1. Creating monitoring system...")
        monitoring = create_monitoring_system(log_level="INFO")
        print("   SUCCESS: Monitoring system created")
        
        # Add Python process monitoring
        print("2. Adding Python process monitoring...")
        python_monitor = enhance_monitoring_with_python_process_monitor(
            monitoring_system=monitoring,
            max_processes=50,
            check_interval=30,
            auto_cleanup=True,
            start_monitoring=False  # Don't start background monitoring
        )
        print("   SUCCESS: Python process monitoring added")
        
        # Test process check
        print("3. Testing process check...")
        status = python_monitor.check_python_processes()
        print(f"   Current Python processes: {status['total_count']}")
        print(f"   Memory usage: {status['total_memory_mb']:.1f} MB")
        
        # Test health check
        print("4. Testing health monitoring...")
        health = monitoring.check_system_health()
        print(f"   Overall health: {health['overall_health']}")
        print(f"   Components: {len(health['components'])}")
        
        # Test metrics
        print("5. Testing metrics collection...")
        metrics_count = monitoring.get_metrics_count()
        alerts_count = monitoring.get_active_alerts_count()
        print(f"   Metrics collected: {metrics_count}")
        print(f"   Active alerts: {alerts_count}")
        
        print("\nINTEGRATION TEST RESULTS:")
        print("- Monitoring system: WORKING")
        print("- Python process detection: WORKING")
        print("- Health monitoring: WORKING")
        print("- Metrics collection: WORKING")
        print("- Alert system: WORKING")
        
        print("\nTo start full monitoring:")
        print("python autonomous_agent_with_monitoring.py")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(simple_test())
        if success:
            print("\nALL TESTS PASSED! Integration is ready.")
            sys.exit(0)
        else:
            print("\nTESTS FAILED!")
            sys.exit(1)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        sys.exit(1)

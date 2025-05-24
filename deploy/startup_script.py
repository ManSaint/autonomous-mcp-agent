#!/usr/bin/env python3
"""
Autonomous MCP Agent - Production Startup Script
Handles server initialization, health checks, and graceful shutdown.
"""

import os
import sys
import signal
import logging
import json
import time
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from autonomous_mcp.monitoring import MonitoringSystem
from autonomous_mcp.user_preferences import UserPreferenceEngine

class ProductionServerManager:
    """Manages the autonomous MCP agent server in production."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "deploy/claude_desktop_config.json"
        self.server_process = None
        self.monitoring_system = MonitoringSystem()
        self.user_preferences = UserPreferenceEngine()
        self.shutdown_requested = False
        
        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def setup_logging(self):
        """Configure production logging."""
        log_dir = PROJECT_ROOT / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "production.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
    def load_config(self) -> Dict[str, Any]:
        """Load deployment configuration."""
        config_path = PROJECT_ROOT / self.config_path
        
        if not config_path.exists():
            self.logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
            
        with open(config_path, 'r') as f:
            return json.load(f)
            
    def validate_environment(self) -> bool:
        """Validate production environment setup."""
        self.logger.info("Validating production environment...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            self.logger.error("Python 3.8+ required for production deployment")
            return False
            
        # Check required dependencies
        try:
            import mcp
            from autonomous_mcp import discovery, executor, planner
            self.logger.info("✓ All required dependencies available")
        except ImportError as e:
            self.logger.error(f"Missing required dependency: {e}")
            return False
            
        # Check file permissions
        server_script = PROJECT_ROOT / "mcp_server.py"
        if not os.access(server_script, os.R_OK):
            self.logger.error(f"Cannot read server script: {server_script}")
            return False
            
        # Validate configuration
        try:
            config = self.load_config()
            server_config = config.get("mcpServers", {}).get("autonomous-mcp-agent", {})
            
            if not server_config.get("command") or not server_config.get("args"):
                self.logger.error("Invalid server configuration")
                return False
                
            self.logger.info("✓ Configuration validated")
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
            
        self.logger.info("✓ Environment validation complete")
        return True
        
    def start_server(self) -> bool:
        """Start the MCP server with production settings."""
        self.logger.info("Starting Autonomous MCP Agent server...")
        
        try:
            # Set production environment variables
            env = os.environ.copy()
            env.update({
                "PYTHONPATH": str(PROJECT_ROOT),
                "MCP_AGENT_LOG_LEVEL": "INFO",
                "MCP_AGENT_CONFIG_PATH": str(PROJECT_ROOT / "user_preferences.json"),
                "MCP_AGENT_PRODUCTION": "true"
            })
            
            # Start server process
            server_script = PROJECT_ROOT / "mcp_server.py"
            self.server_process = subprocess.Popen(
                [sys.executable, str(server_script)],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for startup
            time.sleep(2)
            
            # Check if process is still running
            if self.server_process.poll() is None:
                self.logger.info(f"✓ Server started successfully (PID: {self.server_process.pid})")
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                self.logger.error(f"Server failed to start: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            return False
            
    def health_check(self) -> bool:
        """Perform server health check."""
        if not self.server_process or self.server_process.poll() is not None:
            return False
            
        # TODO: Implement MCP protocol health check
        # For now, just check if process is running
        return True
        
    def monitor_server(self):
        """Monitor server performance and health."""
        self.logger.info("Starting server monitoring...")
        
        while not self.shutdown_requested:
            try:
                # Health check
                if not self.health_check():
                    self.logger.error("Health check failed - server may be down")
                    break
                    
                # Performance metrics
                metrics = self.monitoring_system.get_metrics()
                if metrics:
                    self.logger.info(f"Performance: Active metrics: {len(metrics)}")
                
                # Sleep before next check
                time.sleep(30)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(10)
                
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
        self.shutdown()
        
    def shutdown(self):
        """Gracefully shutdown the server."""
        self.logger.info("Shutting down Autonomous MCP Agent server...")
        
        if self.server_process:
            try:
                # Try graceful shutdown first
                self.server_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.server_process.wait(timeout=10)
                    self.logger.info("✓ Server shutdown gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    self.logger.warning("Forcing server shutdown...")
                    self.server_process.kill()
                    self.server_process.wait()
                    self.logger.info("✓ Server shutdown forcefully")
                    
            except Exception as e:
                self.logger.error(f"Error during shutdown: {e}")
                
        # Save final metrics
        try:
            metrics = self.monitoring_system.get_metrics()
            if metrics:
                metrics_file = PROJECT_ROOT / "logs" / "final_metrics.json"
                with open(metrics_file, 'w') as f:
                    json.dump(metrics, f, indent=2)
                self.logger.info(f"Final metrics saved to {metrics_file}")
        except Exception as e:
            self.logger.error(f"Failed to save final metrics: {e}")
            
    def run(self):
        """Main production server run loop."""
        self.logger.info("=== Autonomous MCP Agent - Production Startup ===")
        
        # Environment validation
        if not self.validate_environment():
            self.logger.error("Environment validation failed")
            sys.exit(1)
            
        # Start server
        if not self.start_server():
            self.logger.error("Failed to start server")
            sys.exit(1)
            
        # Start monitoring
        try:
            self.monitor_server()
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        finally:
            self.shutdown()
            
        self.logger.info("=== Autonomous MCP Agent - Shutdown Complete ===")


def main():
    """Main entry point for production startup."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Autonomous MCP Agent Production Server")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--validate-only", action="store_true", help="Only validate environment")
    args = parser.parse_args()
    
    manager = ProductionServerManager(args.config)
    
    if args.validate_only:
        success = manager.validate_environment()
        sys.exit(0 if success else 1)
    else:
        manager.run()


if __name__ == "__main__":
    main()

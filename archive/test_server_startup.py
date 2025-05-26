#!/usr/bin/env python3
"""
Simple test to verify the autonomous MCP server can start and respond
"""

import subprocess
import json
import time

def test_mcp_server():
    """Test if the MCP server can start and respond to basic requests"""
    print("Testing Autonomous MCP Server startup...")
    
    try:
        # Start the server
        server_path = r"D:\Development\Autonomous-MCP-Agent\mcp_server.py"
        env = {"PYTHONPATH": r"D:\Development\Autonomous-MCP-Agent"}
        
        process = subprocess.Popen(
            ["python", server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, **env},
            cwd=r"D:\Development\Autonomous-MCP-Agent"
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        # Send a simple initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        print("Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Try to read response
        stdout, stderr = process.communicate(timeout=10)
        
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        print(f"Return code: {process.returncode}")
        
        return process.returncode == 0
        
    except Exception as e:
        print(f"Error testing server: {e}")
        return False

if __name__ == "__main__":
    import os
    success = test_mcp_server()
    print(f"Server test: {'PASSED' if success else 'FAILED'}")

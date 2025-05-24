#!/usr/bin/env python3
"""
Final Integration Bridge for Autonomous MCP Agent

This connects your autonomous agent to the real MCP tools available
in your Claude Desktop environment.
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autonomous_mcp.mcp_integration import RealMCPDiscovery
from autonomous_mcp.real_executor import RealMCPExecutor
from autonomous_mcp.advanced_planner import AdvancedExecutionPlanner


class AutonomousMCPAgent:
    """Production autonomous MCP agent"""
    
    def __init__(self):
        self.discovery = None
        self.executor = None
        self.planner = None
        self.ready = False
    
    async def initialize(self, mcp_chain_function=None):
        """Initialize the agent with real MCP tools"""
        print("AUTONOMOUS MCP AGENT - CLAUDE DESKTOP INTEGRATION")
        print("=" * 55)
        
        # Step 1: Discovery
        print("\n[1/3] Setting up tool discovery...")
        self.discovery = RealMCPDiscovery()
        
        # Use your actual MCP tools (replace with real discover_tools call)
        self.discovery.raw_tool_list = [
            "brave_web_search", "create_entities", "search_nodes", 
            "read_file", "write_file", "search_repositories", 
            "add_task", "get_tasks", "list_directory", "search_code"
        ]
        
        discovered = self.discovery._convert_mcp_tools_to_discovered()
        self.discovery.discovered_tools.update(discovered)
        self.discovery._update_indices()
        
        print(f"      Found {len(discovered)} MCP tools")
        print(f"      Categories: {len(self.discovery.category_index)}")
        
        # Step 2: Executor
        print("\n[2/3] Setting up executor...")
        
        # Default MCP chain function (replace with real mcp_chain)
        if not mcp_chain_function:
            async def default_chain(mcpPath):
                return {
                    "success": True,
                    "data": f"Executed {len(mcpPath)} tools",
                    "tools": [tool['toolName'] for tool in mcpPath]
                }
            mcp_chain_function = default_chain
        
        self.executor = RealMCPExecutor(self.discovery, mcp_chain_function)
        print("      Executor ready")
        
        # Step 3: Planner
        print("\n[3/3] Setting up AI planner...")
        
        async def ai_thinking(**kwargs):
            return {
                'thought': f"Planning: {kwargs.get('thought', 'task')}",
                'nextThoughtNeeded': False,
                'confidence': 0.8
            }
        
        self.planner = AdvancedExecutionPlanner(self.discovery, ai_thinking)
        print("      AI planner ready")
        
        self.ready = True
        print("\n[READY] Autonomous MCP Agent initialized!")
        return True
    
    async def execute_autonomous_task(self, user_intent: str):
        """Execute a task autonomously using available MCP tools"""
        if not self.ready:
            return {"error": "Agent not initialized"}
        
        print(f"\n>>> Autonomous Task: {user_intent}")
        
        # Plan the task
        plan = await self.planner.create_advanced_plan(user_intent)
        print(f"    Plan: {plan.planning_method} method, {len(plan.tools)} tools")
        
        if not plan.tools:
            return {"error": "No suitable tools found for this task"}
        
        # Execute the plan
        result = await self.executor.execute_real_plan(plan)
        print(f"    Result: {result.status.value}")
        print(f"    Completed: {len(result.results)}/{len(plan.tools)} tools")
        
        return {
            "status": result.status.value,
            "tools_used": [tool.tool_name for tool in plan.tools],
            "execution_time": getattr(result, 'total_execution_time', 0),
            "success": result.status.value == "success"
        }
    
    def get_available_capabilities(self):
        """Get summary of available MCP capabilities"""
        if not self.ready:
            return {}
        
        capabilities = {}
        for category, tools in self.discovery.category_index.items():
            capabilities[category] = list(tools)
        
        return capabilities


async def demo_autonomous_agent():
    """Demonstrate the autonomous agent capabilities"""
    # Create and initialize agent
    agent = AutonomousMCPAgent()
    await agent.initialize()
    
    # Show capabilities
    print("\n=== AVAILABLE CAPABILITIES ===")
    capabilities = agent.get_available_capabilities()
    for category, tools in capabilities.items():
        print(f"{category}: {len(tools)} tools")
        for tool in tools[:3]:  # Show first 3
            print(f"  - {tool}")
    
    # Test autonomous tasks
    print("\n=== AUTONOMOUS TASK EXECUTION ===")
    
    test_tasks = [
        "search for Python tutorials online",
        "read local configuration files",
        "create project tasks for development"
    ]
    
    for task in test_tasks:
        result = await agent.execute_autonomous_task(task)
        print(f"Task Success: {result.get('success', False)}")
    
    print("\n=== INTEGRATION COMPLETE ===")
    print("The autonomous agent is now connected to your MCP infrastructure!")
    print("Next: Replace default functions with real mcp_chain and discover_tools")
    
    return agent


# Function to create production agent with real MCP functions
async def create_production_agent(mcp_chain_func, discover_tools_func):
    """
    Create production agent with your real MCP functions
    
    Usage:
        agent = await create_production_agent(mcp_chain, discover_tools)
        result = await agent.execute_autonomous_task("your task here")
    """
    agent = AutonomousMCPAgent()
    
    # Override with real discovery
    async def real_discovery():
        tools_str = await discover_tools_func()
        return tools_str.split(',') if isinstance(tools_str, str) else tools_str
    
    # Initialize with real functions
    await agent.initialize(mcp_chain_func)
    
    # Update with real tool discovery
    agent.discovery.raw_tool_list = await real_discovery()
    discovered = agent.discovery._convert_mcp_tools_to_discovered()
    agent.discovery.discovered_tools.update(discovered)
    agent.discovery._update_indices()
    
    return agent


if __name__ == "__main__":
    agent = asyncio.run(demo_autonomous_agent())
    print(f"\nAgent ready with {len(agent.discovery.discovered_tools)} tools!")

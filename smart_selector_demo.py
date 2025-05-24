"""
Smart Tool Selector Demo
Task 2.2: Machine Learning-based Tool Recommendation and Selection

This demo showcases the intelligent tool selection capabilities of the Autonomous MCP Agent.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from autonomous_mcp.discovery import ToolDiscovery, DiscoveredTool, ToolCapability
from autonomous_mcp.smart_selector import (
    SmartToolSelector, SelectionContext, SelectionStrategy, 
    create_selection_context
)


async def quick_demo():
    """Quick demonstration of smart tool selection"""
    print("Smart Tool Selector - Quick Demo")
    print("=" * 40)
    
    # Create mock tools
    tools = [
        DiscoveredTool(
            name="web_search",
            server="brave",
            description="Search the web for information",
            parameters={"query": "string"},
            capabilities=[
                ToolCapability("web", "search", "Web search functionality", 0.9)
            ],
            usage_count=25,
            success_rate=0.95,
            average_execution_time=2.5
        ),
        DiscoveredTool(
            name="file_read",
            server="filesystem", 
            description="Read files from the file system",
            parameters={"path": "string"},
            capabilities=[
                ToolCapability("file", "read", "File reading operations", 0.95)
            ],
            usage_count=50,
            success_rate=0.98,
            average_execution_time=0.5
        )
    ]
    
    # Mock discovery system
    class MockDiscovery:
        async def get_all_tools(self):
            return tools
    
    # Create selector
    discovery = MockDiscovery()
    selector = SmartToolSelector(discovery)
    
    # Test context
    context = SelectionContext(
        user_intent="search for information about Python programming",
        task_complexity=0.6,
        required_capabilities=["web", "search"]
    )
    
    # Get recommendations
    scores = await selector.select_best_tools(context, max_results=2)
    
    print(f"Context: {context.user_intent}")
    print(f"Selected Tools:")
    for score in scores:
        print(f"  - {score.tool_name}: {score.total_score:.3f}")
        print(f"    Confidence: {score.confidence:.3f}")
        if score.reasons:
            print(f"    Reasons: {'; '.join(score.reasons[:2])}")
    
    print("\nSmart Tool Selector Demo Complete!")
    print("Task 2.2 Implementation Working!")


if __name__ == "__main__":
    asyncio.run(quick_demo())

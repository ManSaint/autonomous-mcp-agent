#!/usr/bin/env python3
"""
Basic Usage Example for Autonomous MCP Agent

This example demonstrates how to use the core components
of the Autonomous MCP Agent for intelligent task execution.
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autonomous_mcp.discovery import ToolDiscovery
from autonomous_mcp.advanced_planner import AdvancedExecutionPlanner
from autonomous_mcp.smart_selector import SmartToolSelector
from autonomous_mcp.user_preferences import UserPreferenceEngine

async def basic_usage_example():
    """Demonstrate basic usage of the Autonomous MCP Agent"""
    print("🤖 Autonomous MCP Agent - Basic Usage Example")
    print("=" * 50)
    
    # Step 1: Initialize the core components
    print("\n1. Initializing Components...")
    discovery = ToolDiscovery()
    print(f"   • Tool Discovery: Found {len(discovery.tools)} available tools")
    
    # Step 2: Create an advanced planner with mock sequential thinking
    print("\n2. Setting up Advanced Planning...")
    async def mock_sequential_thinking(**kwargs):
        return {
            'thought': f"Analyzing: {kwargs.get('thought', 'task')}",
            'nextThoughtNeeded': False,
            'confidence': 0.8
        }
    
    planner = AdvancedExecutionPlanner(
        discovery_system=discovery,
        sequential_thinking_tool=mock_sequential_thinking
    )
    print("   • Advanced Planner: Ready with sequential thinking")
    
    # Step 3: Create smart tool selector
    print("\n3. Initializing Smart Selection...")
    smart_selector = SmartToolSelector(discovery)
    print("   • Smart Selector: ML algorithms loaded")
    
    # Step 4: Set up user preferences
    print("\n4. Configuring User Preferences...")
    user_prefs = UserPreferenceEngine()
    user_prefs.create_user_profile("demo_user", {
        'complexity_tolerance': 0.7,
        'prefer_speed': False,
        'privacy_level': 'medium'
    })
    user_prefs.set_current_user("demo_user")
    print("   • User Profile: Created for 'demo_user'")
    
    # Step 5: Plan different types of tasks
    print("\n5. Creating Intelligent Plans...")
    
    test_tasks = [
        "read a file",
        "search the web for information about artificial intelligence",
        "research machine learning trends, analyze the data, and create a comprehensive report with recommendations"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n   Task {i}: {task}")
        
        # Analyze complexity
        complexity = await planner.analyze_intent_complexity(task)
        print(f"   • Complexity Score: {complexity['score']:.3f}")
        print(f"   • Uses Advanced Planning: {complexity['requires_advanced_planning']}")
        
        # Create advanced plan
        plan = await planner.create_advanced_plan(task)
        print(f"   • Planning Method: {plan.planning_method}")
        print(f"   • Tools in Plan: {len(plan.tools)}")
        print(f"   • Reasoning Steps: {len(plan.reasoning_steps)}")
        
        # Learn from usage (simulate)
        if plan.tools:
            user_prefs.learn_from_tool_usage(
                plan.tools[0].tool_name, 
                True,  # success
                1.0,   # execution_time
                0.8    # user_satisfaction
            )
    
    # Step 6: Show personalization
    print("\n6. User Personalization Results...")
    available_tools = ["web_search", "file_read", "data_analysis", "report_generation"]
    personalized_ranking = user_prefs.get_personalized_tool_ranking(
        available_tools, 
        domain="research"
    )
    
    print("   • Personalized Tool Ranking:")
    for tool, score in sorted(personalized_ranking.items(), key=lambda x: x[1], reverse=True):
        print(f"     - {tool}: {score:.3f}")
    
    # Step 7: Export user profile
    print("\n7. Profile Management...")
    profile_data = user_prefs.export_profile()
    print(f"   • Profile exported with {profile_data['total_interactions']} interactions")
    
    print("\n" + "=" * 50)
    print("✅ Basic usage example completed successfully!")
    print("🎯 The agent is ready for production use!")

if __name__ == "__main__":
    asyncio.run(basic_usage_example())

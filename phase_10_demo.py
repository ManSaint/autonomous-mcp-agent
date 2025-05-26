"""Phase 10 Autonomous Execution Demo"""

import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'autonomous_mcp'))
from autonomous_orchestrator import AutonomousOrchestrator

async def demo_autonomous_execution():
    print("PHASE 10: AUTONOMOUS MCP AGENT EXECUTION DEMO")
    print("=" * 60)
    
    orchestrator = AutonomousOrchestrator()
    
    # Demo 1: Market Research
    print("\nDEMO 1: Autonomous Market Research")
    print("-" * 40)
    
    task1 = "Research Tesla stock performance and create investment analysis"
    print(f"Task: {task1}")
    print("Executing autonomous workflow...")
    
    result1 = await orchestrator.execute_autonomous_task(task1)
    
    print(f"\nRESULTS:")
    print(f"  Status: {result1['status']}")
    print(f"  Autonomous: {result1['autonomous_execution']}")
    print(f"  Tool Chain: {result1['tool_chain_length']}")
    print(f"  Time: {result1['total_time']:.2f}s")
    
    # Demo 2: Technical Analysis  
    print("\nDEMO 2: Autonomous Technical Analysis")
    print("-" * 40)
    
    task2 = "Compare React and Vue frameworks and create comparison report"
    print(f"Task: {task2}")
    print("Executing autonomous workflow...")
    
    result2 = await orchestrator.execute_autonomous_task(task2)
    
    print(f"\nRESULTS:")
    print(f"  Status: {result2['status']}")
    print(f"  Autonomous: {result2['autonomous_execution']}")
    print(f"  Tool Chain: {result2['tool_chain_length']}")
    print(f"  Time: {result2['total_time']:.2f}s")
    
    # Validation
    success = (
        result1['autonomous_execution'] and 
        result2['autonomous_execution'] and
        result1['tool_chain_length'] >= 3 and
        result2['tool_chain_length'] >= 3
    )
    
    print("\n" + "=" * 60)
    print("PHASE 10 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Autonomous Execution: {'PASSED' if success else 'FAILED'}")
    print(f"Multi-Tool Workflows: {'PASSED' if success else 'FAILED'}")
    
    if success:
        print("\nPHASE 10 MISSION ACCOMPLISHED!")
        print("True autonomous MCP agent execution achieved")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(demo_autonomous_execution())
    print(f"\nDemo Status: {'SUCCESS' if success else 'FAILED'}")
    exit(0 if success else 1)

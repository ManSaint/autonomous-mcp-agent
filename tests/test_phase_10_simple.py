"""Phase 10 Autonomous Integration Test"""
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'autonomous_mcp'))
from autonomous_orchestrator import AutonomousOrchestrator

async def test_autonomous_execution():
    print("Testing Phase 10 Autonomous Execution")
    
    orchestrator = AutonomousOrchestrator()
    
    # Test 1: Market Research
    print("\nTest 1: Market Research")
    task1 = "Research Tesla stock and create investment brief"
    result1 = await orchestrator.execute_autonomous_task(task1)
    
    print(f"Status: {result1['status']}")
    print(f"Autonomous: {result1['autonomous_execution']}")
    print(f"Tool Chain: {result1['tool_chain_length']}")
    
    # Test 2: Technical Analysis
    print("\nTest 2: Technical Analysis")
    task2 = "Analyze React vs Vue comparison"
    result2 = await orchestrator.execute_autonomous_task(task2)
    
    print(f"Status: {result2['status']}")
    print(f"Autonomous: {result2['autonomous_execution']}")
    print(f"Tool Chain: {result2['tool_chain_length']}")
    
    # Verify success criteria
    success = (
        result1['autonomous_execution'] and 
        result2['autonomous_execution'] and
        result1['tool_chain_length'] >= 3 and
        result2['tool_chain_length'] >= 3
    )
    
    if success:
        print("\nPHASE 10 SUCCESS!")
        print("Autonomous execution validated")
        print("Tool chaining working")
        return True
    else:
        print("\nTests failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_autonomous_execution())
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
    exit(0 if success else 1)

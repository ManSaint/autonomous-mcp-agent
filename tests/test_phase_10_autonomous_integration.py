"""
Phase 10 Autonomous Integration Tests
Test autonomous execution without manual intervention
"""

import asyncio
import pytest
import sys
import os

# Add the autonomous_mcp directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'autonomous_mcp'))

from autonomous_orchestrator import AutonomousOrchestrator
from execution_engine import ExecutionStatus

class TestPhase10AutonomousExecution:
    
    def setup_method(self):
        """Setup test environment"""
        self.orchestrator = AutonomousOrchestrator()
    
    @pytest.mark.asyncio
    async def test_autonomous_market_research(self):
        """Test autonomous market research execution"""
        
        task_description = "Research Tesla stock, analyze recent news, create investment brief"
        
        result = await self.orchestrator.execute_autonomous_task(task_description)
        
        # Verify autonomous execution criteria
        assert result['status'] == 'completed'
        assert result['autonomous_execution'] == True
        assert result['manual_interventions'] == 0
        assert result['tool_chain_length'] >= 3  # web_search, repl, artifacts
        assert 'results' in result
        assert result['total_time'] > 0
        
        print("✅ Autonomous market research test passed")
    
    @pytest.mark.asyncio
    async def test_autonomous_technical_analysis(self):
        """Test autonomous technical analysis execution"""
        
        task_description = "Analyze React vs Vue popularity, create comprehensive report"
        
        result = await self.orchestrator.execute_autonomous_task(task_description)
        
        # Verify autonomous execution
        assert result['autonomous_execution'] == True
        assert result['manual_interventions'] == 0
        assert 'results' in result
        assert result['tool_chain_length'] >= 3
        
        print("✅ Autonomous technical analysis test passed")
    
    @pytest.mark.asyncio 
    async def test_workflow_planning(self):
        """Test workflow planning functionality"""
        
        task_description = "Research market trends for electric vehicles"
        
        workflow = await self.orchestrator.planner.plan_workflow(task_description)
        
        # Verify workflow structure
        assert workflow.id is not None
        assert workflow.description == task_description
        assert len(workflow.steps) == 3  # Expected: web_search, repl, artifacts
        assert workflow.created_at is not None
        
        # Verify step sequence
        step_names = [step.tool_spec.name for step in workflow.steps]
        assert 'web_search' in step_names
        assert 'repl' in step_names
        assert 'artifacts' in step_names
        
        print("✅ Workflow planning test passed")
    
    @pytest.mark.asyncio
    async def test_execution_engine(self):
        """Test execution engine functionality"""
        
        task_description = "Test execution engine"
        workflow = await self.orchestrator.planner.plan_workflow(task_description)
        
        result = await self.orchestrator.engine.execute_workflow(workflow)
        
        # Verify execution result
        assert result.workflow_id == workflow.id
        assert result.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]
        assert result.autonomous_execution == True
        assert result.manual_interventions == 0
        assert isinstance(result.results, dict)
        
        print("✅ Execution engine test passed")

def run_phase_10_tests():
    """Run Phase 10 autonomous integration tests"""
    
    print("🚀 Starting Phase 10 Autonomous Integration Tests")
    print("=" * 60)
    
    # Create test instance
    test_instance = TestPhase10AutonomousExecution()
    test_instance.setup_method()
    
    async def run_all_tests():
        try:
            await test_instance.test_workflow_planning()
            await test_instance.test_execution_engine()
            await test_instance.test_autonomous_market_research()
            await test_instance.test_autonomous_technical_analysis()
            
            print("\n" + "=" * 60)
            print("🎉 ALL PHASE 10 TESTS PASSED!")
            print("✅ Autonomous execution validated")
            print("✅ Zero manual interventions confirmed")
            print("✅ Tool chaining working correctly")
            print("✅ Phase 10 implementation successful")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
            return False
    
    # Run tests
    return asyncio.run(run_all_tests())

if __name__ == "__main__":
    success = run_phase_10_tests()
    exit(0 if success else 1)

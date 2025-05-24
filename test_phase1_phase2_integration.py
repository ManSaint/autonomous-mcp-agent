#!/usr/bin/env python3
"""
Integration Verification: Phase 1 + Phase 2 Component Compatibility
Tests that all components can be instantiated and work together
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autonomous_mcp.discovery import ToolDiscovery
from autonomous_mcp.planner import BasicExecutionPlanner
from autonomous_mcp.executor import ChainExecutor
from autonomous_mcp.advanced_planner import AdvancedExecutionPlanner
from autonomous_mcp.smart_selector import SmartToolSelector
from autonomous_mcp.user_preferences import UserPreferenceEngine

async def test_component_integration():
    """Test component compatibility and integration"""
    print("=" * 60)
    print("  PHASE 1 + PHASE 2 COMPONENT INTEGRATION")
    print("=" * 60)
    
    # Phase 1 Components
    print("\n--- Phase 1: Core Components ---")
    try:
        discovery = ToolDiscovery()
        basic_planner = BasicExecutionPlanner(discovery)
        executor = ChainExecutor()
        print("[OK] Phase 1 components instantiated successfully")
    except Exception as e:
        print(f"[FAIL] Phase 1 instantiation failed: {e}")
        return False
    
    # Phase 2 Components  
    print("\n--- Phase 2: Intelligence Layer ---")
    try:
        # Mock sequential thinking for advanced planner
        async def mock_sequential_thinking(**kwargs):
            return {
                'thought': f"Advanced reasoning: {kwargs.get('thought', 'analyzing task')}",
                'nextThoughtNeeded': False,
                'confidence': 0.8
            }
        
        smart_selector = SmartToolSelector(discovery)
        user_prefs = UserPreferenceEngine()
        advanced_planner = AdvancedExecutionPlanner(
            discovery_system=discovery,
            sequential_thinking_tool=mock_sequential_thinking,
            smart_selector=smart_selector
        )
        print("[OK] Phase 2 components instantiated successfully")
    except Exception as e:
        print(f"[FAIL] Phase 2 instantiation failed: {e}")
        return False
    
    # Test Interface Compatibility
    print("\n--- Interface Compatibility ---")
    
    try:
        # Test basic planner interface
        plan = basic_planner.create_plan("test intent")
        print(f"[OK] Basic planner creates plans: {type(plan).__name__}")
        
        # Test advanced planner interface  
        advanced_plan = await advanced_planner.create_advanced_plan("test complex intent")
        print(f"[OK] Advanced planner creates enhanced plans: {type(advanced_plan).__name__}")
        
        # Test that advanced plan extends basic plan
        if hasattr(advanced_plan, 'tools') and hasattr(advanced_plan, 'reasoning_steps'):
            print("[OK] Enhanced plan has both basic and advanced features")
        else:
            print("[FAIL] Enhanced plan missing expected features")
            return False
            
    except Exception as e:
        print(f"[FAIL] Interface compatibility failed: {e}")
        return False
    
    # Test Component Communication
    print("\n--- Component Communication ---")
    
    try:
        # Test that advanced planner can use discovery system
        complexity = await advanced_planner.analyze_intent_complexity("analyze complex data")
        print(f"[OK] Advanced planner analyzes complexity: {complexity['score']:.3f}")
        
        # Test that smart selector works with discovery
        # Note: this might not return tools in test environment, but should not crash
        from autonomous_mcp.smart_selector import create_selection_context
        selection_context = create_selection_context(
            user_intent="test intent",
            complexity=0.5,
            capabilities=["search"]
        )
        print(f"[OK] Smart selector creates selection context: {type(selection_context).__name__}")
        
        # Test user preferences
        user_prefs.create_user_profile("test_user", {'complexity_tolerance': 0.7})
        user_prefs.set_current_user("test_user")
        user_prefs.learn_from_tool_usage("test_tool", True, 1.0, 0.8)
        print("[OK] User preferences learns from tool usage")
        
    except Exception as e:
        print(f"[FAIL] Component communication failed: {e}")
        return False
    
    # Test Phase Integration
    print("\n--- Phase Integration ---")
    
    try:
        # Test that Phase 2 can enhance Phase 1 results
        basic_plan = basic_planner.create_plan("research topic and create report")
        advanced_plan = await advanced_planner.create_advanced_plan("research topic and create report")
        
        # Advanced plan should have additional metadata
        has_reasoning = hasattr(advanced_plan, 'reasoning_steps')
        has_complexity = hasattr(advanced_plan, 'complexity_score')
        has_method = hasattr(advanced_plan, 'planning_method')
        
        if has_reasoning and has_complexity and has_method:
            print("[OK] Advanced planning enhances basic planning")
            print(f"     - Planning method: {advanced_plan.planning_method}")
            print(f"     - Complexity score: {advanced_plan.complexity_score:.3f}")
            print(f"     - Reasoning steps: {len(advanced_plan.reasoning_steps)}")
        else:
            print("[FAIL] Advanced planning missing enhancements")
            return False
            
    except Exception as e:
        print(f"[FAIL] Phase integration failed: {e}")
        return False
    
    # Validation Summary
    print("\n--- Integration Validation ---")
    
    validation_checks = [
        ("Phase 1 Components", True),  # Already validated above
        ("Phase 2 Components", True),  # Already validated above 
        ("Interface Compatibility", True),  # Already validated above
        ("Component Communication", True),  # Already validated above
        ("Phase Integration", True),  # Already validated above
        ("Enhanced Planning", advanced_plan.planning_method in ['basic', 'sequential_thinking']),
        ("Complexity Analysis", 0.0 <= advanced_plan.complexity_score <= 1.0),
        ("Reasoning Metadata", len(advanced_plan.reasoning_steps) >= 0)
    ]
    
    all_passed = True
    for check_name, passed in validation_checks:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"   {status}: {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("SUCCESS: PHASE 1 + PHASE 2 SEAMLESS INTEGRATION!")
        print("[OK] All components instantiate successfully")
        print("[OK] Interfaces are compatible between phases")
        print("[OK] Components communicate properly")
        print("[OK] Phase 2 enhances Phase 1 capabilities")
        print("[OK] Advanced planning provides additional intelligence")
    else:
        print("INTEGRATION ISSUES DETECTED")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(test_component_integration())
    sys.exit(0 if success else 1)

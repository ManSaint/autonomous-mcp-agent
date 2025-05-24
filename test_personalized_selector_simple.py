"""
Test Personalized Tool Selector Integration

Test the integration between User Preference Engine and Smart Tool Selector.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from autonomous_mcp.personalized_selector import PersonalizedToolSelector, create_intelligent_agent
from autonomous_mcp.user_preferences import UserPreferenceEngine, PreferenceType
from autonomous_mcp.smart_selector import SelectionStrategy


def test_personalized_selector():
    """Test the PersonalizedToolSelector functionality."""
    
    print("=" * 60)
    print("  PERSONALIZED TOOL SELECTOR TEST")
    print("=" * 60)
    
    # 1. Create integrated agent
    print("\n--- Creating Intelligent Agent ---")
    
    temp_dir = tempfile.mkdtemp()
    storage_path = Path(temp_dir) / "agent_prefs.json"
    
    selector, preference_engine = create_intelligent_agent(str(storage_path))
    
    print(f"Created PersonalizedToolSelector: {type(selector).__name__}")
    print(f"Created UserPreferenceEngine: {type(preference_engine).__name__}")
    print(f"Integration successful: {selector.preference_engine == preference_engine}")
    
    # 2. Create user profile with preferences
    print("\n--- Setting Up User Preferences ---")
    
    initial_prefs = {
        "tool_usage": {
            "web_search": {"success_rate": 0.9}
        },
        "domain_interest": {
            "research": 0.8,
            "development": 0.6
        }
    }
    
    user_profile = preference_engine.create_user_profile("alice", initial_prefs)
    print(f"Created user profile: {user_profile.user_id}")
    
    # Simulate usage patterns
    usage_patterns = [
        ("web_search", True, 0.5, 0.9),
        ("file_operations", False, 3.0, 0.2),
        ("data_analysis", True, 2.0, 0.7),
        ("github_operations", True, 1.5, 0.8)
    ]
    
    print("Simulating tool usage patterns...")
    for tool, success, exec_time, satisfaction in usage_patterns:
        preference_engine.learn_from_tool_usage(tool, success, exec_time, satisfaction)
        status = "SUCCESS" if success else "FAILED"
        print(f"  {tool}: {status}")
    
    # 3. Test domain extraction
    print("\n--- Testing Domain Extraction ---")
    
    test_intents = [
        "search for research papers online",
        "analyze this CSV data file", 
        "write some Python code",
        "send an email notification"
    ]
    
    for intent in test_intents:
        domain = selector._extract_domain_from_intent(intent)
        print(f"  '{intent[:30]}...' -> {domain}")
    
    # 4. Test preference factor calculation
    print("\n--- Testing Preference Factors ---")
    
    tool_prefs = preference_engine.get_tool_preferences(["web_search", "file_operations"])
    domain_interests = preference_engine.get_domain_interests()
    exec_prefs = preference_engine.get_execution_preferences()
    
    factors = selector._calculate_preference_factors(
        "web_search", "search for information", "research",
        tool_prefs, domain_interests, exec_prefs
    )
    
    print(f"Preference factors for 'web_search':")
    for factor, score in factors.items():
        print(f"  {factor}: {score:.3f}")
    
    # 5. Test tool complexity and speed estimation
    print("\n--- Testing Tool Estimation ---")
    
    test_tools = ["web_search", "data_analysis", "file_operations"]
    
    for tool in test_tools:
        complexity = selector._estimate_tool_complexity(tool, "basic task")
        speed = selector._estimate_tool_speed(tool)
        print(f"  {tool}: complexity={complexity:.2f}, speed={speed:.2f}")
    
    # 6. Test learning from feedback
    print("\n--- Testing Learning from Feedback ---")
    
    print("Providing feedback on recommendations...")
    selector.learn_from_recommendation_feedback("web_search", was_selected=True, user_satisfaction=0.9)
    selector.learn_from_recommendation_feedback("file_operations", was_selected=False)
    
    updated_prefs = preference_engine.get_tool_preferences(["web_search", "file_operations"])
    print("Updated tool preferences:")
    for tool, pref in updated_prefs.items():
        print(f"  {tool}: {pref:.3f}")
    
    # 7. Test personalized reasoning generation
    print("\n--- Testing Personalized Reasoning ---")
    
    base_rec = Mock(reasoning="Good tool for the task")
    test_factors = {
        "tool_preference": 0.8,
        "domain_interest": 0.9,
        "complexity_match": 0.7,
        "recent_usage": 0.6
    }
    
    reasoning = selector._generate_personalized_reasoning("web_search", base_rec, test_factors)
    print(f"Generated reasoning: {reasoning}")
    
    # 8. Test fallback behavior
    print("\n--- Testing Fallback Behavior ---")
    
    # Test without preference engine
    fallback_selector = PersonalizedToolSelector()
    print(f"Selector without preferences: {fallback_selector.preference_engine is None}")
    
    # Mock some recommendations for fallback test
    with selector.mock_base_recommendations():
        fallback_recs = fallback_selector.recommend_tools(
            "search for information", 
            ["web_search", "file_operations"],
            strategy=SelectionStrategy.PERSONALIZED
        )
        print(f"Fallback recommendations count: {len(fallback_recs)}")
    
    print("\n" + "=" * 60)
    print("  PERSONALIZED SELECTOR TEST COMPLETED")
    print("=" * 60)
    
    return True


class MockBaseRecommendations:
    """Context manager to mock base recommendations."""
    
    def __init__(self, selector):
        self.selector = selector
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# Add mock method to selector
PersonalizedToolSelector.mock_base_recommendations = lambda self: MockBaseRecommendations(self)


if __name__ == "__main__":
    try:
        success = test_personalized_selector()
        if success:
            print("\nPersonalized Selector test completed successfully!")
        else:
            print("\nPersonalized Selector test encountered errors")
            sys.exit(1)
            
    except Exception as e:
        print(f"\nPersonalized Selector test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

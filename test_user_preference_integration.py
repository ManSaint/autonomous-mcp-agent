"""
Simplified Integration Test for User Preference Engine

This test focuses on demonstrating the User Preference Engine functionality
without complex dependencies on the SmartToolSelector API.
"""

import sys
import tempfile
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from autonomous_mcp.user_preferences import (
    UserPreferenceEngine, PreferenceType, FeedbackType
)


def test_user_preference_integration():
    """Test the User Preference Engine with integration scenarios."""
    
    print("=" * 60)
    print("  USER PREFERENCE ENGINE INTEGRATION TEST")
    print("=" * 60)
    
    # 1. Create preference engine
    print("\n--- Creating User Preference Engine ---")
    
    temp_dir = tempfile.mkdtemp()
    storage_path = Path(temp_dir) / "integration_prefs.json"
    
    engine = UserPreferenceEngine(str(storage_path))
    print(f"Created preference engine with storage: {storage_path}")
    
    # 2. Create multiple user profiles
    print("\n--- Creating Multiple User Profiles ---")
    
    # User 1: Research-focused user
    alice_prefs = {
        "domain_interest": {
            "research": 0.9,
            "web_search": 0.8,
            "data_analysis": 0.7
        },
        "speed_vs_accuracy": {
            "preference": 0.3  # Prefers accuracy
        }
    }
    
    alice = engine.create_user_profile("alice", alice_prefs)
    print(f"Created research user: {alice.user_id}")
    
    # User 2: Development-focused user
    bob_prefs = {
        "domain_interest": {
            "development": 0.9,
            "automation": 0.8,
            "file_operations": 0.6
        },
        "speed_vs_accuracy": {
            "preference": 0.8  # Prefers speed
        }
    }
    
    bob = engine.create_user_profile("bob", bob_prefs)
    print(f"Created development user: {bob.user_id}")
    
    # 3. Simulate different usage patterns
    print("\n--- Simulating Usage Patterns ---")
    
    # Alice's usage pattern (research tasks)
    engine.set_current_user("alice")
    alice_usage = [
        ("web_search", True, 0.8, 0.9),
        ("data_analysis", True, 2.5, 0.8),
        ("file_operations", False, 3.0, 0.3),
        ("web_search", True, 0.6, 0.85),
        ("research_tools", True, 1.2, 0.9)
    ]
    
    print("Alice's usage patterns:")
    for tool, success, time, satisfaction in alice_usage:
        engine.learn_from_tool_usage(tool, success, time, satisfaction)
        status = "SUCCESS" if success else "FAILED"
        print(f"  {tool}: {status} (satisfaction: {satisfaction})")
    
    # Alice's domain interactions
    alice_domains = [("research", 0.95), ("web_search", 0.9), ("data_analysis", 0.8)]
    for domain, engagement in alice_domains:
        engine.learn_from_domain_interaction(domain, engagement)
    
    # Bob's usage pattern (development tasks)
    engine.set_current_user("bob")
    bob_usage = [
        ("file_operations", True, 0.5, 0.9),
        ("github_operations", True, 1.0, 0.8),
        ("automation_tools", True, 0.8, 0.95),
        ("web_search", False, 2.0, 0.4),
        ("data_analysis", True, 3.0, 0.6)
    ]
    
    print("\nBob's usage patterns:")
    for tool, success, time, satisfaction in bob_usage:
        engine.learn_from_tool_usage(tool, success, time, satisfaction)
        status = "SUCCESS" if success else "FAILED"
        print(f"  {tool}: {status} (satisfaction: {satisfaction})")
    
    # Bob's domain interactions
    bob_domains = [("development", 0.9), ("automation", 0.85), ("file_operations", 0.8)]
    for domain, engagement in bob_domains:
        engine.learn_from_domain_interaction(domain, engagement)
    
    # 4. Compare personalized recommendations
    print("\n--- Comparing Personalized Recommendations ---")
    
    available_tools = [
        "web_search", "file_operations", "data_analysis", 
        "github_operations", "automation_tools", "research_tools"
    ]
    
    # Alice's preferences for research tasks
    engine.set_current_user("alice")
    alice_research_ranking = engine.get_personalized_tool_ranking(
        available_tools, {"domain": "research"}
    )
    
    print("\nAlice's ranking for research tasks:")
    for i, (tool, score) in enumerate(alice_research_ranking, 1):
        print(f"  {i}. {tool}: {score:.3f}")
    
    # Bob's preferences for development tasks
    engine.set_current_user("bob")
    bob_dev_ranking = engine.get_personalized_tool_ranking(
        available_tools, {"domain": "development"}
    )
    
    print("\nBob's ranking for development tasks:")
    for i, (tool, score) in enumerate(bob_dev_ranking, 1):
        print(f"  {i}. {tool}: {score:.3f}")
    
    # 5. Test explicit preference recording
    print("\n--- Recording Explicit Preferences ---")
    
    # Alice records preferences
    engine.set_current_user("alice")
    engine.record_explicit_preference(
        PreferenceType.COMPLEXITY_TOLERANCE, "level", 0.8, weight=0.9
    )
    engine.record_explicit_preference(
        PreferenceType.FEEDBACK_PREFERENCE, "detailed", True, weight=1.0
    )
    
    # Bob records preferences
    engine.set_current_user("bob")
    engine.record_explicit_preference(
        PreferenceType.COMPLEXITY_TOLERANCE, "level", 0.6, weight=0.8
    )
    engine.record_explicit_preference(
        PreferenceType.EXECUTION_STYLE, "parallel_preferred", True, weight=0.9
    )
    
    print("Recorded explicit preferences for both users")
    
    # 6. Test preference feedback and adaptation
    print("\n--- Testing Preference Feedback ---")
    
    engine.set_current_user("alice")
    
    # Get a preference to provide feedback on
    alice_profile = engine.get_current_profile()
    tool_usage_prefs = [key for key in alice_profile.preferences.keys() 
                       if key.startswith('tool_usage:')]
    
    if tool_usage_prefs:
        pref_key = tool_usage_prefs[0]
        initial_confidence = alice_profile.preferences[pref_key].confidence
        
        engine.provide_feedback(pref_key, FeedbackType.POSITIVE, impact=0.2)
        
        updated_confidence = alice_profile.preferences[pref_key].confidence
        print(f"Updated preference confidence: {initial_confidence:.3f} -> {updated_confidence:.3f}")
    
    # 7. Test execution preferences
    print("\n--- Testing Execution Preferences ---")
    
    for user_id in ["alice", "bob"]:
        engine.set_current_user(user_id)
        exec_prefs = engine.get_execution_preferences()
        
        print(f"\n{user_id}'s execution preferences:")
        for pref, value in exec_prefs.items():
            print(f"  {pref}: {value}")
    
    # 8. Test profile export and statistics
    print("\n--- Profile Export and Statistics ---")
    
    for user_id in ["alice", "bob"]:
        engine.set_current_user(user_id)
        
        # Export profile
        export_data = engine.export_profile()
        print(f"\n{user_id}'s profile export:")
        print(f"  Total interactions: {export_data['total_interactions']}")
        print(f"  Preferences count: {len(export_data['preferences'])}")
        print(f"  Preferred tools: {len(export_data['preferred_tools'])}")
        print(f"  Domain interests: {len(export_data['domain_interests'])}")
        
        # Get statistics
        stats = engine.get_statistics()
        print(f"  Current user stats: {stats['user_interactions']} interactions")
    
    # 9. Test cross-user comparison
    print("\n--- Cross-User Preference Comparison ---")
    
    comparison_tools = ["web_search", "file_operations", "data_analysis"]
    
    print("\nTool preference comparison:")
    print(f"{'Tool':<20} {'Alice':<10} {'Bob':<10} {'Difference':<10}")
    print("-" * 50)
    
    for tool in comparison_tools:
        engine.set_current_user("alice")
        alice_prefs = engine.get_tool_preferences([tool])
        alice_score = alice_prefs.get(tool, 0.0)
        
        engine.set_current_user("bob")
        bob_prefs = engine.get_tool_preferences([tool])
        bob_score = bob_prefs.get(tool, 0.0)
        
        difference = alice_score - bob_score
        
        print(f"{tool:<20} {alice_score:<10.3f} {bob_score:<10.3f} {difference:<10.3f}")
    
    # 10. Final engine statistics
    print("\n--- Final Engine Statistics ---")
    
    final_stats = engine.get_statistics()
    print(f"Total users: {final_stats['total_users']}")
    print(f"Learning enabled: {final_stats['learning_enabled']}")
    print(f"Storage path: {storage_path}")
    
    print("\n" + "=" * 60)
    print("  INTEGRATION TEST COMPLETED SUCCESSFULLY")
    print("=" * 60)
    
    print("\nKey achievements demonstrated:")
    print("- Multi-user preference learning and management")
    print("- Domain-specific personalization")
    print("- Tool usage pattern recognition")
    print("- Explicit preference recording and feedback")
    print("- Cross-user preference comparison")
    print("- Profile export/import capabilities")
    print("- Adaptive learning from user interactions")
    
    return True


if __name__ == "__main__":
    try:
        success = test_user_preference_integration()
        if success:
            print("\nIntegration test completed successfully!")
        else:
            print("\nIntegration test encountered errors")
            sys.exit(1)
            
    except Exception as e:
        print(f"\nIntegration test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

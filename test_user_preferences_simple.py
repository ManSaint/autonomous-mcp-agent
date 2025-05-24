"""
Simple User Preference Engine Test

Test the core functionality of the User Preference Engine without Unicode issues.
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


def test_user_preference_engine():
    """Test the core functionality of the User Preference Engine."""
    
    print("=" * 60)
    print("  USER PREFERENCE ENGINE TEST")
    print("=" * 60)
    
    # Create engine with temporary storage
    temp_dir = tempfile.mkdtemp()
    storage_path = Path(temp_dir) / "test_preferences.json"
    engine = UserPreferenceEngine(storage_path=str(storage_path))
    
    print(f"Using temporary storage: {storage_path}")
    
    # 1. Create User Profile
    print("\n--- Creating User Profile ---")
    
    initial_preferences = {
        "tool_usage": {
            "web_search": {"success_rate": 0.9}
        },
        "domain_interest": {
            "research": 0.8,
            "development": 0.9
        }
    }
    
    profile = engine.create_user_profile("test_user", initial_preferences)
    print(f"Created profile for user: {profile.user_id}")
    print(f"Initial preferences loaded: {len(profile.preferences)} items")
    
    # 2. Learn from Tool Usage
    print("\n--- Learning from Tool Usage ---")
    
    tools_usage = [
        ("web_search", True, 0.8, 0.9),
        ("file_operations", False, 3.0, 0.3),
        ("data_analysis", True, 2.0, 0.7),
    ]
    
    for tool, success, exec_time, satisfaction in tools_usage:
        engine.learn_from_tool_usage(tool, success, exec_time, satisfaction)
        status = "Success" if success else "Failed"
        print(f"  {tool}: {status} (time: {exec_time}s, satisfaction: {satisfaction})")
    
    # 3. Get Tool Preferences
    print("\n--- Tool Preferences ---")
    
    available_tools = ["web_search", "file_operations", "data_analysis"]
    preferences = engine.get_tool_preferences(available_tools)
    
    for tool, score in preferences.items():
        print(f"  {tool}: {score:.3f}")
    
    # 4. Get Personalized Rankings
    print("\n--- Personalized Tool Ranking ---")
    
    ranking = engine.get_personalized_tool_ranking(available_tools, {"domain": "research"})
    
    for i, (tool, score) in enumerate(ranking, 1):
        print(f"  {i}. {tool}: {score:.3f}")
    
    # 5. Record Explicit Preference
    print("\n--- Recording Explicit Preferences ---")
    
    engine.record_explicit_preference(
        PreferenceType.COMPLEXITY_TOLERANCE, 
        "level", 
        0.8
    )
    print("  Recorded complexity tolerance preference")
    
    # 6. Get Statistics
    print("\n--- Engine Statistics ---")
    
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 7. Test Export/Import
    print("\n--- Export/Import Test ---")
    
    export_data = engine.export_profile()
    print(f"  Exported profile data with {len(export_data)} keys")
    
    new_engine = UserPreferenceEngine()
    import_success = new_engine.import_profile(export_data)
    print(f"  Import success: {import_success}")
    
    print("\n" + "=" * 60)
    print("  TEST COMPLETED SUCCESSFULLY")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        success = test_user_preference_engine()
        if success:
            print("\nTest completed successfully!")
        else:
            print("\nTest encountered errors")
            sys.exit(1)
            
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

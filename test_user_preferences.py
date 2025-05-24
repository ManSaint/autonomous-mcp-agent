#!/usr/bin/env python3
"""
Simple test script to verify UserPreferenceEngine compatibility fixes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_user_preference_engine():
    """Test the UserPreferenceEngine methods"""
    print("Testing UserPreferenceEngine compatibility...")
    
    try:
        from autonomous_mcp.user_preferences import UserPreferenceEngine
        print("✅ UserPreferenceEngine imported successfully")
        
        # Create instance
        engine = UserPreferenceEngine()
        print("✅ UserPreferenceEngine instantiated")
        
        # Test required methods exist
        required_methods = ['get_preferences', 'reset_preferences', 'update_preferences']
        for method in required_methods:
            if hasattr(engine, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False
        
        # Test get_preferences method
        try:
            prefs = engine.get_preferences()
            print(f"✅ get_preferences() returned: {type(prefs)}")
            print(f"✅ Keys: {list(prefs.keys())}")
            
            # Verify expected structure
            expected_keys = ['preferred_tools', 'avoided_tools', 'domain_interests', 'execution_preferences', 'privacy_settings']
            for key in expected_keys:
                if key in prefs:
                    print(f"✅ Key '{key}' present")
                else:
                    print(f"❌ Key '{key}' missing")
                    
        except Exception as e:
            print(f"❌ get_preferences() failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test reset_preferences method
        try:
            reset_result = engine.reset_preferences()
            print(f"✅ reset_preferences() returned: {type(reset_result)}")
        except Exception as e:
            print(f"❌ reset_preferences() failed: {e}")
            return False
        
        # Test update_preferences method
        try:
            test_prefs = {'test_key': 'test_value'}
            update_result = engine.update_preferences(test_prefs)
            print(f"✅ update_preferences() returned: {type(update_result)}")
        except Exception as e:
            print(f"❌ update_preferences() failed: {e}")
            return False
        
        print("🎉 All UserPreferenceEngine tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_autonomous_tools():
    """Test the autonomous tools with UserPreferenceEngine"""
    print("\nTesting AdvancedAutonomousTools with UserPreferenceEngine...")
    
    try:
        from autonomous_mcp.autonomous_tools import AdvancedAutonomousTools
        print("✅ AdvancedAutonomousTools imported successfully")
        
        # Create instance
        tools = AdvancedAutonomousTools()
        print("✅ AdvancedAutonomousTools instantiated")
        
        # Check if UserPreferenceEngine is properly initialized
        if hasattr(tools, 'preferences'):
            print("✅ preferences attribute exists")
            
            # Test if get_preferences method exists on the preferences object
            if hasattr(tools.preferences, 'get_preferences'):
                print("✅ preferences.get_preferences method exists")
            else:
                print("❌ preferences.get_preferences method missing")
                return False
        else:
            print("❌ preferences attribute missing")
            return False
        
        print("🎉 AdvancedAutonomousTools tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ AdvancedAutonomousTools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("USER PREFERENCE ENGINE COMPATIBILITY TEST")
    print("=" * 60)
    
    success1 = test_user_preference_engine()
    success2 = test_autonomous_tools()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED - UserPreferenceEngine compatibility fixed!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - UserPreferenceEngine needs more work")
        sys.exit(1)

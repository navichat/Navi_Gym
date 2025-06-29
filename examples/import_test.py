"""
Minimal test for Navi Gym imports.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_imports():
    """Test basic imports only."""
    print("Testing Navi Gym imports...")
    
    try:
        import navi_gym
        print("✅ navi_gym imported")
        
        from navi_gym.core import environments, agents, avatar_controller
        print("✅ Core modules imported")
        
        from navi_gym.integration import customer_api
        print("✅ Integration modules imported")
        
        from navi_gym.core.environments import BaseEnvironment, AvatarEnvironment
        print("✅ Environment classes imported")
        
        from navi_gym.core.agents import BaseAgent, PPOAgent, AvatarAgent
        print("✅ Agent classes imported")
        
        from navi_gym.core.avatar_controller import AvatarController, AvatarConfig
        print("✅ Avatar controller imported")
        
        from navi_gym.integration.customer_api import CustomerAPIBridge
        print("✅ Customer API bridge imported")
        
        print("\n🎉 All imports successful!")
        print("Navi Gym package structure is working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    test_imports()

# agents/test_agent.py - Test the AI agents easily
import json
import sys
import os

# Add the current directory to path so we can import our agent
sys.path.append(os.path.dirname(__file__))

from fitness_ai_single import main

def test_daily_insights():
    """Test daily insights functionality"""
    print("🧪 Testing Daily Insights...")
    
    test_data = {
        "request_type": "daily_insights",
        "data": {
            "steps": 5000,
            "sleepScore": 80,
            "recoveryStatus": "Good Recovery",
            "averageHeartRate": 75,
            "stressLevel": 25,
            "bodyBattery": 85
        }
    }
    
    # Simulate command line argument
    sys.argv = ['test_agent.py', json.dumps(test_data)]
    
    print("📊 Test data:", json.dumps(test_data, indent=2))
    print("\n🤖 AI Response:")
    print("-" * 50)
    
    main()

def test_chat():
    """Test chat functionality"""
    print("\n🧪 Testing Chat...")
    
    test_data = {
        "request_type": "chat",
        "message": "How's my recovery today?",
        "data": {
            "steps": 8500,
            "sleepScore": 78,
            "recoveryStatus": "Good Recovery",
            "stressLevel": 30
        }
    }
    
    # Simulate command line argument
    sys.argv = ['test_agent.py', json.dumps(test_data)]
    
    print("💬 Test message: 'How's my recovery today?'")
    print("\n🤖 AI Response:")
    print("-" * 50)
    
    main()

if __name__ == "__main__":
    print("🚀 Testing Fitness AI Agents")
    print("=" * 50)
    
    try:
        test_daily_insights()
        test_chat()
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("Check that CrewAI dependencies are installed correctly.")
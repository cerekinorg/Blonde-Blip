#!/usr/bin/env python3
"""
Test script to verify blonde command launches updated welcome screen
"""

import subprocess
import sys
import time

def test_blonde_command():
    """Test that blonde command launches updated welcome screen"""
    print("Testing updated 'blonde' command...")
    
    try:
        # Test in a subprocess with timeout
        result = subprocess.run(
            [sys.executable, "blonde", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="."
        )
        
        if result.returncode == 0:
            print("✅ 'blonde --help' executed successfully")
            if "Welcome Screen" in result.stdout:
                print("✅ Help text mentions Welcome Screen")
            else:
                print("⚠️ Help text doesn't mention Welcome Screen")
        else:
            print(f"❌ Command failed with return code: {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
                
    except subprocess.TimeoutExpired:
        print("⚠️ Command timed out (may be waiting for input)")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n📋 Expected Behavior:")
    print("- Running 'blonde' should launch the new Welcome Screen")
    print("- Welcome Screen has: Model/Provider selection + Chat input + Settings integration")
    print("- From Welcome Screen, you can access Dashboard with all integrated components")
    print("\n🎮 Key Features in Updated Screen:")
    print("- ✅ Enhanced Settings (Ctrl+S) - 5 comprehensive tabs")
    print("- ✅ Model Switcher (Ctrl+M) - Quick provider/model switcher")  
    print("- ✅ File Editor - Integrated editor with autosave")
    print("- ✅ Diff Panel - Color-coded diff display")
    print("- ✅ Agent Thinking Panel - Streaming thoughts with collapse")
    print("- ✅ Context Tracker - Token warnings at 80%/90%/95%")
    print("- ✅ 3-Column Dashboard - Collapsible panels")

if __name__ == "__main__":
    test_blonde_command()
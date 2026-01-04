#!/usr/bin/env python3
"""Test script for the updated welcome screen"""

import sys
import os
sys.path.insert(0, '.')

try:
    from tui.welcome_screen import WelcomeScreen, OPENCODE_LOGO, BLONDE_LOGO
    print("✓ WelcomeScreen class imported successfully")
    print("✓ OPENCODE_LOGO defined successfully")
    print("✓ BLONDE_LOGO defined successfully")
    print("✓ All imports working correctly")
    
    # Test logo display
    print("\n--- OpenCode Logo ---")
    print(OPENCODE_LOGO)
    print("\n--- Blonde Logo ---")
    print(BLONDE_LOGO)
    
    # Test that the class can be instantiated
    app = WelcomeScreen()
    print("✓ WelcomeScreen instantiated successfully")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

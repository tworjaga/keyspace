#!/usr/bin/env python3
"""Test script to diagnose import issues"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("Step 1: Importing basic modules...")
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    print("✓ PyQt6 imported successfully")
except Exception as e:
    print(f"✗ PyQt6 import failed: {e}")
    sys.exit(1)

print("\nStep 2: Importing integration manager...")
try:
    from backend.integrations.integration_manager import IntegrationManager, IntegrationConfig
    print("✓ IntegrationManager imported successfully")
except Exception as e:
    print(f"✗ IntegrationManager import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 3: Creating IntegrationConfig...")
try:
    config = IntegrationConfig(api_enabled=True, api_port=8080)
    print(f"✓ Config created: api_enabled={config.api_enabled}")
except Exception as e:
    print(f"✗ Config creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 4: Creating IntegrationManager...")
try:
    manager = IntegrationManager(config)
    print(f"✓ IntegrationManager created")
    print(f"  - API server: {manager.api_server}")

except Exception as e:
    print(f"✗ IntegrationManager creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 5: Testing API server start...")
if manager.api_server:
    try:
        result = manager.api_server.start()
        print(f"✓ API server start result: {result}")
        if result:
            print(f"  - Server running: {manager.api_server.is_running()}")
    except Exception as e:
        print(f"✗ API server start failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("✗ No API server available")

print("\nAll tests completed!")

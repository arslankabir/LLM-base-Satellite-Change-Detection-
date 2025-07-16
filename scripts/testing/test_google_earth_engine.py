#!/usr/bin/env python3
"""
🧪 Test Google Earth Engine Setup

This script helps test and configure Google Earth Engine properly.
"""

import os
import sys

def test_google_earth_engine():
    """Test Google Earth Engine setup"""
    print("🧪 Testing Google Earth Engine Setup")
    print("=" * 50)
    
    # Step 1: Check if earthengine-api is installed
    try:
        import ee
        print("✅ earthengine-api is installed")
    except ImportError:
        print("❌ earthengine-api not installed")
        print("💡 Install with: python -m pip install earthengine-api")
        return False
    
    # Step 2: Try to initialize without project
    try:
        print("🔄 Trying to initialize without project...")
        ee.Initialize()
        print("✅ Google Earth Engine initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        
        # Step 3: Try with default project
        try:
            print("🔄 Trying with default project...")
            ee.Initialize(project='earthengine-legacy')
            print("✅ Google Earth Engine initialized with default project!")
            return True
        except Exception as e2:
            print(f"❌ Default project failed: {e2}")
            
            # Step 4: Provide instructions
            print("\n🔧 Setup Instructions:")
            print("1. Go to: https://console.cloud.google.com/")
            print("2. Create a new project or select existing one")
            print("3. Enable Earth Engine API")
            print("4. Get your project ID")
            print("5. Run: ee.Initialize(project='your-project-id')")
            print()
            print("💡 Quick fix - try this:")
            print("   python -c \"import ee; ee.Initialize(project='earthengine-legacy'); print('Success!')\"")
            
            return False

def setup_environment():
    """Set up environment variables for Google Earth Engine"""
    print("\n🔧 Setting up environment...")
    
    # Set default project
    os.environ['EARTHENGINE_PROJECT'] = 'earthengine-legacy'
    
    print("✅ Environment variables set")
    print("   EARTHENGINE_PROJECT = earthengine-legacy")

def main():
    """Main function"""
    # Set up environment
    setup_environment()
    
    # Test Google Earth Engine
    success = test_google_earth_engine()
    
    if success:
        print("\n🎉 Google Earth Engine is ready!")
        print("\n🚀 You can now:")
        print("   • Download sample data: python download_google_earth_engine.py --source samples")
        print("   • Download specific areas with the download scripts")
        print("   • Use Google Earth Engine in your SatelliteLLM project")
    else:
        print("\n⚠️  Google Earth Engine needs additional setup")
        print("   Follow the instructions above to complete setup")

if __name__ == "__main__":
    main() 
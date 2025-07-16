#!/usr/bin/env python3
"""
Debug script to test frontend functionality and identify issues
"""

import requests
import os
from pathlib import Path

def test_frontend_upload():
    """Test the frontend upload functionality"""
    
    print("🔍 Testing Frontend Upload Functionality")
    print("=" * 50)
    
    # Check if high-resolution files exist
    before_file = Path("../data/gaza_high_res/gaza_strip_2023_10m.tif")
    after_file = Path("../data/gaza_2025_high_res/gaza_strip_2025_10m_20250715_084932.tif")
    
    if not before_file.exists():
        print(f"❌ Before file not found: {before_file}")
        return False
    
    if not after_file.exists():
        print(f"❌ After file not found: {after_file}")
        return False
    
    print(f"✅ Found before file: {before_file} ({before_file.stat().st_size / (1024*1024):.1f} MB)")
    print(f"✅ Found after file: {after_file} ({after_file.stat().st_size / (1024*1024):.1f} MB)")
    
    # Test API endpoint directly
    print("\n🧪 Testing API endpoint directly...")
    
    try:
        with open(before_file, 'rb') as before_f, open(after_file, 'rb') as after_f:
            files = {
                'before_image': ('gaza_2023_10m.tif', before_f, 'image/tiff'),
                'after_image': ('gaza_2025_10m.tif', after_f, 'image/tiff')
            }
            
            print("📡 Sending request to API...")
            response = requests.post('http://localhost:8000/generate-summary', files=files, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ API request successful!")
                print(f"📊 Summary: {result.get('summary', 'No summary')}")
                print(f"🎯 Confidence: {result.get('confidence', 0):.2f}")
                return True
            else:
                print(f"❌ API request failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        return False

def test_server_status():
    """Test if server is running"""
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def main():
    """Main debug function"""
    print("🏗️  Frontend Debug Test")
    print("=" * 50)
    
    # Test 1: Check server status
    if not test_server_status():
        print("\n💡 Start the server first: python main.py")
        return
    
    # Test 2: Test file upload
    if test_frontend_upload():
        print("\n✅ Frontend should work! Check browser console for errors.")
    else:
        print("\n❌ Frontend upload test failed. Check server logs.")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
🌍 Google Earth Engine Setup Script

This script sets up Google Earth Engine for downloading high-resolution satellite imagery.
Google Earth Engine is the BEST source for satellite data - it's free, easy to use, and has petabytes of data!
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package_name: str):
    """Install a Python package"""
    print(f"📦 Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False

def check_authentication():
    """Check if Google Earth Engine is authenticated"""
    try:
        import ee
        ee.Initialize()
        print("✅ Google Earth Engine is authenticated and ready!")
        return True
    except Exception as e:
        print(f"❌ Google Earth Engine not authenticated: {e}")
        return False

def main():
    """Main setup function"""
    print("🌍 Setting up Google Earth Engine for Satellite Imagery")
    print("=" * 60)
    print()
    print("🎯 Google Earth Engine is the BEST source for satellite data!")
    print("   • FREE access to petabytes of data")
    print("   • High-resolution imagery (10m-30m)")
    print("   • Easy Python API")
    print("   • Global coverage")
    print()
    
    # Step 1: Install required packages
    print("📋 Step 1: Installing required packages...")
    packages = [
        "earthengine-api",
        "requests",
        "numpy",
        "Pillow"
    ]
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
        print()
    
    if success_count < len(packages):
        print("⚠️  Some packages failed to install. Please check your internet connection.")
        return
    
    # Step 2: Check authentication
    print("🔐 Step 2: Checking Google Earth Engine authentication...")
    if not check_authentication():
        print()
        print("🔑 You need to authenticate with Google Earth Engine:")
        print("   1. Go to: https://signup.earthengine.google.com/")
        print("   2. Sign up for a FREE account")
        print("   3. Run: earthengine authenticate")
        print("   4. Follow the authentication process")
        print()
        print("💡 After authentication, run this script again to verify setup.")
        return
    
    # Step 3: Test download
    print("🧪 Step 3: Testing Google Earth Engine download...")
    try:
        from download_google_earth_engine import GoogleEarthEngineDownloader
        
        downloader = GoogleEarthEngineDownloader("test_gee")
        print("✅ Google Earth Engine downloader ready!")
        
    except Exception as e:
        print(f"❌ Error testing downloader: {e}")
        return
    
    print()
    print("🎉 Google Earth Engine setup complete!")
    print("=" * 60)
    print()
    print("🚀 You can now download high-resolution satellite imagery:")
    print()
    print("📥 Download sample datasets:")
    print("   python download_google_earth_engine.py --source samples")
    print()
    print("📥 Download specific area (Sentinel-2, 10m resolution):")
    print("   python download_google_earth_engine.py --source sentinel2 --bbox -74.1 40.7 -73.9 40.9 --start-date 2023-01-01 --end-date 2023-12-31")
    print()
    print("📥 Download specific area (Landsat, 30m resolution):")
    print("   python download_google_earth_engine.py --source landsat --bbox -74.1 40.7 -73.9 40.9 --start-date 2023-01-01 --end-date 2023-12-31")
    print()
    print("📥 Download high-resolution imagery (1-5m resolution):")
    print("   python download_google_earth_engine.py --source highres --bbox -74.1 40.7 -73.9 40.9 --start-date 2023-01-01 --end-date 2023-12-31")
    print()
    print("🎯 Test with your SatelliteLLM system:")
    print("   1. Start server: python main.py")
    print("   2. Upload downloaded imagery to web interface")
    print("   3. Get AI-powered analysis!")

if __name__ == "__main__":
    main() 
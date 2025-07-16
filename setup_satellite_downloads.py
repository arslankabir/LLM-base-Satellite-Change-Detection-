#!/usr/bin/env python3
"""
🔧 Setup Satellite Data Download Dependencies

This script installs the required packages for downloading high-resolution satellite imagery.
"""

import subprocess
import sys
from pathlib import Path

def install_package(package_name: str, pip_name: str = None):
    """Install a Python package"""
    if pip_name is None:
        pip_name = package_name
    
    print(f"📦 Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        print(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False

def main():
    """Main setup function"""
    print("🛰️  Setting up Satellite Data Download Dependencies")
    print("=" * 60)
    
    # Required packages for satellite data downloading
    packages = [
        ("sentinelsat", "sentinelsat"),  # For Sentinel-2 data
        ("landsatxplore", "landsatxplore"),  # For Landsat data
        ("rasterio", "rasterio"),  # For GeoTIFF processing
        ("requests", "requests"),  # For HTTP downloads
        ("numpy", "numpy"),  # For numerical operations
        ("Pillow", "Pillow"),  # For image processing
    ]
    
    print("📋 Installing required packages...")
    print()
    
    success_count = 0
    for package_name, pip_name in packages:
        if install_package(package_name, pip_name):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"✅ Setup complete! {success_count}/{len(packages)} packages installed successfully")
    
    if success_count == len(packages):
        print("\n🎉 All dependencies installed successfully!")
        print("\n🚀 You can now:")
        print("   1. Download sample data: python download_sample_data.py")
        print("   2. Download Sentinel-2 data: python download_satellite_data.py --source sentinel2")
        print("   3. Download Landsat data: python download_satellite_data.py --source landsat")
        print("   4. Test your system with high-resolution imagery")
    else:
        print("\n⚠️  Some packages failed to install. You may need to:")
        print("   1. Check your internet connection")
        print("   2. Update pip: python -m pip install --upgrade pip")
        print("   3. Install system dependencies (GDAL, etc.)")
        print("   4. Try installing packages individually")

if __name__ == "__main__":
    main() 
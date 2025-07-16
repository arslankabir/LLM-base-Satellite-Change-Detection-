#!/usr/bin/env python3
"""
🏗️ Google Earth Engine Setup for SatelliteLLM

This script sets up Google Earth Engine for the SatelliteLLM project,
including authentication, project configuration, and initial testing.

Prerequisites:
1. Google Earth Engine account (https://earthengine.google.com/)
2. Python 3.7+ with pip
3. Internet connection for authentication
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
import argparse

class GoogleEarthEngineSetup:
    """Google Earth Engine setup and configuration for SatelliteLLM"""
    
    def __init__(self, project_id: str = "unique-acronym-445710-k6"):
        self.project_id = project_id
        self.setup_dir = Path("gee_setup")
        self.setup_dir.mkdir(exist_ok=True)
        
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 7):
            print("❌ Python 3.7+ required")
            return False
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
        
        # Check if earthengine-api is installed
        try:
            import earthengine
            print("✅ earthengine-api is installed")
        except ImportError:
            print("❌ earthengine-api not installed")
            print("💡 Installing earthengine-api...")
            return self.install_earthengine_api()
        
        return True
    
    def install_earthengine_api(self) -> bool:
        """Install Google Earth Engine Python API"""
        try:
            print("📦 Installing earthengine-api...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "earthengine-api"])
            print("✅ earthengine-api installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install earthengine-api: {e}")
            return False
    
    def authenticate_gee(self) -> bool:
        """Authenticate with Google Earth Engine"""
        try:
            print("🔐 Authenticating with Google Earth Engine...")
            print("📋 This will open a browser window for authentication")
            print("💡 Follow the instructions in the browser to complete authentication")
            
            # Run earthengine authenticate
            result = subprocess.run(
                ["earthengine", "authenticate"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print("✅ Google Earth Engine authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Authentication timed out")
            return False
        except FileNotFoundError:
            print("❌ earthengine command not found")
            print("💡 Make sure earthengine-api is installed")
            return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_gee_connection(self) -> bool:
        """Test Google Earth Engine connection and project access"""
        try:
            print("🧪 Testing Google Earth Engine connection...")
            
            # Test script
            test_script = f"""
import ee
try:
    ee.Initialize(project='{self.project_id}')
    print("[OK] Google Earth Engine initialized successfully")
    print(f"[INFO] Project ID: {self.project_id}")
    
    # Test basic functionality
    test_image = ee.Image('USGS/SRTMGL1_003')
    bounds = test_image.geometry().bounds()
    print("[OK] Basic Earth Engine functionality working")
    
    # Test satellite collections
    sentinel2_collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    sentinel2_count = sentinel2_collection.size().getInfo()
    print(f"[OK] Sentinel-2 collection accessible ({{sentinel2_count}} images)")
    
    landsat_collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    landsat_count = landsat_collection.size().getInfo()
    print(f"[OK] Landsat collection accessible ({{landsat_count}} images)")
    
    print("[SUCCESS] All tests passed! Google Earth Engine is ready for use.")
    
except Exception as e:
    print(f"[ERROR] Test failed: {{e}}")
    exit(1)
"""
            
            # Save test script
            test_file = self.setup_dir / "test_gee.py"
            with open(test_file, 'w') as f:
                f.write(test_script)
            
            # Run test
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print(result.stdout)
            if result.stderr:
                print(f"⚠️  Warnings: {result.stderr}")
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
    
    def create_env_file(self) -> bool:
        """Create or update .env file with GEE configuration"""
        try:
            print("📝 Creating .env file with GEE configuration...")
            
            env_content = f"""# Google Earth Engine Configuration
GEE_PROJECT_ID={self.project_id}

# Ollama Configuration (for AI summaries)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# API Configuration
API_HOST=localhost
API_PORT=8000
"""
            
            env_file = Path(".env")
            
            # Read existing .env if it exists
            existing_content = ""
            if env_file.exists():
                with open(env_file, 'r') as f:
                    existing_content = f.read()
            
            # Merge with new GEE configuration
            if "GEE_PROJECT_ID" not in existing_content:
                with open(env_file, 'a') as f:
                    f.write(f"\n# Google Earth Engine Configuration\nGEE_PROJECT_ID={self.project_id}\n")
                print("✅ Added GEE configuration to existing .env file")
            else:
                print("✅ GEE configuration already exists in .env file")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    
    def create_sample_scripts(self) -> bool:
        """Create sample scripts for common GEE operations"""
        try:
            print("📄 Creating sample GEE scripts...")
            
            # Sample download script
            sample_download = '''#!/usr/bin/env python3
"""
Sample Google Earth Engine download script for SatelliteLLM

This script demonstrates how to download satellite imagery using GEE.
"""

import ee
import os
from pathlib import Path

def download_sample_imagery():
    """Download sample satellite imagery for testing"""
    
    # Initialize Earth Engine
    ee.Initialize(project='unique-acronym-445710-k6')
    
    # Define region of interest (example: small area)
    roi = ee.Geometry.Rectangle([34.2, 31.2, 34.6, 31.6])  # Gaza Strip area
    
    # Get Sentinel-2 imagery
    sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    
    # Filter for recent, cloud-free imagery
    filtered = sentinel2.filterBounds(roi)\\
                       .filterDate('2024-01-01', '2024-12-31')\\
                       .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))\\
                       .sort('CLOUDY_PIXEL_PERCENTAGE')
    
    # Get the best image
    image = filtered.first()
    
    if image:
        print("✅ Found suitable satellite imagery")
        
        # Prepare RGB bands
        rgb = image.select(['B4', 'B3', 'B2'])  # Red, Green, Blue
        rgb = rgb.divide(10000).multiply(255).byte()
        
        # Get download URL
        url = rgb.getThumbURL({
            'region': roi,
            'dimensions': '1024x1024',
            'format': 'png'
        })
        
        print(f"📥 Download URL: {url}")
        print("💡 Use this URL to download the image for testing")
        
    else:
        print("❌ No suitable imagery found")

if __name__ == "__main__":
    download_sample_imagery()
'''
            
            # Save sample script
            sample_file = self.setup_dir / "sample_download.py"
            with open(sample_file, 'w') as f:
                f.write(sample_download)
            
            print("✅ Created sample download script: gee_setup/sample_download.py")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create sample scripts: {e}")
            return False
    
    def run_full_setup(self) -> bool:
        """Run complete GEE setup process"""
        print("🏗️  Google Earth Engine Setup for SatelliteLLM")
        print("=" * 60)
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Step 2: Authenticate
        if not self.authenticate_gee():
            return False
        
        # Step 3: Test connection
        if not self.test_gee_connection():
            return False
        
        # Step 4: Create configuration
        if not self.create_env_file():
            return False
        
        # Step 5: Create sample scripts
        if not self.create_sample_scripts():
            return False
        
        print("\n🎉 Google Earth Engine setup completed successfully!")
        print("=" * 60)
        print("📋 Next steps:")
        print("   1. Test the sample script: python gee_setup/sample_download.py")
        print("   2. Run Gaza Strip download: python download_gaza_strip_data.py")
        print("   3. Start SatelliteLLM server: python main.py")
        print("=" * 60)
        
        return True

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Setup Google Earth Engine for SatelliteLLM")
    parser.add_argument("--project-id", default="unique-acronym-445710-k6",
                       help="Google Earth Engine project ID")
    parser.add_argument("--skip-auth", action="store_true",
                       help="Skip authentication (if already authenticated)")
    parser.add_argument("--test-only", action="store_true",
                       help="Only test existing setup")
    
    args = parser.parse_args()
    
    setup = GoogleEarthEngineSetup(args.project_id)
    
    if args.test_only:
        # Only test existing setup
        if setup.test_gee_connection():
            print("✅ Google Earth Engine is properly configured")
        else:
            print("❌ Google Earth Engine setup needs attention")
    else:
        # Run full setup
        setup.run_full_setup()

if __name__ == "__main__":
    main() 
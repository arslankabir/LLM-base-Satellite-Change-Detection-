#!/usr/bin/env python3
"""
🧪 Test 2023 vs 2025 Gaza Strip Analysis

This script tests the SatelliteLLM system with the specific 2023 and 2025 Gaza Strip files:
- 2023: gaza_high_res/gaza_strip_2023_10m.tif
- 2025: gaza_2025_high_res/gaza_strip_2025_10m_20250715_084932.tif
"""

import requests
import json
from pathlib import Path

def test_2023_vs_2025_analysis():
    """Test 2023 vs 2025 Gaza Strip analysis with SatelliteLLM system"""
    
    print("🧪 Testing 2023 vs 2025 Gaza Strip Analysis")
    print("=" * 60)
    
    # Define the specific files
    before_file = Path("gaza_high_res/gaza_strip_2023_10m.tif")
    after_file = Path("gaza_2025_high_res/gaza_strip_2025_10m_20250715_084932.tif")
    
    # Check if files exist
    if not before_file.exists():
        raise FileNotFoundError(f"2023 file not found: {before_file}")
    
    if not after_file.exists():
        raise FileNotFoundError(f"2025 file not found: {after_file}")
    
    print(f"📁 Found 2023 file: {before_file} ({before_file.stat().st_size / (1024*1024):.1f} MB)")
    print(f"📁 Found 2025 file: {after_file} ({after_file.stat().st_size / (1024*1024):.1f} MB)")
    print(f"📊 Analysis: 2023 vs 2025 (2-year comparison)")
    
    # Test the SatelliteLLM API
    print("\n🚀 Testing SatelliteLLM API with 2023 vs 2025 data...")
    
    url = "http://localhost:8000/generate-summary"
    
    try:
        with open(before_file, 'rb') as before_f, open(after_file, 'rb') as after_f:
            files = {
                'before_image': ('gaza_2023_10m.tif', before_f, 'image/tiff'),
                'after_image': ('gaza_2025_10m.tif', after_f, 'image/tiff')
            }
            
            print("📡 Uploading 2023 vs 2025 GeoTIFF files to SatelliteLLM...")
            print("   ⏳ This may take a few minutes due to large file sizes...")
            
            response = requests.post(url, files=files, timeout=300)  # 5 minute timeout
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ 2023 vs 2025 Gaza Strip Analysis Successful!")
                print("=" * 60)
                print(f"📊 Summary: {result['summary']}")
                print(f"🎯 Confidence: {result['confidence']:.2f}")
                print(f"🗺️  Map Overlay URL: {result['map_overlay_url']}")
                print("=" * 60)
                
                # Save results
                results_file = Path("gaza_2025_high_res/2023_vs_2025_analysis_results.json")
                results_file.parent.mkdir(exist_ok=True)
                with open(results_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"💾 Results saved to: {results_file}")
                
                print("\n🎯 Key Insights:")
                print("   • 2-year environmental change analysis (2023-2025)")
                print("   • High-resolution 10m satellite data")
                print("   • Professional NDVI/NDBI indices")
                print("   • AI-powered natural language summary")
                
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
                
    except Exception as e:
        raise Exception(f"Unexpected error: {e}. Make sure your SatelliteLLM server is running: python main.py")
    

def main():
    """Main function"""
    print("🏗️  2023 vs 2025 Gaza Strip Satellite Analysis")
    print("=" * 60)
    
    success = test_2023_vs_2025_analysis()
    
    if success:
        print("\n✅ Analysis completed successfully!")
        print("🌐 You can now use the frontend with these same files:")
        print("   • Before: gaza_high_res/gaza_strip_2023_10m.tif")
        print("   • After: gaza_2025_high_res/gaza_strip_2025_10m_20250715_084932.tif")
    else:
        print("\n❌ Analysis failed. Check the error messages above.")

if __name__ == "__main__":
    main() 
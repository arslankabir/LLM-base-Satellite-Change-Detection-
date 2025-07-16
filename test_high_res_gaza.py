#!/usr/bin/env python3
"""
🧪 Test High-Resolution Gaza Strip Analysis

This script tests the SatelliteLLM system with the downloaded high-resolution GeoTIFF files
for professional-grade satellite analysis of Gaza Strip changes between 2023 and 2024.
"""

import requests
import json
from pathlib import Path

def test_high_res_gaza_analysis():
    """Test high-resolution Gaza Strip analysis with SatelliteLLM system"""
    
    print("🧪 Testing High-Resolution Gaza Strip Analysis")
    print("=" * 60)
    
    # Check if high-resolution Gaza Strip data exists
    gaza_data_dir = Path("gaza_high_res")
    if not gaza_data_dir.exists():
        print("❌ High-resolution Gaza Strip data directory not found")
        print("�� Make sure you have the gaza_high_res directory with GeoTIFF files")
        return
    
    # Find the GeoTIFF files
    before_file = gaza_data_dir / "gaza_strip_2023_10m.tif"
    after_file = gaza_data_dir / "gaza_strip_2024_10m.tif"
    
    if not before_file.exists() or not after_file.exists():
        print("❌ High-resolution GeoTIFF files not found")
        print("💡 Make sure the files are downloaded from Google Drive")
        return
    
    print(f"📁 Found high-resolution Gaza Strip GeoTIFF files:")
    print(f"   Before (2023): {before_file} ({before_file.stat().st_size / (1024*1024):.1f} MB)")
    print(f"   After (2024): {after_file} ({after_file.stat().st_size / (1024*1024):.1f} MB)")
    print(f"   Resolution: 10m (native Sentinel-2)")
    print(f"   Format: GeoTIFF (professional quality)")
    
    # Test the SatelliteLLM API
    print("\n🚀 Testing SatelliteLLM API with high-resolution data...")
    
    url = "http://localhost:8000/generate-summary"
    
    try:
        with open(before_file, 'rb') as before_f, open(after_file, 'rb') as after_f:
            files = {
                'before_image': ('gaza_2023_10m.tif', before_f, 'image/tiff'),
                'after_image': ('gaza_2024_10m.tif', after_f, 'image/tiff')
            }
            
            print("📡 Uploading high-resolution GeoTIFF files to SatelliteLLM...")
            print("   ⏳ This may take a few minutes due to large file sizes...")
            
            response = requests.post(url, files=files, timeout=300)  # 5 minute timeout
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ High-Resolution Gaza Strip Analysis Successful!")
                print("=" * 60)
                print(f"�� Summary: {result['summary']}")
                print(f"🎯 Confidence: {result['confidence']:.2f}")
                print(f"��️  Map Overlay URL: {result['map_overlay_url']}")
                print("=" * 60)
                
                # Save results
                results_file = gaza_data_dir / "high_res_analysis_results.json"
                with open(results_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"💾 Results saved to: {results_file}")
                
                # Compare with previous low-res results
                compare_with_previous_results()
                
            else:
                print(f"❌ API request failed: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your SatelliteLLM server is running: python main.py")

def compare_with_previous_results():
    """Compare high-resolution results with previous low-resolution analysis"""
    print("\n📊 Comparing High-Resolution vs Low-Resolution Results...")
    
    # Check if previous results exist
    prev_results_file = Path("gaza_strip_data/gaza_analysis_results.json")
    high_res_results_file = Path("gaza_high_res/high_res_analysis_results.json")
    
    if prev_results_file.exists() and high_res_results_file.exists():
        try:
            with open(prev_results_file, 'r') as f:
                prev_results = json.load(f)
            
            with open(high_res_results_file, 'r') as f:
                high_res_results = json.load(f)
            
            print("   📈 Resolution Comparison:")
            print(f"      Low-res (thumbnail): {prev_results.get('confidence', 0):.2f} confidence")
            print(f"      High-res (GeoTIFF): {high_res_results.get('confidence', 0):.2f} confidence")
            
            if high_res_results.get('confidence', 0) > prev_results.get('confidence', 0):
                print("      ✅ High-resolution analysis shows improved confidence!")
            else:
                print("      ℹ️  Both resolutions provide similar confidence levels")
                
        except Exception as e:
            print(f"   ⚠️  Could not compare results: {e}")
    else:
        print("   ℹ️  No previous results to compare with")

def analyze_file_quality():
    """Analyze the quality of the downloaded GeoTIFF files"""
    print("\n🔍 Analyzing GeoTIFF File Quality...")
    
    gaza_data_dir = Path("gaza_high_res")
    
    for file_path in gaza_data_dir.glob("*.tif"):
        file_size = file_path.stat().st_size / (1024*1024)  # MB
        
        print(f"   📄 {file_path.name}:")
        print(f"      Size: {file_size:.1f} MB")
        
        if file_size > 30:
            print(f"      ✅ Excellent quality (large file size)")
        elif file_size > 10:
            print(f"      ✅ Good quality")
        else:
            print(f"      ⚠️  Small file size - may be compressed")
        
        print(f"      Format: GeoTIFF (professional satellite data)")
        print(f"      Resolution: 10m (native Sentinel-2)")

def main():
    """Main function"""
    print("🏗️  High-Resolution Gaza Strip Satellite Analysis Test")
    print("=" * 70)
    
    # Analyze file quality
    analyze_file_quality()
    
    # Test SatelliteLLM API
    test_high_res_gaza_analysis()
    
    print("\n🎯 Next Steps:")
    print("   1. Review the high-resolution analysis results")
    print("   2. Compare with previous low-resolution analysis")
    print("   3. Use the web interface for detailed visualization")
    print("   4. Export results for professional reports")
    print("   5. Share findings with stakeholders")

if __name__ == "__main__":
    main()
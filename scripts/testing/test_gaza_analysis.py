#!/usr/bin/env python3
"""
🧪 Test Gaza Strip Satellite Analysis

This script tests the SatelliteLLM system with the downloaded Gaza Strip imagery
for change detection analysis between 2023 and 2024.
"""

import requests
import json
from pathlib import Path

def test_gaza_analysis():
    """Test Gaza Strip analysis with SatelliteLLM system"""
    
    print("🧪 Testing Gaza Strip Satellite Analysis")
    print("=" * 50)
    
    # Check if Gaza Strip data exists
    gaza_data_dir = Path("../data/gaza_strip_data")
    if not gaza_data_dir.exists():
        print("❌ Gaza Strip data directory not found")
        print("💡 Run: python download_gaza_strip_data.py")
        return
    
    # Find the downloaded files
    before_file = None
    after_file = None
    
    # Look for 2023 and 2024 files
    for year_dir in gaza_data_dir.glob("gaza_sentinel2_*"):
        if "2023" in year_dir.name:
            for jpg_file in year_dir.glob("*.jpg"):
                before_file = jpg_file
                break
        elif "2024" in year_dir.name:
            for jpg_file in year_dir.glob("*.jpg"):
                after_file = jpg_file
                break
    
    if not before_file or not after_file:
        print("❌ Gaza Strip image files not found")
        print("💡 Run: python download_gaza_strip_data.py")
        return
    
    print(f"📁 Found Gaza Strip images:")
    print(f"   Before (2023): {before_file}")
    print(f"   After (2024): {after_file}")
    
    # Test the SatelliteLLM API
    print("\n🚀 Testing SatelliteLLM API...")
    
    url = "http://localhost:8000/generate-summary"
    
    try:
        with open(before_file, 'rb') as before_f, open(after_file, 'rb') as after_f:
            files = {
                'before_image': ('gaza_2023.jpg', before_f, 'image/jpeg'),
                'after_image': ('gaza_2024.jpg', after_f, 'image/jpeg')
            }
            
            print("📡 Uploading Gaza Strip images to SatelliteLLM...")
            response = requests.post(url, files=files)
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Gaza Strip Analysis Successful!")
                print("=" * 50)
                print(f"📊 Summary: {result['summary']}")
                print(f"🎯 Confidence: {result['confidence']:.2f}")
                print(f"🗺️  Map Overlay URL: {result['map_overlay_url']}")
                print("=" * 50)
                
                # Save results
                results_file = gaza_data_dir / "gaza_analysis_results.json"
                with open(results_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"💾 Results saved to: {results_file}")
                
            else:
                print(f"❌ API request failed: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your SatelliteLLM server is running: python main.py")

def test_llama_integration():
    """Test Llama integration with Gaza data"""
    print("\n🤖 Testing Llama Integration with Gaza Data...")
    
    try:
        from gpt_summary import generate_summary
        
        # Create sample change data for Gaza Strip
        gaza_change_data = {
            "overall_change_percentage": 15.5,
            "vegetation_changes": {
                "loss_percentage": 8.2,
                "gain_percentage": 2.1,
                "net_change": -6.1
            },
            "urban_development": {
                "growth_rate": 12.3,
                "decline_rate": 3.2,
                "net_urban_change": 9.1
            },
            "ndvi_changes": {
                "mean_ndvi_change": -0.15,
                "vegetation_health_decline": True
            },
            "ndbi_changes": {
                "mean_ndbi_change": 0.08,
                "urban_expansion": True
            },
            "change_type": "urban_expansion_and_vegetation_loss",
            "confidence_score": 0.87
        }
        
        print("📡 Testing Llama analysis of Gaza Strip changes...")
        summary, confidence = generate_summary(gaza_change_data)
        
        print("\n✅ Llama Analysis Results:")
        print("=" * 50)
        print(f"📊 Summary: {summary}")
        print(f"🎯 Confidence: {confidence:.2f}")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Llama integration error: {e}")

def main():
    """Main function"""
    print("🏗️  Gaza Strip Satellite Analysis Test")
    print("=" * 60)
    
    # Test SatelliteLLM API
    test_gaza_analysis()
    
    # Test Llama integration
    test_llama_integration()
    
    print("\n🎯 Next Steps:")
    print("   1. Review the analysis results")
    print("   2. Compare with other time periods if needed")
    print("   3. Use the web interface for detailed analysis")
    print("   4. Export results for further processing")

if __name__ == "__main__":
    main() 
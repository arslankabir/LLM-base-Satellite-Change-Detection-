import requests
import json
import os

def test_llama_integration():
    """Test the Llama integration directly"""
    print("🧪 Testing Llama Integration...")
    
    try:
        from gpt_summary import get_llm
        llm = get_llm()
        
        if llm:
            print("✅ Llama model successfully loaded!")
            
            # Test with sample satellite data
            test_data = {
                "analysis_type": "enhanced_rgb_with_satellite_simulation",
                "total_change_percentage": 5.2,
                "vegetation_changes": {
                    "loss_percentage": 2.1,
                    "gain_percentage": 0.5,
                    "net_change": -1.6,
                    "mean_ndvi_change": -0.15
                },
                "urban_changes": {
                    "growth_percentage": 1.8,
                    "decline_percentage": 0.2,
                    "net_change": 1.6,
                    "mean_ndbi_change": 0.12
                }
            }
            
            from gpt_summary import format_change_data, create_satellite_prompt
            formatted_data = format_change_data(test_data)
            prompt = create_satellite_prompt()
            
            print("📡 Testing satellite analysis prompt...")
            response = llm(prompt.format(change_data=formatted_data))
            print("✅ Llama Response:")
            print(response)
            
        else:
            print("❌ No Llama models available")
            
    except Exception as e:
        print(f"❌ Error testing Llama: {e}")

def test_enhanced_system():
    """Test the enhanced system with NDVI/NDBI analysis and LLM integration"""
    
    # API endpoint
    url = "http://localhost:8000/generate-summary"
    
    # Sample image files
    files = {
        'before_image': open('sample_data/before.jpg', 'rb'),
        'after_image': open('sample_data/after.jpg', 'rb')
    }
    
    try:
        print("🚀 Testing Enhanced SatelliteLLM System...")
        print("📡 Uploading sample satellite images...")
        
        # Make the request
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Enhanced System Test Successful!")
            print("=" * 50)
            print(f"📊 Summary: {result['summary']}")
            print(f"🎯 Confidence: {result['confidence']:.2f}")
            print(f"🗺️  Map Overlay URL: {result['map_overlay_url']}")
            print("=" * 50)
            
            # Test the frontend endpoint
            print("\n🌐 Testing Frontend Access...")
            frontend_response = requests.get("http://localhost:8000/frontend")
            if frontend_response.status_code == 200:
                print("✅ Frontend accessible at: http://localhost:8000/frontend")
            else:
                print("❌ Frontend not accessible")
                
        else:
            print(f"❌ Enhanced System Test Failed!")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Close the files
        files['before_image'].close()
        files['after_image'].close()

if __name__ == "__main__":
    # Test Llama integration first
    test_llama_integration()
    print("\n" + "="*60 + "\n")
    # Then test the full system
    test_enhanced_system() 
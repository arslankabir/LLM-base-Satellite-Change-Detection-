#!/usr/bin/env python3
"""
🔍 Diagnose Gaza Strip Data Analysis Issues

This script investigates why the analysis shows minimal changes when there should be
significant destruction from the war in Gaza (2023-2025).
"""

import numpy as np
import rasterio
from PIL import Image
import matplotlib.pyplot as plt
from pathlib import Path

def diagnose_geotiff_data(file_path: str, description: str):
    """Diagnose GeoTIFF data structure and content"""
    print(f"\n🔍 Diagnosing {description}: {file_path}")
    print("=" * 60)
    
    try:
        with rasterio.open(file_path) as src:
            print(f"📊 File Info:")
            print(f"   • Bands: {src.count}")
            print(f"   • Width: {src.width}")
            print(f"   • Height: {src.height}")
            print(f"   • CRS: {src.crs}")
            print(f"   • Transform: {src.transform}")
            print(f"   • Data type: {src.dtypes[0]}")
            
            # Read data
            data = src.read()
            print(f"\n📈 Data Statistics:")
            print(f"   • Shape: {data.shape}")
            print(f"   • Min values: {np.min(data, axis=(1,2))}")
            print(f"   • Max values: {np.max(data, axis=(1,2))}")
            print(f"   • Mean values: {np.mean(data, axis=(1,2))}")
            print(f"   • Std values: {np.std(data, axis=(1,2))}")
            
            # Check for valid data
            print(f"\n✅ Data Quality:")
            print(f"   • Non-zero pixels: {np.count_nonzero(data)}")
            print(f"   • Zero pixels: {np.sum(data == 0)}")
            print(f"   • NaN pixels: {np.sum(np.isnan(data))}")
            print(f"   • Inf pixels: {np.sum(np.isinf(data))}")
            
            # Check band configuration
            print(f"\n🎨 Band Analysis:")
            if data.shape[0] >= 4:
                print(f"   • Has NIR band (band 4): {data.shape[0] >= 4}")
                print(f"   • NIR range: {np.min(data[3])} to {np.max(data[3])}")
            if data.shape[0] >= 5:
                print(f"   • Has SWIR band (band 5): {data.shape[0] >= 5}")
                print(f"   • SWIR range: {np.min(data[4])} to {np.max(data[4])}")
            
            return data
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def compare_images_directly(before_path: str, after_path: str):
    """Compare images directly to see actual differences"""
    print(f"\n🔄 Direct Image Comparison")
    print("=" * 60)
    
    try:
        # Load as regular images for direct comparison
        before_img = Image.open(before_path).convert('RGB')
        after_img = Image.open(after_path).convert('RGB')
        
        before_arr = np.array(before_img)
        after_arr = np.array(after_img)
        
        print(f"📊 Image Info:")
        print(f"   • Before shape: {before_arr.shape}")
        print(f"   • After shape: {after_arr.shape}")
        
        # Calculate differences
        diff = np.abs(after_arr.astype(float) - before_arr.astype(float))
        
        print(f"\n📈 Difference Statistics:")
        print(f"   • Mean difference: {np.mean(diff):.2f}")
        print(f"   • Max difference: {np.max(diff):.2f}")
        print(f"   • Std difference: {np.std(diff):.2f}")
        
        # Calculate significant changes
        thresholds = [10, 20, 30, 50, 100]
        for threshold in thresholds:
            significant_pixels = np.sum(diff > threshold)
            percentage = (significant_pixels / diff.size) * 100
            print(f"   • Pixels > {threshold}: {significant_pixels} ({percentage:.2f}%)")
        
        # Channel-specific analysis
        print(f"\n🎨 Channel Analysis:")
        for i, channel in enumerate(['Red', 'Green', 'Blue']):
            channel_diff = diff[:,:,i]
            significant = np.sum(channel_diff > 30)
            percentage = (significant / channel_diff.size) * 100
            print(f"   • {channel}: {significant} pixels > 30 ({percentage:.2f}%)")
        
        return diff
        
    except Exception as e:
        print(f"❌ Error in direct comparison: {e}")
        return None

def check_geotiff_band_order(before_path: str, after_path: str):
    """Check if GeoTIFF band order is correct for NDVI/NDBI calculation"""
    print(f"\n🎯 GeoTIFF Band Order Check")
    print("=" * 60)
    
    try:
        with rasterio.open(before_path) as before_src:
            before_data = before_src.read()
        
        with rasterio.open(after_path) as after_src:
            after_data = after_src.read()
        
        print(f"📊 Band Configuration:")
        print(f"   • Before bands: {before_data.shape[0]}")
        print(f"   • After bands: {after_data.shape[0]}")
        
        # Check if we have enough bands for NDVI/NDBI
        if before_data.shape[0] < 4:
            print(f"❌ WARNING: Only {before_data.shape[0]} bands available")
            print(f"   • Need at least 4 bands for NDVI (Red + NIR)")
            print(f"   • Need at least 5 bands for NDBI (NIR + SWIR)")
            print(f"   • Falling back to RGB analysis")
            return False
        
        # Test NDVI calculation
        print(f"\n🌱 NDVI Test:")
        before_ndvi = calculate_test_ndvi(before_data)
        after_ndvi = calculate_test_ndvi(after_data)
        
        if before_ndvi is not None and after_ndvi is not None:
            ndvi_diff = after_ndvi - before_ndvi
            print(f"   • Before NDVI range: {np.min(before_ndvi):.3f} to {np.max(before_ndvi):.3f}")
            print(f"   • After NDVI range: {np.min(after_ndvi):.3f} to {np.max(after_ndvi):.3f}")
            print(f"   • NDVI change range: {np.min(ndvi_diff):.3f} to {np.max(ndvi_diff):.3f}")
            print(f"   • Mean NDVI change: {np.mean(ndvi_diff):.3f}")
            
            # Check for significant changes
            significant_loss = np.sum(ndvi_diff < -0.1)
            significant_gain = np.sum(ndvi_diff > 0.1)
            total_pixels = ndvi_diff.size
            
            print(f"   • Significant vegetation loss: {significant_loss} pixels ({(significant_loss/total_pixels)*100:.2f}%)")
            print(f"   • Significant vegetation gain: {significant_gain} pixels ({(significant_gain/total_pixels)*100:.2f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in band order check: {e}")
        return False

def calculate_test_ndvi(data):
    """Calculate NDVI for testing"""
    try:
        if data.shape[0] >= 4:
            # Assuming bands: Blue(0), Green(1), Red(2), NIR(3)
            red_band = data[2].astype(float)
            nir_band = data[3].astype(float)
            
            # Avoid division by zero
            denominator = nir_band + red_band
            denominator[denominator == 0] = 1e-10
            
            ndvi = (nir_band - red_band) / denominator
            return ndvi
        return None
    except Exception as e:
        print(f"❌ Error calculating NDVI: {e}")
        return None

def main():
    """Main diagnostic function"""
    print("🔍 Gaza Strip Data Diagnostic")
    print("=" * 60)
    print("Investigating why analysis shows minimal changes when significant")
    print("destruction should be detected from the war (2023-2025)")
    print("=" * 60)
    
    # File paths
    before_file = "gaza_high_res/gaza_strip_2023_10m.tif"
    after_file = "gaza_2025_high_res/gaza_strip_2025_10m_20250715_084932.tif"
    
    # Check if files exist
    if not Path(before_file).exists():
        print(f"❌ Before file not found: {before_file}")
        return
    
    if not Path(after_file).exists():
        print(f"❌ After file not found: {after_file}")
        return
    
    # Diagnose individual files
    before_data = diagnose_geotiff_data(before_file, "2023 Gaza Strip")
    after_data = diagnose_geotiff_data(after_file, "2025 Gaza Strip")
    
    # Direct comparison
    diff_data = compare_images_directly(before_file, after_file)
    
    # Check GeoTIFF band configuration
    band_check = check_geotiff_band_order(before_file, after_file)
    
    print(f"\n🎯 Diagnostic Summary")
    print("=" * 60)
    print("Based on the analysis above, potential issues could be:")
    print("1. Incorrect band order in GeoTIFF files")
    print("2. Data normalization/scaling issues")
    print("3. Cloud cover or atmospheric conditions")
    print("4. Different acquisition dates affecting comparison")
    print("5. Resolution or projection differences")
    print("6. Data quality issues in the source imagery")

if __name__ == "__main__":
    main() 
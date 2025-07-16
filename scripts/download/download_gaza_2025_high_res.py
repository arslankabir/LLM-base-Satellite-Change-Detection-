#!/usr/bin/env python3
"""
🏗️ Gaza Strip 2025 High-Resolution GeoTIFF Downloader

This script downloads high-resolution GeoTIFF satellite imagery for the Gaza Strip area
for 2025 and exports it to Google Drive for full-resolution analysis.

Similar to the 2023/2024 high-resolution downloads in gaza_high_res/
"""

import os
import ee
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import argparse
from pathlib import Path
import time
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

class GazaStrip2025HighResDownloader:
    """Download high-resolution GeoTIFF satellite imagery for Gaza Strip area including 2025"""
    
    def __init__(self, output_dir: str = "gaza_2025_high_res"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Gaza Strip bounding box (approximate)
        # Coordinates: [min_lon, min_lat, max_lon, max_lat]
        self.gaza_bbox = (34.2, 31.2, 34.6, 31.6)
        
        # Initialize Google Earth Engine
        try:
            project_id = os.getenv('GEE_PROJECT_ID')
            if not project_id:
                raise ValueError("GEE_PROJECT_ID not found in .env file")
            ee.Initialize(project=project_id)
            print("✅ Google Earth Engine initialized for high-resolution 2025 Gaza analysis")
        except Exception as e:
            print(f"❌ Error initializing Google Earth Engine: {e}")
            return
    
    def download_gaza_2025_high_res(self,
                                   year: int,
                                   month_start: int = 1,
                                   month_end: int = 12,
                                   max_cloud_cover: int = 20) -> List[str]:
        """
        Download high-resolution GeoTIFF satellite imagery for Gaza Strip for a specific year
        
        Args:
            year: Year to download (2023, 2024, 2025)
            month_start: Start month (1-12)
            month_end: End month (1-12)
            max_cloud_cover: Maximum cloud cover percentage
            
        Returns:
            List of downloaded file paths
        """
        try:
            print(f"🛰️  Downloading Gaza Strip high-resolution imagery for {year}...")
            
            # Define the Gaza Strip region of interest
            min_lon, min_lat, max_lon, max_lat = self.gaza_bbox
            roi = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])
            
            # Date range
            start_date = f"{year}-{month_start:02d}-01"
            end_date = f"{year}-{month_end:02d}-28"
            
            print(f"   Area: Gaza Strip ({min_lon}, {min_lat}, {max_lon}, {max_lat})")
            print(f"   Date range: {start_date} to {end_date}")
            print(f"   Max cloud cover: {max_cloud_cover}%")
            
            # Try Sentinel-2 first (10m resolution)
            try:
                print("🔍 Searching for Sentinel-2 imagery...")
                sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                
                filtered = sentinel2.filterBounds(roi)\
                                   .filterDate(start_date, end_date)\
                                   .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_cloud_cover))\
                                   .sort('CLOUDY_PIXEL_PERCENTAGE')
                
                image = filtered.first()
                
                if image:
                    cloud_cover = image.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()
                    print(f"✅ Found Sentinel-2 image with {cloud_cover}% cloud cover")
                    return self._export_high_res_geotiff(image, roi, f"gaza_strip_{year}_10m")
                else:
                    print("⚠️  No Sentinel-2 images found, trying Landsat...")
                    
            except Exception as e:
                print(f"⚠️  Sentinel-2 failed: {e}, trying Landsat...")
            
            # Try Landsat as fallback (30m resolution)
            try:
                print("🔍 Searching for Landsat imagery...")
                landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                
                filtered = landsat.filterBounds(roi)\
                                 .filterDate(start_date, end_date)\
                                 .filter(ee.Filter.lt('CLOUD_COVER', max_cloud_cover))\
                                 .sort('CLOUD_COVER')
                
                image = filtered.first()
                
                if image:
                    cloud_cover = image.get('CLOUD_COVER').getInfo()
                    print(f"✅ Found Landsat image with {cloud_cover}% cloud cover")
                    return self._export_high_res_geotiff(image, roi, f"gaza_strip_{year}_30m")
                else:
                    print("❌ No Landsat images found either")
                    return []
                    
            except Exception as e:
                print(f"❌ Landsat failed: {e}")
                return []
            
        except Exception as e:
            print(f"❌ Error downloading Gaza Strip data: {e}")
            return []
    
    def download_gaza_2025_comparison_high_res(self,
                                              year1: int = 2024,
                                              year2: int = 2025,
                                              max_cloud_cover: int = 20) -> Dict[str, str]:
        """
        Download high-resolution before/after imagery for Gaza Strip comparison including 2025
        
        Args:
            year1: First year (before)
            year2: Second year (after) - can be 2025
            max_cloud_cover: Maximum cloud cover percentage
            
        Returns:
            Dictionary with before/after file paths
        """
        print(f"🔄 Downloading Gaza Strip high-resolution comparison: {year1} vs {year2}")
        
        results = {}
        
        # Download first year
        files1 = self.download_gaza_2025_high_res(year1, max_cloud_cover=max_cloud_cover)
        if files1:
            results[f"before_{year1}"] = files1[0]
            print(f"✅ Downloaded {year1} high-resolution imagery: {files1[0]}")
        
        # Download second year
        files2 = self.download_gaza_2025_high_res(year2, max_cloud_cover=max_cloud_cover)
        if files2:
            results[f"after_{year2}"] = files2[0]
            print(f"✅ Downloaded {year2} high-resolution imagery: {files2[0]}")
        
        return results
    
    def _export_high_res_geotiff(self, image, roi, dataset_name: str) -> List[str]:
        """Export high-resolution GeoTIFF to Google Drive"""
        try:
            print(f"📤 Exporting high-resolution GeoTIFF: {dataset_name}")
            
            # Get image info
            image_info = image.getInfo()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Prepare RGB bands for export
            # For Sentinel-2: B4 (Red), B3 (Green), B2 (Blue)
            # For Landsat: SR_B4 (Red), SR_B3 (Green), SR_B2 (Blue)
            
            # Check if it's Sentinel-2 or Landsat based on available bands
            bands = [band['id'] for band in image_info['bands']]
            
            if 'B4' in bands and 'B3' in bands and 'B2' in bands:
                # Sentinel-2
                rgb_image = image.select(['B4', 'B3', 'B2'])  # Red, Green, Blue
                rgb_image = rgb_image.divide(10000).multiply(255).byte()  # Scale to 0-255
                print("   Using Sentinel-2 bands (B4, B3, B2)")
            elif 'SR_B4' in bands and 'SR_B3' in bands and 'SR_B2' in bands:
                # Landsat
                rgb_image = image.select(['SR_B4', 'SR_B3', 'SR_B2'])  # Red, Green, Blue
                rgb_image = rgb_image.divide(10000).multiply(255).byte()  # Scale to 0-255
                print("   Using Landsat bands (SR_B4, SR_B3, SR_B2)")
            else:
                print("⚠️  Unknown band structure, using first 3 bands")
                rgb_image = image.select(bands[:3])
            
            # Create export task
            export_task = ee.batch.Export.image.toDrive(
                image=rgb_image,
                description=f"{dataset_name}_{timestamp}",
                folder="Gaza_Strip_High_Res_2025",
                fileNamePrefix=f"{dataset_name}_{timestamp}",
                region=roi,
                scale=10,  # 10m resolution for Sentinel-2, will be resampled for Landsat
                crs='EPSG:4326',
                fileFormat='GeoTIFF',
                maxPixels=1e13
            )
            
            # Start the export
            export_task.start()
            print(f"🚀 Started export task: {export_task.id}")
            
            # Wait for completion
            print("⏳ Waiting for export to complete...")
            while export_task.status()['state'] in ['READY', 'RUNNING']:
                print(f"   Status: {export_task.status()['state']}")
                time.sleep(30)  # Check every 30 seconds
            
            if export_task.status()['state'] == 'COMPLETED':
                print(f"✅ Export completed successfully!")
                print(f"📁 File will be available in Google Drive folder: Gaza_Strip_High_Res_2025")
                print(f"📄 Filename: {dataset_name}_{timestamp}.tif")
                
                # Save export info to local file
                export_info = {
                    'task_id': export_task.id,
                    'status': export_task.status()['state'],
                    'filename': f"{dataset_name}_{timestamp}.tif",
                    'drive_folder': "Gaza_Strip_High_Res_2025",
                    'timestamp': timestamp,
                    'dataset_name': dataset_name
                }
                
                info_file = self.output_dir / f"{dataset_name}_{timestamp}_export_info.json"
                with open(info_file, 'w') as f:
                    json.dump(export_info, f, indent=2)
                
                print(f"💾 Export info saved to: {info_file}")
                return [str(info_file)]
                
            else:
                print(f"❌ Export failed: {export_task.status()}")
                return []
                
        except Exception as e:
            print(f"❌ Error exporting high-resolution GeoTIFF: {e}")
            return []

def main():
    """Main function to download Gaza Strip 2025 high-resolution data"""
    parser = argparse.ArgumentParser(description="Download Gaza Strip high-resolution GeoTIFF imagery including 2025")
    parser.add_argument("--output", default="gaza_2025_high_res", help="Output directory")
    parser.add_argument("--year1", type=int, default=2024, help="First year for comparison")
    parser.add_argument("--year2", type=int, default=2025, help="Second year for comparison")
    parser.add_argument("--cloud-cover", type=int, default=20, help="Maximum cloud cover percentage")
    
    args = parser.parse_args()
    
    print("🏗️  Gaza Strip 2025 High-Resolution GeoTIFF Downloader")
    print("=" * 70)
    print("📤 This will export full-resolution GeoTIFF files to Google Drive")
    print("📁 Files will be saved in: Gaza_Strip_High_Res_2025 folder")
    print("=" * 70)
    
    downloader = GazaStrip2025HighResDownloader(args.output)
    
    # Download comparison between two years
    results = downloader.download_gaza_2025_comparison_high_res(
        year1=args.year1,
        year2=args.year2,
        max_cloud_cover=args.cloud_cover
    )
    
    print("\n📊 High-Resolution Export Results:")
    for key, file_path in results.items():
        print(f"   {key}: {file_path}")
    
    print(f"\n✅ Export tasks completed!")
    print("📁 Check your Google Drive folder: Gaza_Strip_High_Res_2025")
    print("⏱️  Large files may take several minutes to appear in Drive")
    print("📄 Download the .tif files and place them in your project directory")

if __name__ == "__main__":
    main() 
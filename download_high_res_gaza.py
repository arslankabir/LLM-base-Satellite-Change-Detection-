#!/usr/bin/env python3
"""
🛰️ High-Resolution Gaza Strip GeoTIFF Downloader

This script downloads full-resolution GeoTIFF files from Google Earth Engine
for high-quality satellite analysis of the Gaza Strip area.

Note: This requires Google Drive API setup for full-resolution downloads.
"""

import os
import ee
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse
from pathlib import Path
import time

class HighResGazaDownloader:
    """Download high-resolution GeoTIFF files for Gaza Strip"""
    
    def __init__(self, output_dir: str = "gaza_high_res"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Gaza Strip bounding box (approximate)
        self.gaza_bbox = (34.2, 31.2, 34.6, 31.6)
        
        # Initialize Google Earth Engine
        try:
            ee.Initialize(project='unique-acronym-445710-k6')
            print("✅ Google Earth Engine initialized for high-resolution Gaza analysis")
        except Exception as e:
            print(f"❌ Error initializing Google Earth Engine: {e}")
            return
    
    def download_high_res_gaza(self,
                              year: int,
                              max_cloud_cover: int = 20,
                              scale: int = 10) -> str:
        """
        Download high-resolution GeoTIFF for Gaza Strip
        
        Args:
            year: Year to download
            max_cloud_cover: Maximum cloud cover percentage
            scale: Pixel resolution in meters (10m for Sentinel-2)
            
        Returns:
            Task ID for monitoring
        """
        try:
            print(f"🛰️  Preparing high-resolution Gaza Strip download for {year}...")
            
            # Define the Gaza Strip region of interest
            min_lon, min_lat, max_lon, max_lat = self.gaza_bbox
            roi = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])
            
            # Date range
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            
            print(f"   Area: Gaza Strip ({min_lon}, {min_lat}, {max_lon}, {max_lat})")
            print(f"   Date range: {start_date} to {end_date}")
            print(f"   Resolution: {scale}m")
            print(f"   Max cloud cover: {max_cloud_cover}%")
            
            # Get Sentinel-2 imagery
            sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
            
            filtered = sentinel2.filterBounds(roi)\
                               .filterDate(start_date, end_date)\
                               .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_cloud_cover))\
                               .sort('CLOUDY_PIXEL_PERCENTAGE')
            
            image = filtered.first()
            
            if not image:
                print("❌ No Sentinel-2 images found")
                return None
            
            cloud_cover = image.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()
            print(f"✅ Found Sentinel-2 image with {cloud_cover}% cloud cover")
            
            # Prepare RGB image
            rgb_image = image.select(['B4', 'B3', 'B2'])  # Red, Green, Blue
            rgb_image = rgb_image.divide(10000).multiply(255).byte()  # Scale to 0-255
            
            # Export to Google Drive as GeoTIFF
            filename = f"gaza_strip_{year}_{scale}m"
            
            task = ee.batch.Export.image.toDrive(
                image=rgb_image,
                description=filename,
                folder='Gaza_Strip_Satellite_Data',
                fileNamePrefix=filename,
                region=roi,
                scale=scale,
                crs='EPSG:4326',
                fileFormat='GeoTIFF',
                maxPixels=1e13
            )
            
            task.start()
            print(f"🚀 Export task started: {task.id}")
            print(f"📁 File will be saved to Google Drive folder: 'Gaza_Strip_Satellite_Data'")
            print(f"📄 Filename: {filename}.tif")
            
            return task.id
            
        except Exception as e:
            print(f"❌ Error preparing high-resolution download: {e}")
            return None
    
    def download_multiple_years(self, years: List[int], scale: int = 10) -> Dict[str, str]:
        """Download high-resolution data for multiple years"""
        print(f"🔄 Downloading high-resolution Gaza Strip data for years: {years}")
        
        task_ids = {}
        
        for year in years:
            task_id = self.download_high_res_gaza(year, scale=scale)
            if task_id:
                task_ids[f"gaza_{year}"] = task_id
                print(f"✅ Task started for {year}: {task_id}")
            
            # Wait between tasks to avoid rate limiting
            time.sleep(2)
        
        # Save task IDs for monitoring
        tasks_file = self.output_dir / "export_tasks.json"
        with open(tasks_file, 'w') as f:
            json.dump(task_ids, f, indent=2)
        
        print(f"💾 Task IDs saved to: {tasks_file}")
        return task_ids
    
    def check_task_status(self, task_id: str) -> str:
        """Check the status of an export task"""
        try:
            task = ee.batch.Task(task_id)
            status = task.status()
            return status['state']
        except Exception as e:
            print(f"❌ Error checking task status: {e}")
            return "UNKNOWN"
    
    def monitor_tasks(self, task_ids: Dict[str, str]):
        """Monitor export tasks"""
        print("📊 Monitoring export tasks...")
        
        while True:
            all_completed = True
            
            for name, task_id in task_ids.items():
                status = self.check_task_status(task_id)
                print(f"   {name}: {status}")
                
                if status not in ['COMPLETED', 'FAILED']:
                    all_completed = False
            
            if all_completed:
                print("✅ All tasks completed!")
                break
            
            print("⏳ Waiting 30 seconds before next check...")
            time.sleep(30)
    
    def create_analysis_guide(self):
        """Create a guide for using the downloaded GeoTIFF files"""
        guide = {
            "title": "Gaza Strip High-Resolution Satellite Analysis Guide",
            "description": "Guide for analyzing high-resolution GeoTIFF files",
            "files_location": "Google Drive > Gaza_Strip_Satellite_Data",
            "file_format": "GeoTIFF (.tif)",
            "resolution": "10m (Sentinel-2)",
            "coordinate_system": "EPSG:4326 (Geographic)",
            "bands": {
                "B4": "Red band",
                "B3": "Green band", 
                "B2": "Blue band"
            },
            "analysis_steps": [
                "1. Download GeoTIFF files from Google Drive",
                "2. Use GIS software (QGIS, ArcGIS) for detailed analysis",
                "3. Upload to SatelliteLLM web interface for AI analysis",
                "4. Compare before/after images for change detection",
                "5. Generate NDVI/NDBI indices for environmental analysis"
            ],
            "recommended_software": [
                "QGIS (free)",
                "ArcGIS Pro",
                "ENVI",
                "Google Earth Pro"
            ]
        }
        
        guide_file = self.output_dir / "analysis_guide.json"
        with open(guide_file, 'w') as f:
            json.dump(guide, f, indent=2)
        
        print(f"📖 Analysis guide saved to: {guide_file}")
        return guide

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Download high-resolution GeoTIFF files for Gaza Strip")
    parser.add_argument("--years", nargs="+", type=int, default=[2023, 2024],
                       help="Years to download (default: 2023 2024)")
    parser.add_argument("--scale", type=int, default=10,
                       help="Pixel resolution in meters (default: 10)")
    parser.add_argument("--monitor", action="store_true",
                       help="Monitor export tasks")
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = HighResGazaDownloader()
    
    # Download high-resolution data
    task_ids = downloader.download_multiple_years(args.years, args.scale)
    
    if task_ids:
        print(f"\n✅ Started {len(task_ids)} export tasks")
        
        # Create analysis guide
        guide = downloader.create_analysis_guide()
        
        print("\n📋 Next Steps:")
        print("1. Check Google Drive folder: 'Gaza_Strip_Satellite_Data'")
        print("2. Wait for GeoTIFF files to complete (may take 10-30 minutes)")
        print("3. Download the .tif files to your local machine")
        print("4. Use GIS software or upload to SatelliteLLM for analysis")
        
        if args.monitor:
            print("\n📊 Monitoring tasks...")
            downloader.monitor_tasks(task_ids)
    
    else:
        print("❌ No tasks were started")

if __name__ == "__main__":
    main() 
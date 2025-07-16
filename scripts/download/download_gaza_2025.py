#!/usr/bin/env python3
"""
🏗️ Gaza Strip 2025 Satellite Imagery Downloader

This script downloads high-resolution satellite imagery for the Gaza Strip area
for 2025 and creates comparison datasets with previous years.

Available periods: 2023, 2024, 2025 (current year)
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

class GazaStrip2025Downloader:
    """Download satellite imagery for Gaza Strip area including 2025 data"""
    
    def __init__(self, output_dir: str = "gaza_2025_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Gaza Strip bounding box (approximate)
        # Coordinates: [min_lon, min_lat, max_lon, max_lat]
        self.gaza_bbox = (34.2, 31.2, 34.6, 31.6)
        
        # Initialize Google Earth Engine
        try:
            ee.Initialize(project='unique-acronym-445710-k6')
            print("✅ Google Earth Engine initialized for Gaza Strip 2025 analysis")
        except Exception as e:
            print(f"❌ Error initializing Google Earth Engine: {e}")
            return
    
    def download_gaza_2025_imagery(self,
                                  year: int,
                                  month_start: int = 1,
                                  month_end: int = 12,
                                  max_cloud_cover: int = 20) -> List[str]:
        """
        Download satellite imagery for Gaza Strip for a specific year
        
        Args:
            year: Year to download (2023, 2024, 2025)
            month_start: Start month (1-12)
            month_end: End month (1-12)
            max_cloud_cover: Maximum cloud cover percentage
            
        Returns:
            List of downloaded file paths
        """
        try:
            print(f"🛰️  Downloading Gaza Strip imagery for {year}...")
            
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
                    return self._download_ee_image(image, roi, f"gaza_sentinel2_{year}")
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
                    return self._download_ee_image(image, roi, f"gaza_landsat_{year}")
                else:
                    print("❌ No Landsat images found either")
                    return []
                    
            except Exception as e:
                print(f"❌ Landsat failed: {e}")
                return []
            
        except Exception as e:
            print(f"❌ Error downloading Gaza Strip data: {e}")
            return []
    
    def download_gaza_2025_comparison(self,
                                     year1: int = 2024,
                                     year2: int = 2025,
                                     max_cloud_cover: int = 20) -> Dict[str, str]:
        """
        Download before/after imagery for Gaza Strip comparison including 2025
        
        Args:
            year1: First year (before)
            year2: Second year (after) - can be 2025
            max_cloud_cover: Maximum cloud cover percentage
            
        Returns:
            Dictionary with before/after file paths
        """
        print(f"🔄 Downloading Gaza Strip comparison: {year1} vs {year2}")
        
        results = {}
        
        # Download first year
        files1 = self.download_gaza_2025_imagery(year1, max_cloud_cover=max_cloud_cover)
        if files1:
            results[f"before_{year1}"] = files1[0]
            print(f"✅ Downloaded {year1} imagery: {files1[0]}")
        
        # Download second year
        files2 = self.download_gaza_2025_imagery(year2, max_cloud_cover=max_cloud_cover)
        if files2:
            results[f"after_{year2}"] = files2[0]
            print(f"✅ Downloaded {year2} imagery: {files2[0]}")
        
        return results
    
    def download_gaza_2025_timeline(self,
                                   years: List[int] = [2023, 2024, 2025],
                                   max_cloud_cover: int = 20) -> Dict[str, str]:
        """
        Download imagery for multiple years to create a timeline analysis
        
        Args:
            years: List of years to download
            max_cloud_cover: Maximum cloud cover percentage
            
        Returns:
            Dictionary with year: file_path mappings
        """
        print(f"📅 Downloading Gaza Strip timeline: {years}")
        
        results = {}
        
        for year in years:
            files = self.download_gaza_2025_imagery(year, max_cloud_cover=max_cloud_cover)
            if files:
                results[str(year)] = files[0]
                print(f"✅ Downloaded {year} imagery: {files[0]}")
            else:
                print(f"❌ Failed to download {year} imagery")
        
        return results
    
    def _download_ee_image(self, image, roi, dataset_name: str) -> List[str]:
        """Download an Earth Engine image in high resolution"""
        try:
            # Create output directory
            output_dir = self.output_dir / dataset_name
            output_dir.mkdir(exist_ok=True)
            
            # Get image info
            image_info = image.getInfo()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Download RGB bands (Sentinel-2 uses different band names)
            # Available bands: B1, B2, B3, B4, B5, B6, B7, B8, B8A, B9, B11, B12
            # For RGB: B4 (Red), B3 (Green), B2 (Blue)
            rgb_image = image.select(['B4', 'B3', 'B2'])  # Red, Green, Blue
            rgb_image = rgb_image.divide(10000).multiply(255).byte()  # Scale to 0-255
            
            filename = f"{dataset_name}_{timestamp}"
            
            # Method 1: Try high-resolution thumbnail (better quality)
            try:
                print("📥 Downloading high-resolution image...")
                thumb_url = rgb_image.getThumbURL({
                    'region': roi,
                    'dimensions': '2048x2048',  # Higher resolution
                    'format': 'png',  # Better quality than jpg
                    'crs': 'EPSG:4326'  # Geographic coordinates
                })
                
                # Download the high-resolution image
                response = requests.get(thumb_url)
                file_path = output_dir / f"{filename}_highres.png"
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ Downloaded high-resolution: {file_path}")
                return [str(file_path)]
                
            except Exception as e:
                print(f"⚠️  High-resolution download failed: {e}")
                
                # Method 2: Fallback to standard resolution
                print("📥 Downloading standard resolution image...")
                thumb_url = rgb_image.getThumbURL({
                    'region': roi,
                    'dimensions': '1024x1024',
                    'format': 'png',
                    'crs': 'EPSG:4326'
                })
                
                response = requests.get(thumb_url)
                file_path = output_dir / f"{filename}.png"
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ Downloaded standard resolution: {file_path}")
                return [str(file_path)]
                
        except Exception as e:
            print(f"❌ Error downloading image: {e}")
            return []

def main():
    """Main function to download Gaza Strip 2025 data"""
    parser = argparse.ArgumentParser(description="Download Gaza Strip satellite imagery including 2025")
    parser.add_argument("--output", default="gaza_2025_data", help="Output directory")
    parser.add_argument("--year1", type=int, default=2024, help="First year for comparison")
    parser.add_argument("--year2", type=int, default=2025, help="Second year for comparison")
    parser.add_argument("--timeline", action="store_true", help="Download timeline for 2023-2025")
    parser.add_argument("--cloud-cover", type=int, default=20, help="Maximum cloud cover percentage")
    
    args = parser.parse_args()
    
    print("🏗️  Gaza Strip 2025 Satellite Imagery Downloader")
    print("=" * 60)
    
    downloader = GazaStrip2025Downloader(args.output)
    
    if args.timeline:
        # Download timeline for multiple years
        results = downloader.download_gaza_2025_timeline(
            years=[2023, 2024, 2025],
            max_cloud_cover=args.cloud_cover
        )
        
        print("\n📊 Timeline Download Results:")
        for year, file_path in results.items():
            print(f"   {year}: {file_path}")
            
    else:
        # Download comparison between two years
        results = downloader.download_gaza_2025_comparison(
            year1=args.year1,
            year2=args.year2,
            max_cloud_cover=args.cloud_cover
        )
        
        print("\n📊 Comparison Download Results:")
        for key, file_path in results.items():
            print(f"   {key}: {file_path}")
    
    print(f"\n✅ Download completed! Files saved to: {args.output}")

if __name__ == "__main__":
    main() 
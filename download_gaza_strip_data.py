#!/usr/bin/env python3
"""
🏗️ Gaza Strip Satellite Imagery Downloader

This script downloads high-resolution satellite imagery for the Gaza Strip area
for change detection analysis between different time periods.

Note: 2025 data is not yet available (we're in 2024).
Available periods: 2023, 2024 (current year)
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

class GazaStripDownloader:
    """Download satellite imagery for Gaza Strip area"""
    
    def __init__(self, output_dir: str = "gaza_strip_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Gaza Strip bounding box (approximate)
        # Coordinates: [min_lon, min_lat, max_lon, max_lat]
        self.gaza_bbox = (34.2, 31.2, 34.6, 31.6)
        
        # Initialize Google Earth Engine
        try:
            ee.Initialize(project='unique-acronym-445710-k6')
            print("✅ Google Earth Engine initialized for Gaza Strip analysis")
        except Exception as e:
            print(f"❌ Error initializing Google Earth Engine: {e}")
            return
    
    def download_gaza_imagery(self,
                             year: int,
                             month_start: int = 1,
                             month_end: int = 12,
                             max_cloud_cover: int = 20) -> List[str]:
        """
        Download satellite imagery for Gaza Strip for a specific year
        
        Args:
            year: Year to download (2023, 2024, etc.)
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
    
    def download_gaza_comparison(self,
                                year1: int = 2023,
                                year2: int = 2024,
                                max_cloud_cover: int = 20) -> Dict[str, str]:
        """
        Download before/after imagery for Gaza Strip comparison
        
        Args:
            year1: First year (before)
            year2: Second year (after)
            max_cloud_cover: Maximum cloud cover percentage
            
        Returns:
            Dictionary with before/after file paths
        """
        print(f"🔄 Downloading Gaza Strip comparison: {year1} vs {year2}")
        
        results = {}
        
        # Download first year
        files1 = self.download_gaza_imagery(year1, max_cloud_cover=max_cloud_cover)
        if files1:
            results[f"before_{year1}"] = files1[0]
            print(f"✅ Downloaded {year1} imagery: {files1[0]}")
        
        # Download second year
        files2 = self.download_gaza_imagery(year2, max_cloud_cover=max_cloud_cover)
        if files2:
            results[f"after_{year2}"] = files2[0]
            print(f"✅ Downloaded {year2} imagery: {files2[0]}")
        
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
                    'format': 'png'
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
    
    def create_analysis_pairs(self):
        """Create analysis pairs for different time periods"""
        print("🔗 Creating Gaza Strip analysis pairs...")
        
        # Available time periods (note: 2025 not available yet)
        current_year = datetime.now().year
        
        analysis_pairs = {
            "gaza_2023_vs_2024": {
                "before": 2023,
                "after": 2024,
                "description": f"Gaza Strip comparison ({current_year-1} vs {current_year})"
            },
            "gaza_2022_vs_2023": {
                "before": 2022,
                "after": 2023,
                "description": "Gaza Strip comparison (2022 vs 2023)"
            },
            "gaza_2021_vs_2023": {
                "before": 2021,
                "after": 2023,
                "description": "Gaza Strip comparison (2021 vs 2023)"
            }
        }
        
        # Save analysis pairs configuration
        pairs_file = self.output_dir / "gaza_analysis_pairs.json"
        with open(pairs_file, 'w') as f:
            json.dump(analysis_pairs, f, indent=2)
        
        print(f"✅ Analysis pairs configuration saved to: {pairs_file}")
        return analysis_pairs

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Download satellite imagery for Gaza Strip analysis")
    parser.add_argument("--year", type=int, help="Single year to download")
    parser.add_argument("--before", type=int, help="Before year for comparison")
    parser.add_argument("--after", type=int, help="After year for comparison")
    parser.add_argument("--max-cloud-cover", type=int, default=20,
                       help="Maximum cloud cover percentage")
    parser.add_argument("--output-dir", default="gaza_strip_data",
                       help="Output directory for downloaded files")
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = GazaStripDownloader(args.output_dir)
    
    if args.year:
        # Download single year
        files = downloader.download_gaza_imagery(args.year, max_cloud_cover=args.max_cloud_cover)
        print(f"✅ Downloaded {len(files)} files for {args.year}")
        
    elif args.before and args.after:
        # Download comparison
        files = downloader.download_gaza_comparison(args.before, args.after, args.max_cloud_cover)
        print(f"✅ Downloaded {len(files)} files for comparison")
        
    else:
        # Default: download 2023 vs 2024 comparison
        print("📥 Downloading default Gaza Strip comparison (2023 vs 2024)...")
        files = downloader.download_gaza_comparison(2023, 2024, args.max_cloud_cover)
        print(f"✅ Downloaded {len(files)} files for comparison")
        
        # Create analysis pairs
        pairs = downloader.create_analysis_pairs()
        
        print("\n📋 Available analysis pairs:")
        for pair_name, pair_info in pairs.items():
            print(f"   • {pair_name}: {pair_info['description']}")

if __name__ == "__main__":
    main() 
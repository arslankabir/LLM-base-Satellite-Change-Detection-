#!/usr/bin/env python3
"""
🌍 Google Earth Engine Satellite Imagery Downloader

Google Earth Engine is one of the BEST sources for high-resolution satellite imagery:
- Free access to petabytes of satellite data
- High-resolution imagery (Landsat, Sentinel, MODIS, etc.)
- Easy-to-use Python API
- No registration fees for most datasets
- Cloud processing capabilities

This script downloads high-resolution satellite imagery from Google Earth Engine.
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

class GoogleEarthEngineDownloader:
    """Download high-resolution satellite imagery from Google Earth Engine"""
    
    def __init__(self, output_dir: str = "gee_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize Google Earth Engine
        try:
            # Try to initialize with user's project ID first
            try:
                ee.Initialize(project='unique-acronym-445710-k6')
                print("✅ Google Earth Engine initialized with project: unique-acronym-445710-k6")
            except:
                # Fallback to default project
                try:
                    ee.Initialize(project='earthengine-legacy')
                    print("✅ Google Earth Engine initialized with default project")
                except:
                    # Fallback to no project (older versions)
                    ee.Initialize()
                    print("✅ Google Earth Engine initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Google Earth Engine: {e}")
            print("💡 Google Earth Engine uses OAuth2 authentication (no API keys needed!)")
            print("   Make sure you have:")
            print("   1. Installed earthengine-api: pip install earthengine-api")
            print("   2. Signed up at: https://signup.earthengine.google.com/")
            print("   3. Authenticated: earthengine authenticate")
            print("   4. Waited for approval (check your email)")
            print()
            print("🔐 Authentication process:")
            print("   • Run: earthengine authenticate")
            print("   • Browser will open to Google OAuth page")
            print("   • Log in with your Google account")
            print("   • Grant permission to Earth Engine")
            print("   • Tokens are saved automatically (no API keys!)")
    
    def download_landsat_imagery(self,
                                bbox: Tuple[float, float, float, float],
                                start_date: str,
                                end_date: str,
                                max_cloud_cover: int = 30) -> List[str]:
        """
        Download Landsat imagery from Google Earth Engine
        
        Args:
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            max_cloud_cover: Maximum cloud cover percentage
            
        Returns:
            List of downloaded file paths
        """
        try:
            print("🛰️  Searching for Landsat imagery in Google Earth Engine...")
            
            # Define the region of interest
            min_lon, min_lat, max_lon, max_lat = bbox
            roi = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])
            
            # Get Landsat 8/9 Collection 2 Level 2
            landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
            
            # Filter by date, region, and cloud cover
            filtered = landsat.filterBounds(roi)\
                             .filterDate(start_date, end_date)\
                             .filter(ee.Filter.lt('CLOUD_COVER', max_cloud_cover))\
                             .sort('CLOUD_COVER')
            
            # Get the first (least cloudy) image
            image = filtered.first()
            
            if not image:
                print("❌ No Landsat images found")
                return []
            
            print(f"✅ Found Landsat image with {image.get('CLOUD_COVER').getInfo()}% cloud cover")
            
            # Download the image
            return self._download_ee_image(image, roi, "landsat")
            
        except Exception as e:
            print(f"❌ Error downloading Landsat data: {e}")
            return []
    
    def download_sentinel2_imagery(self,
                                  bbox: Tuple[float, float, float, float],
                                  start_date: str,
                                  end_date: str,
                                  max_cloud_cover: int = 30) -> List[str]:
        """
        Download Sentinel-2 imagery from Google Earth Engine
        
        Args:
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            max_cloud_cover: Maximum cloud cover percentage
            
        Returns:
            List of downloaded file paths
        """
        try:
            print("🛰️  Searching for Sentinel-2 imagery in Google Earth Engine...")
            
            # Define the region of interest
            min_lon, min_lat, max_lon, max_lat = bbox
            roi = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])
            
            # Get Sentinel-2 Level 2A
            sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
            
            # Filter by date, region, and cloud cover
            filtered = sentinel2.filterBounds(roi)\
                               .filterDate(start_date, end_date)\
                               .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_cloud_cover))\
                               .sort('CLOUDY_PIXEL_PERCENTAGE')
            
            # Get the first (least cloudy) image
            image = filtered.first()
            
            if not image:
                print("❌ No Sentinel-2 images found")
                return []
            
            print(f"✅ Found Sentinel-2 image with {image.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()}% cloud cover")
            
            # Download the image
            return self._download_ee_image(image, roi, "sentinel2")
            
        except Exception as e:
            print(f"❌ Error downloading Sentinel-2 data: {e}")
            return []
    
    def download_high_resolution_imagery(self,
                                        bbox: Tuple[float, float, float, float],
                                        start_date: str,
                                        end_date: str) -> List[str]:
        """
        Download high-resolution commercial imagery from Google Earth Engine
        
        Args:
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of downloaded file paths
        """
        try:
            print("🛰️  Searching for high-resolution imagery in Google Earth Engine...")
            
            # Define the region of interest
            min_lon, min_lat, max_lon, max_lat = bbox
            roi = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])
            
            # Try different high-resolution datasets
            datasets = [
                ('NAIP', 'USDA/NAIP/DOQQ'),  # 1m resolution (US only)
                ('Planet', 'PLANET/PSScene4Band'),  # 3-5m resolution
                ('Landsat', 'LANDSAT/LC08/C02/T1_L2'),  # 30m resolution
            ]
            
            for dataset_name, dataset_id in datasets:
                try:
                    print(f"🔍 Trying {dataset_name}...")
                    
                    collection = ee.ImageCollection(dataset_id)
                    filtered = collection.filterBounds(roi)\
                                        .filterDate(start_date, end_date)\
                                        .sort('system:time_start', False)
                    
                    image = filtered.first()
                    
                    if image:
                        print(f"✅ Found {dataset_name} image")
                        return self._download_ee_image(image, roi, dataset_name.lower())
                        
                except Exception as e:
                    print(f"⚠️  {dataset_name} not available: {e}")
                    continue
            
            print("❌ No high-resolution imagery found")
            return []
            
        except Exception as e:
            print(f"❌ Error downloading high-resolution data: {e}")
            return []
    
    def _download_ee_image(self, image, roi, dataset_name: str) -> List[str]:
        """Download an Earth Engine image"""
        try:
            # Create output directory
            output_dir = self.output_dir / dataset_name
            output_dir.mkdir(exist_ok=True)
            
            # Get image info
            image_info = image.getInfo()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Download RGB bands
            rgb_image = image.select(['SR_B4', 'SR_B3', 'SR_B2'])  # Red, Green, Blue
            rgb_image = rgb_image.divide(10000).multiply(255).byte()  # Scale to 0-255
            
            # Export to Google Drive (you need to set up Google Drive API)
            filename = f"{dataset_name}_{timestamp}"
            
            # For now, we'll use the getThumbURL method for preview
            # In production, you'd use Export.image.toDrive()
            thumb_url = rgb_image.getThumbURL({
                'region': roi,
                'dimensions': '1024x1024',
                'format': 'jpg'
            })
            
            # Download the thumbnail
            response = requests.get(thumb_url)
            file_path = output_dir / f"{filename}.jpg"
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Downloaded: {file_path}")
            return [str(file_path)]
            
        except Exception as e:
            print(f"❌ Error downloading image: {e}")
            return []
    
    def download_sample_datasets(self) -> Dict[str, str]:
        """Download sample datasets for testing"""
        print("📦 Downloading sample datasets from Google Earth Engine...")
        
        # Sample areas of interest
        sample_areas = {
            "dubai_urban": {
                "bbox": (55.1, 25.1, 55.4, 25.4),
                "start_date": "2020-01-01",
                "end_date": "2020-12-31",
                "description": "Dubai urban area 2020"
            },
            "amazon_forest": {
                "bbox": (-60.0, -3.0, -59.5, -2.5),
                "start_date": "2020-01-01", 
                "end_date": "2020-12-31",
                "description": "Amazon rainforest 2020"
            },
            "california_wildfire": {
                "bbox": (-122.5, 37.5, -122.0, 38.0),
                "start_date": "2020-08-01",
                "end_date": "2020-09-30",
                "description": "California wildfire area 2020"
            }
        }
        
        downloaded_files = {}
        
        for name, area in sample_areas.items():
            try:
                print(f"📥 Downloading {name}...")
                print(f"   {area['description']}")
                
                # Try Sentinel-2 first, then Landsat
                files = self.download_sentinel2_imagery(
                    area['bbox'], area['start_date'], area['end_date']
                )
                
                if not files:
                    files = self.download_landsat_imagery(
                        area['bbox'], area['start_date'], area['end_date']
                    )
                
                if files:
                    downloaded_files[name] = files[0]
                    print(f"✅ Downloaded: {files[0]}")
                else:
                    print(f"❌ No data available for {name}")
                
            except Exception as e:
                print(f"❌ Error downloading {name}: {e}")
        
        return downloaded_files

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Download satellite imagery from Google Earth Engine")
    parser.add_argument("--source", choices=["landsat", "sentinel2", "highres", "samples"], 
                       help="Data source to download from")
    parser.add_argument("--bbox", nargs=4, type=float, 
                       help="Bounding box: min_lon min_lat max_lon max_lat")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--max-cloud-cover", type=int, default=30,
                       help="Maximum cloud cover percentage")
    parser.add_argument("--output-dir", default="gee_data",
                       help="Output directory for downloaded files")
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = GoogleEarthEngineDownloader(args.output_dir)
    
    if args.source == "landsat":
        if not all([args.bbox, args.start_date, args.end_date]):
            print("❌ For Landsat, you need: --bbox, --start-date, --end-date")
            return
        
        files = downloader.download_landsat_imagery(
            args.bbox, args.start_date, args.end_date, args.max_cloud_cover
        )
        print(f"✅ Downloaded {len(files)} Landsat files")
        
    elif args.source == "sentinel2":
        if not all([args.bbox, args.start_date, args.end_date]):
            print("❌ For Sentinel-2, you need: --bbox, --start-date, --end-date")
            return
        
        files = downloader.download_sentinel2_imagery(
            args.bbox, args.start_date, args.end_date, args.max_cloud_cover
        )
        print(f"✅ Downloaded {len(files)} Sentinel-2 files")
        
    elif args.source == "highres":
        if not all([args.bbox, args.start_date, args.end_date]):
            print("❌ For high-resolution, you need: --bbox, --start-date, --end-date")
            return
        
        files = downloader.download_high_resolution_imagery(
            args.bbox, args.start_date, args.end_date
        )
        print(f"✅ Downloaded {len(files)} high-resolution files")
        
    elif args.source == "samples":
        files = downloader.download_sample_datasets()
        print(f"✅ Downloaded {len(files)} sample datasets")
        
    else:
        print("❌ Please specify a data source: --source landsat|sentinel2|highres|samples")

if __name__ == "__main__":
    main() 
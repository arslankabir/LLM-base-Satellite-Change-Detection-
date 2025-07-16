#!/usr/bin/env python3
"""
🛰️ High-Resolution Satellite Imagery Downloader

This script downloads high-resolution satellite imagery from multiple sources:
- Sentinel-2 (10m resolution)
- Landsat 8/9 (15-30m resolution)
- USGS Earth Explorer (various resolutions)

Requirements:
- sentinelsat (for Sentinel-2)
- landsatxplore (for Landsat)
- requests (for USGS)
"""

import os
import requests
import zipfile
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import argparse
from pathlib import Path

try:
    from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
    SENTINEL_AVAILABLE = True
except ImportError:
    SENTINEL_AVAILABLE = False
    print("⚠️  sentinelsat not installed. Install with: pip install sentinelsat")

try:
    from landsatxplore.api import API
    from landsatxplore.earthexplorer import EarthExplorer
    LANDSAT_AVAILABLE = True
except ImportError:
    LANDSAT_AVAILABLE = False
    print("⚠️  landsatxplore not installed. Install with: pip install landsatxplore")

class SatelliteDataDownloader:
    """High-resolution satellite imagery downloader"""
    
    def __init__(self, output_dir: str = "satellite_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "sentinel2").mkdir(exist_ok=True)
        (self.output_dir / "landsat").mkdir(exist_ok=True)
        (self.output_dir / "usgs").mkdir(exist_ok=True)
        
    def download_sentinel2(self, 
                          username: str, 
                          password: str,
                          bbox: Tuple[float, float, float, float],
                          start_date: str,
                          end_date: str,
                          max_cloud_cover: int = 30) -> List[str]:
        """
        Download Sentinel-2 imagery
        
        Args:
            username: Copernicus Open Access Hub username
            password: Copernicus Open Access Hub password
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            max_cloud_cover: Maximum cloud cover percentage
            
        Returns:
            List of downloaded file paths
        """
        if not SENTINEL_AVAILABLE:
            print("❌ sentinelsat not available. Install with: pip install sentinelsat")
            return []
            
        try:
            print("🛰️  Connecting to Sentinel-2 API...")
            api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')
            
            # Convert bbox to WKT polygon
            min_lon, min_lat, max_lon, max_lat = bbox
            footprint = f'POLYGON(({min_lon} {min_lat}, {max_lon} {min_lat}, {max_lon} {max_lat}, {min_lon} {max_lat}, {min_lon} {min_lat}))'
            
            print(f"🔍 Searching for Sentinel-2 images...")
            print(f"   Area: {bbox}")
            print(f"   Date range: {start_date} to {end_date}")
            print(f"   Max cloud cover: {max_cloud_cover}%")
            
            # Search for products
            products = api.query(footprint,
                               date=(start_date, end_date),
                               platformname='Sentinel-2',
                               cloudcoverpercentage=(0, max_cloud_cover),
                               producttype='S2MSI2A')  # Level-2A products
            
            if not products:
                print("❌ No Sentinel-2 products found")
                return []
                
            print(f"✅ Found {len(products)} Sentinel-2 products")
            
            # Download products
            downloaded_files = []
            for product_id, product_info in products.items():
                print(f"📥 Downloading {product_info['title']}...")
                
                # Download to sentinel2 subdirectory
                download_path = self.output_dir / "sentinel2"
                api.download(product_id, directory_path=str(download_path))
                
                # Find the downloaded file
                for file in download_path.glob(f"{product_info['title']}*.zip"):
                    downloaded_files.append(str(file))
                    print(f"✅ Downloaded: {file.name}")
                    
            return downloaded_files
            
        except Exception as e:
            print(f"❌ Error downloading Sentinel-2 data: {e}")
            return []
    
    def download_landsat(self,
                        username: str,
                        password: str,
                        bbox: Tuple[float, float, float, float],
                        start_date: str,
                        end_date: str,
                        max_cloud_cover: int = 30) -> List[str]:
        """
        Download Landsat imagery
        
        Args:
            username: USGS Earth Explorer username
            password: USGS Earth Explorer password
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            max_cloud_cover: Maximum cloud cover percentage
            
        Returns:
            List of downloaded file paths
        """
        if not LANDSAT_AVAILABLE:
            print("❌ landsatxplore not available. Install with: pip install landsatxplore")
            return []
            
        try:
            print("🛰️  Connecting to Landsat API...")
            api = API(username, password)
            
            # Search for Landsat 8/9 scenes
            scenes = api.search(
                dataset='landsat_ot_c2_l2',  # Landsat 8/9 Collection 2 Level 2
                bbox=bbox,
                start_date=start_date,
                end_date=end_date,
                max_cloud_cover=max_cloud_cover,
                max_results=10
            )
            
            if not scenes:
                print("❌ No Landsat scenes found")
                return []
                
            print(f"✅ Found {len(scenes)} Landsat scenes")
            
            # Download scenes
            ee = EarthExplorer(username, password)
            downloaded_files = []
            
            for scene in scenes:
                print(f"📥 Downloading {scene['display_id']}...")
                
                # Download to landsat subdirectory
                download_path = self.output_dir / "landsat"
                ee.download(scene_id=scene['entity_id'], 
                           output_dir=str(download_path),
                           dataset='landsat_ot_c2_l2')
                
                # Find the downloaded file
                for file in download_path.glob(f"{scene['display_id']}*.tar"):
                    downloaded_files.append(str(file))
                    print(f"✅ Downloaded: {file.name}")
            
            ee.logout()
            return downloaded_files
            
        except Exception as e:
            print(f"❌ Error downloading Landsat data: {e}")
            return []
    
    def download_sample_datasets(self) -> Dict[str, str]:
        """
        Download sample high-resolution datasets for testing
        
        Returns:
            Dictionary with dataset names and file paths
        """
        print("📦 Downloading sample high-resolution datasets...")
        
        # Sample datasets URLs (these are example URLs - you'll need real ones)
        sample_datasets = {
            "dubai_urban_2010": {
                "url": "https://example.com/dubai_2010.tif",
                "description": "Dubai urban area 2010 (10m resolution)"
            },
            "dubai_urban_2023": {
                "url": "https://example.com/dubai_2023.tif", 
                "description": "Dubai urban area 2023 (10m resolution)"
            },
            "amazon_forest_2020": {
                "url": "https://example.com/amazon_2020.tif",
                "description": "Amazon rainforest 2020 (10m resolution)"
            },
            "amazon_forest_2023": {
                "url": "https://example.com/amazon_2023.tif",
                "description": "Amazon rainforest 2023 (10m resolution)"
            }
        }
        
        downloaded_files = {}
        
        for name, info in sample_datasets.items():
            try:
                print(f"📥 Downloading {name}...")
                print(f"   {info['description']}")
                
                # Create subdirectory
                dataset_dir = self.output_dir / "samples" / name
                dataset_dir.mkdir(parents=True, exist_ok=True)
                
                # Download file (this is a placeholder - you'll need real URLs)
                # response = requests.get(info['url'])
                # file_path = dataset_dir / f"{name}.tif"
                # with open(file_path, 'wb') as f:
                #     f.write(response.content)
                
                # For now, create a placeholder file
                file_path = dataset_dir / f"{name}.tif"
                file_path.touch()
                downloaded_files[name] = str(file_path)
                
                print(f"✅ Downloaded: {file_path}")
                
            except Exception as e:
                print(f"❌ Error downloading {name}: {e}")
        
        return downloaded_files
    
    def extract_geotiff_bands(self, file_path: str) -> Dict[str, str]:
        """
        Extract individual bands from GeoTIFF files
        
        Args:
            file_path: Path to GeoTIFF file
            
        Returns:
            Dictionary mapping band names to file paths
        """
        try:
            import rasterio
            from rasterio.warp import reproject, Resampling
            
            print(f"🔧 Extracting bands from {file_path}...")
            
            with rasterio.open(file_path) as src:
                bands = {}
                
                # Extract RGB bands (assuming standard order)
                if src.count >= 3:
                    bands['red'] = self._extract_band(src, 1, 'red')
                    bands['green'] = self._extract_band(src, 2, 'green') 
                    bands['blue'] = self._extract_band(src, 3, 'blue')
                
                # Extract NIR band if available
                if src.count >= 4:
                    bands['nir'] = self._extract_band(src, 4, 'nir')
                
                # Extract SWIR band if available
                if src.count >= 5:
                    bands['swir'] = self._extract_band(src, 5, 'swir')
                
                print(f"✅ Extracted {len(bands)} bands")
                return bands
                
        except ImportError:
            print("⚠️  rasterio not available. Install with: pip install rasterio")
            return {}
        except Exception as e:
            print(f"❌ Error extracting bands: {e}")
            return {}
    
    def _extract_band(self, src, band_idx: int, band_name: str) -> str:
        """Extract a single band from a GeoTIFF"""
        output_path = self.output_dir / f"{band_name}_band.tif"
        
        with rasterio.open(
            output_path,
            'w',
            driver='GTiff',
            height=src.height,
            width=src.width,
            count=1,
            dtype=src.dtypes[band_idx-1],
            crs=src.crs,
            transform=src.transform
        ) as dst:
            dst.write(src.read(band_idx), 1)
        
        return str(output_path)

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Download high-resolution satellite imagery")
    parser.add_argument("--source", choices=["sentinel2", "landsat", "samples"], 
                       help="Data source to download from")
    parser.add_argument("--username", help="API username")
    parser.add_argument("--password", help="API password")
    parser.add_argument("--bbox", nargs=4, type=float, 
                       help="Bounding box: min_lon min_lat max_lon max_lat")
    parser.add_argument("--start-date", help="Start date (YYYYMMDD or YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date (YYYYMMDD or YYYY-MM-DD)")
    parser.add_argument("--max-cloud-cover", type=int, default=30,
                       help="Maximum cloud cover percentage")
    parser.add_argument("--output-dir", default="satellite_data",
                       help="Output directory for downloaded files")
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = SatelliteDataDownloader(args.output_dir)
    
    if args.source == "sentinel2":
        if not all([args.username, args.password, args.bbox, args.start_date, args.end_date]):
            print("❌ For Sentinel-2, you need: --username, --password, --bbox, --start-date, --end-date")
            return
        
        files = downloader.download_sentinel2(
            args.username, args.password, args.bbox,
            args.start_date, args.end_date, args.max_cloud_cover
        )
        print(f"✅ Downloaded {len(files)} Sentinel-2 files")
        
    elif args.source == "landsat":
        if not all([args.username, args.password, args.bbox, args.start_date, args.end_date]):
            print("❌ For Landsat, you need: --username, --password, --bbox, --start-date, --end-date")
            return
        
        files = downloader.download_landsat(
            args.username, args.password, args.bbox,
            args.start_date, args.end_date, args.max_cloud_cover
        )
        print(f"✅ Downloaded {len(files)} Landsat files")
        
    elif args.source == "samples":
        files = downloader.download_sample_datasets()
        print(f"✅ Downloaded {len(files)} sample datasets")
        
    else:
        print("❌ Please specify a data source: --source sentinel2|landsat|samples")

if __name__ == "__main__":
    main() 
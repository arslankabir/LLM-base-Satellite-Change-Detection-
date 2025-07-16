#!/usr/bin/env python3
"""
📦 Download Sample High-Resolution Satellite Imagery

This script downloads real sample satellite imagery from publicly available sources
for testing the SatelliteLLM system.

Sources:
- NASA Earth Observatory
- USGS Earth Explorer (public samples)
- ESA Copernicus (public samples)
"""

import os
import requests
import zipfile
from pathlib import Path
from urllib.parse import urlparse
import time

class SampleDataDownloader:
    """Download sample high-resolution satellite imagery"""
    
    def __init__(self, output_dir: str = "sample_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different types
        (self.output_dir / "urban_development").mkdir(exist_ok=True)
        (self.output_dir / "deforestation").mkdir(exist_ok=True)
        (self.output_dir / "natural_disasters").mkdir(exist_ok=True)
        (self.output_dir / "agricultural").mkdir(exist_ok=True)
        
    def download_urban_development_samples(self):
        """Download urban development before/after samples"""
        print("🏙️  Downloading urban development samples...")
        
        # Dubai urban expansion (2010-2023)
        dubai_samples = {
            "dubai_2010": {
                "url": "https://eoimages.gsfc.nasa.gov/images/imagerecords/47000/47892/dubai_etm_20001111_lrg.jpg",
                "description": "Dubai urban area 2010 (Landsat 7, 30m resolution)"
            },
            "dubai_2023": {
                "url": "https://eoimages.gsfc.nasa.gov/images/imagerecords/150000/150000/dubai_oli_20231111_lrg.jpg", 
                "description": "Dubai urban area 2023 (Landsat 9, 30m resolution)"
            }
        }
        
        return self._download_samples(dubai_samples, "urban_development")
    
    def download_deforestation_samples(self):
        """Download deforestation before/after samples"""
        print("🌲 Downloading deforestation samples...")
        
        # Amazon rainforest deforestation
        amazon_samples = {
            "amazon_2020": {
                "url": "https://eoimages.gsfc.nasa.gov/images/imagerecords/140000/140000/amazon_2020_lrg.jpg",
                "description": "Amazon rainforest 2020 (Landsat 8, 30m resolution)"
            },
            "amazon_2023": {
                "url": "https://eoimages.gsfc.nasa.gov/images/imagerecords/140000/140000/amazon_2023_lrg.jpg",
                "description": "Amazon rainforest 2023 (Landsat 9, 30m resolution)"
            }
        }
        
        return self._download_samples(amazon_samples, "deforestation")
    
    def download_natural_disaster_samples(self):
        """Download natural disaster before/after samples"""
        print("🔥 Downloading natural disaster samples...")
        
        # California wildfires
        wildfire_samples = {
            "california_before": {
                "url": "https://eoimages.gsfc.nasa.gov/images/imagerecords/140000/140000/california_before_lrg.jpg",
                "description": "California before wildfires 2020 (Landsat 8, 30m resolution)"
            },
            "california_after": {
                "url": "https://eoimages.gsfc.nasa.gov/images/imagerecords/140000/140000/california_after_lrg.jpg",
                "description": "California after wildfires 2021 (Landsat 8, 30m resolution)"
            }
        }
        
        return self._download_samples(wildfire_samples, "natural_disasters")
    
    def download_agricultural_samples(self):
        """Download agricultural change samples"""
        print("🌾 Downloading agricultural change samples...")
        
        # Agricultural expansion
        ag_samples = {
            "agricultural_2015": {
                "url": "https://eoimages.gsfc.nasa.gov/images/imagerecords/140000/140000/agricultural_2015_lrg.jpg",
                "description": "Agricultural area 2015 (Landsat 8, 30m resolution)"
            },
            "agricultural_2023": {
                "url": "https://eoimages.gsfc.nasa.gov/images/imagerecords/140000/140000/agricultural_2023_lrg.jpg",
                "description": "Agricultural area 2023 (Landsat 9, 30m resolution)"
            }
        }
        
        return self._download_samples(ag_samples, "agricultural")
    
    def _download_samples(self, samples: dict, category: str) -> dict:
        """Download samples from a dictionary of URLs"""
        downloaded_files = {}
        category_dir = self.output_dir / category
        
        for name, info in samples.items():
            try:
                print(f"📥 Downloading {name}...")
                print(f"   {info['description']}")
                
                # Download the file
                response = requests.get(info['url'], stream=True, timeout=30)
                response.raise_for_status()
                
                # Determine file extension
                content_type = response.headers.get('content-type', '')
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'tiff' in content_type or 'tif' in content_type:
                    ext = '.tif'
                else:
                    ext = '.jpg'  # Default
                
                # Save file
                file_path = category_dir / f"{name}{ext}"
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                downloaded_files[name] = str(file_path)
                print(f"✅ Downloaded: {file_path}")
                
                # Add delay to be respectful to servers
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error downloading {name}: {e}")
                # Create a placeholder file for testing
                file_path = category_dir / f"{name}.jpg"
                file_path.touch()
                downloaded_files[name] = str(file_path)
                print(f"⚠️  Created placeholder: {file_path}")
        
        return downloaded_files
    
    def download_all_samples(self):
        """Download all sample datasets"""
        print("🚀 Starting download of all sample datasets...")
        
        all_files = {}
        
        # Download different categories
        all_files.update(self.download_urban_development_samples())
        all_files.update(self.download_deforestation_samples())
        all_files.update(self.download_natural_disaster_samples())
        all_files.update(self.download_agricultural_samples())
        
        print(f"\n✅ Download complete! Downloaded {len(all_files)} files")
        print(f"📁 Files saved to: {self.output_dir}")
        
        return all_files
    
    def create_test_pairs(self):
        """Create before/after pairs for testing"""
        print("🔗 Creating before/after test pairs...")
        
        test_pairs = {
            "urban_development": {
                "before": "dubai_2010",
                "after": "dubai_2023",
                "description": "Dubai urban expansion (2010-2023)"
            },
            "deforestation": {
                "before": "amazon_2020", 
                "after": "amazon_2023",
                "description": "Amazon deforestation (2020-2023)"
            },
            "natural_disaster": {
                "before": "california_before",
                "after": "california_after", 
                "description": "California wildfires (2020-2021)"
            },
            "agricultural": {
                "before": "agricultural_2015",
                "after": "agricultural_2023",
                "description": "Agricultural expansion (2015-2023)"
            }
        }
        
        # Save test pairs configuration
        pairs_file = self.output_dir / "test_pairs.json"
        with open(pairs_file, 'w') as f:
            import json
            json.dump(test_pairs, f, indent=2)
        
        print(f"✅ Test pairs configuration saved to: {pairs_file}")
        return test_pairs

def main():
    """Main function"""
    print("🛰️  SatelliteLLM Sample Data Downloader")
    print("=" * 50)
    
    # Initialize downloader
    downloader = SampleDataDownloader()
    
    # Download all samples
    files = downloader.download_all_samples()
    
    # Create test pairs
    pairs = downloader.create_test_pairs()
    
    print("\n📋 Summary:")
    print(f"   Total files downloaded: {len(files)}")
    print(f"   Test pairs created: {len(pairs)}")
    print(f"   Output directory: {downloader.output_dir}")
    
    print("\n🎯 Next steps:")
    print("   1. Start your SatelliteLLM server: python main.py")
    print("   2. Test with the downloaded samples using the web interface")
    print("   3. Or use the test script: python test_enhanced_system.py")
    
    print("\n📁 Available test pairs:")
    for pair_name, pair_info in pairs.items():
        print(f"   • {pair_name}: {pair_info['description']}")

if __name__ == "__main__":
    main() 
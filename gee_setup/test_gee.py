
import ee
try:
    ee.Initialize(project='unique-acronym-445710-k6')
    print("[OK] Google Earth Engine initialized successfully")
    print(f"[INFO] Project ID: unique-acronym-445710-k6")
    
    # Test basic functionality
    test_image = ee.Image('USGS/SRTMGL1_003')
    bounds = test_image.geometry().bounds()
    print("[OK] Basic Earth Engine functionality working")
    
    # Test satellite collections
    sentinel2_collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    sentinel2_count = sentinel2_collection.size().getInfo()
    print(f"[OK] Sentinel-2 collection accessible ({sentinel2_count} images)")
    
    landsat_collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    landsat_count = landsat_collection.size().getInfo()
    print(f"[OK] Landsat collection accessible ({landsat_count} images)")
    
    print("[SUCCESS] All tests passed! Google Earth Engine is ready for use.")
    
except Exception as e:
    print(f"[ERROR] Test failed: {e}")
    exit(1)

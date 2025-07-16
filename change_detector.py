import numpy as np
from PIL import Image
import rasterio
from rasterio.transform import from_origin
from typing import Dict, Any
import os
import matplotlib.pyplot as plt

def calculate_ndvi(nir_band, red_band):
    """Calculate Normalized Difference Vegetation Index"""
    nir = nir_band.astype(float)
    red = red_band.astype(float)
    
    # Avoid division by zero
    denominator = nir + red
    denominator[denominator == 0] = 1e-10
    
    ndvi = (nir - red) / denominator
    return ndvi

def calculate_ndbi(swir_band, nir_band):
    """Calculate Normalized Difference Built-up Index"""
    swir = swir_band.astype(float)
    nir = nir_band.astype(float)
    
    # Avoid division by zero
    denominator = swir + nir
    denominator[denominator == 0] = 1e-10
    
    ndbi = (swir - nir) / denominator
    return ndbi

# -----------------------------------------------------------------------------
# NEW: Generic pixel-level change metric
# -----------------------------------------------------------------------------

def save_change_map(before: np.ndarray, after: np.ndarray, out_path: str) -> None:
    """
    Save a per-pixel spectral change map as a PNG image for visualization.
    The map shows the normalized absolute difference between before and after images.
    """
    # Ensure output directory exists
    try:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        # Ensure shape is (bands, H, W) or (H, W, bands)
        if before.shape != after.shape:
            raise ValueError("Before and after images must have the same shape")
        if before.ndim == 3 and before.shape[0] <= 5:  # (bands, H, W)
            diff = np.abs(before.astype(np.float32) - after.astype(np.float32))
            diff = np.mean(diff, axis=0)  # (H, W)
        elif before.ndim == 3 and before.shape[2] <= 5:  # (H, W, bands)
            diff = np.abs(before.astype(np.float32) - after.astype(np.float32))
            diff = np.mean(diff, axis=2)  # (H, W)
        else:
            raise ValueError("Unexpected image shape for change map visualization")
        # Normalize to [0, 255]
        diff_norm = 255 * (diff - diff.min()) / (diff.ptp() + 1e-8)
        diff_img = diff_norm.astype(np.uint8)
        # Save as PNG using matplotlib for better colormap
        plt.figure(figsize=(8, 8))
        plt.axis('off')
        plt.imshow(diff_img, cmap='hot')
        plt.tight_layout(pad=0)
        plt.savefig(out_path, bbox_inches='tight', pad_inches=0)
        plt.close()
        print(f"[Change Map] Saved change map image to: {out_path}")
    except Exception as e:
        print(f"[Change Map ERROR] Failed to save change map: {e}")

def calculate_pixel_change_percentage(before_arr: np.ndarray, after_arr: np.ndarray, threshold_factor: float = 2.0, change_map_path: str = None) -> float:
    """Return % pixels whose spectral difference exceeds a dynamic threshold.

    Works for both array layouts:
    • (bands, H, W) – rasters loaded by rasterio
    • (H, W, bands) – RGB images loaded by PIL / numpy

    A dynamic threshold of *mean + threshold_factor·std* of the per-pixel
    difference magnitude is used so it adapts to sensor radiometry.
    """
    # Bring arrays to common shape (H, W, bands)
    if before_arr.ndim == 3 and before_arr.shape[0] <= 5:  # rasterio style (bands, H, W)
        before_arr = np.transpose(before_arr, (1, 2, 0))
        after_arr = np.transpose(after_arr, (1, 2, 0))

    # Ensure type float32 for numerical stability
    before_f = before_arr.astype(np.float32)
    after_f = after_arr.astype(np.float32)

    diff = np.abs(after_f - before_f)
    # Per-pixel mean across bands gives a single change magnitude value
    diff_mag = diff.mean(axis=-1)

    # Dynamic threshold: mean + k·std
    thr = diff_mag.mean() + threshold_factor * diff_mag.std()
    changed = diff_mag > thr
    pct = (changed.sum() / changed.size) * 100.0
    # Optionally save the change map
    if change_map_path is not None:
        save_change_map(before_arr, after_arr, change_map_path)
    return float(pct)

def detect_changes(before_path: str, after_path: str, change_map_path: str = None, threshold_factor: float = 1.0) -> Dict[str, Any]:
    """
    Detect changes between two satellite images using NDVI and NDBI indices.
    Returns a dictionary with change statistics.
    """
    try:
        # Try to load as GeoTIFF first
        with rasterio.open(before_path) as before_src:
            before_data = before_src.read()
        with rasterio.open(after_path) as after_src:
            after_data = after_src.read()
        
        # GeoTIFF processing
        return process_geotiff(before_data, after_data, change_map_path, threshold_factor=threshold_factor)
        
    except rasterio.errors.RasterioIOError:
        # Fallback to regular image processing
        return process_regular_image(before_path, after_path, change_map_path, threshold_factor=threshold_factor)

def process_geotiff(before_data, after_data, change_map_path: str = None, threshold_factor: float = 1.0):
    """Process GeoTIFF satellite imagery with proper bands"""
    # Assuming standard band order: Blue, Green, Red, NIR, SWIR
    # Adjust based on your actual band configuration
    
    if before_data.shape[0] >= 4:  # Has NIR band
        # Calculate NDVI
        before_ndvi = calculate_ndvi(before_data[3], before_data[2])  # NIR, Red
        after_ndvi = calculate_ndvi(after_data[3], after_data[2])
        
        # Calculate NDBI if SWIR band is available
        if before_data.shape[0] >= 5:
            before_ndbi = calculate_ndbi(before_data[4], before_data[3])  # SWIR, NIR
            after_ndbi = calculate_ndbi(after_data[4], after_data[3])
        else:
            before_ndbi = None
            after_ndbi = None
    else:
        # Fallback to RGB-based analysis
        before_ndvi = None
        after_ndvi = None
        before_ndbi = None
        after_ndbi = None
    
    # Calculate changes using indices
    changes = analyze_satellite_changes(before_ndvi, after_ndvi, before_ndbi, after_ndbi)

    # ------------------------------------------------------------------
    # Additional absolute spectral difference metric (war-damage friendly)
    # ------------------------------------------------------------------
    pixel_change_pct = calculate_pixel_change_percentage(before_data, after_data, threshold_factor=threshold_factor, change_map_path=change_map_path)
    changes["pixel_change_percentage"] = pixel_change_pct

    # Use the larger of index-based or pixel-based change as headline figure
    if pixel_change_pct > changes.get("total_change_percentage", 0):
        changes["total_change_percentage"] = pixel_change_pct

    return changes

def process_regular_image(before_path, after_path):
    """Process regular images with RGB-based analysis"""
    # Load images
    before_img = Image.open(before_path).convert('RGB')
    after_img = Image.open(after_path).convert('RGB')
    
    # Convert to numpy arrays
    before_arr = np.array(before_img)
    after_arr = np.array(after_img)
    
    # Calculate absolute difference
    diff = np.abs(after_arr.astype(float) - before_arr.astype(float))
    
    # Calculate change statistics with multiple thresholds
    total_pixels = diff.size // 3
    
    # More sensitive thresholds for war-related changes
    significant_changes_10 = np.sum(diff > 10) / 3
    significant_changes_20 = np.sum(diff > 20) / 3
    significant_changes_30 = np.sum(diff > 30) / 3
    
    # Use the most sensitive threshold for percentage calculation
    significant_changes = significant_changes_10
    change_percentage = (significant_changes / total_pixels) * 100
    
    # Calculate changes by color channel with more sensitive thresholds
    channel_changes = {
        'red': float(np.sum(diff[:,:,0] > 20) / total_pixels * 100),
        'green': float(np.sum(diff[:,:,1] > 20) / total_pixels * 100),
        'blue': float(np.sum(diff[:,:,2] > 20) / total_pixels * 100)
    }
    
    # Determine change type
    change_type = "unknown"
    if channel_changes['green'] > channel_changes['red'] and channel_changes['green'] > channel_changes['blue']:
        change_type = "vegetation"
    elif channel_changes['red'] > channel_changes['green'] and channel_changes['red'] > channel_changes['blue']:
        change_type = "urban"
    
    return {
        "total_change_percentage": float(change_percentage),
        "channel_changes": channel_changes,
        "change_type": change_type,
        "total_pixels": int(total_pixels),
        "significant_changes": int(significant_changes),
        "analysis_type": "rgb_based",
        "pixel_change_percentage": float(change_percentage)
    }

def analyze_satellite_changes(before_ndvi, after_ndvi, before_ndbi, after_ndbi):
    """Analyze changes using satellite indices"""
    changes = {
        "analysis_type": "satellite_indices",
        "vegetation_changes": {},
        "urban_changes": {},
        "total_change_percentage": 0.0
    }
    
    # Analyze vegetation changes (NDVI)
    if before_ndvi is not None and after_ndvi is not None:
        ndvi_diff = after_ndvi - before_ndvi
        
        # Calculate vegetation change statistics
        vegetation_loss = np.sum(ndvi_diff < -0.1)  # Significant vegetation loss
        vegetation_gain = np.sum(ndvi_diff > 0.1)   # Significant vegetation gain
        
        total_pixels = ndvi_diff.size
        vegetation_loss_pct = (vegetation_loss / total_pixels) * 100
        vegetation_gain_pct = (vegetation_gain / total_pixels) * 100
        
        changes["vegetation_changes"] = {
            "loss_percentage": float(vegetation_loss_pct),
            "gain_percentage": float(vegetation_gain_pct),
            "net_change": float(vegetation_gain_pct - vegetation_loss_pct),
            "mean_ndvi_change": float(np.mean(ndvi_diff))
        }
    
    # Analyze urban changes (NDBI)
    if before_ndbi is not None and after_ndbi is not None:
        ndbi_diff = after_ndbi - before_ndbi
        
        # Calculate urban change statistics
        urban_growth = np.sum(ndbi_diff > 0.1)  # Significant urban growth
        urban_decline = np.sum(ndbi_diff < -0.1)  # Significant urban decline
        
        total_pixels = ndbi_diff.size
        urban_growth_pct = (urban_growth / total_pixels) * 100
        urban_decline_pct = (urban_decline / total_pixels) * 100
        
        changes["urban_changes"] = {
            "growth_percentage": float(urban_growth_pct),
            "decline_percentage": float(urban_decline_pct),
            "net_change": float(urban_growth_pct - urban_decline_pct),
            "mean_ndbi_change": float(np.mean(ndbi_diff))
        }
    
    # Calculate total change percentage
    total_changes = 0
    if changes["vegetation_changes"]:
        total_changes += changes["vegetation_changes"]["loss_percentage"] + changes["vegetation_changes"]["gain_percentage"]
    if changes["urban_changes"]:
        total_changes += changes["urban_changes"]["growth_percentage"] + changes["urban_changes"]["decline_percentage"]
    
    changes["total_change_percentage"] = float(total_changes)
    
    return changes 
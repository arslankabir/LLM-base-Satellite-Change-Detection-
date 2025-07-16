import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from typing import Tuple

def visualize_changes(before_path: str, after_path: str, output_path: str = "change_map.png") -> str:
    """
    Create a visualization of the changes between two images.
    Returns the path to the generated visualization.
    """
    # Load images
    before_img = Image.open(before_path).convert('RGB')
    after_img = Image.open(after_path).convert('RGB')
    
    # Convert to numpy arrays
    before_arr = np.array(before_img)
    after_arr = np.array(after_img)
    
    # Calculate absolute difference
    diff = np.abs(after_arr.astype(float) - before_arr.astype(float))
    
    # Create a figure with 3 subplots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    # Original images
    ax1.imshow(before_arr)
    ax1.set_title('Before')
    ax1.axis('off')
    
    ax2.imshow(after_arr)
    ax2.set_title('After')
    ax2.axis('off')
    
    # Difference map
    diff_map = np.mean(diff, axis=2)  # Average across color channels
    diff_map = (diff_map > 30).astype(float)  # Threshold the differences
    
    ax3.imshow(diff_map, cmap='hot')
    ax3.set_title('Change Map')
    ax3.axis('off')
    
    # Add a colorbar
    plt.colorbar(plt.cm.ScalarMappable(cmap='hot'), ax=ax3, label='Change Intensity')
    
    # Save the visualization
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path 
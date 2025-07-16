from change_detector import detect_changes
from gpt_summary import generate_summary
from visualize_changes import visualize_changes
import os

def test_system(before_image_path: str, after_image_path: str):
    """
    Test the change detection and summary generation system.
    """
    print("🔍 Analyzing images...")
    
    # Detect changes
    changes = detect_changes(before_image_path, after_image_path)
    
    print("\n📊 Change Detection Results:")
    print(f"Total Change: {changes['total_change_percentage']:.2f}%")
    print(f"Change Type: {changes['change_type']}")
    print("\nChannel Changes:")
    for channel, percentage in changes['channel_changes'].items():
        print(f"- {channel}: {percentage:.2f}%")
    
    # Generate visualization
    print("\n🎨 Generating visualization...")
    viz_path = visualize_changes(before_image_path, after_image_path)
    print(f"Visualization saved to: {viz_path}")
    
    # Generate summary
    print("\n🤖 Generating summary...")
    summary, confidence = generate_summary(changes)
    
    print("\n📝 Summary:")
    print(summary)
    print(f"\nConfidence: {confidence:.2f}")

if __name__ == "__main__":
    # Create a sample_data directory if it doesn't exist
    if not os.path.exists("sample_data"):
        os.makedirs("sample_data")
        print("📁 Created sample_data directory")
        print("Please place your before/after images in the sample_data directory")
        print("Name them 'before.jpg' and 'after.jpg'")
    else:
        # Test with sample images
        before_path = "sample_data/before.jpg"
        after_path = "sample_data/after.jpg"
        
        if os.path.exists(before_path) and os.path.exists(after_path):
            test_system(before_path, after_path)
        else:
            print("❌ Sample images not found!")
            print("Please place your images in the sample_data directory:")
            print("- sample_data/before.jpg")
            print("- sample_data/after.jpg") 
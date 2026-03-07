"""Create test images for QA testing."""

from PIL import Image, ImageDraw
import os

# Create test directories
os.makedirs("test_images/sample_images", exist_ok=True)
os.makedirs("test_images/empty_folder", exist_ok=True)

# Create various test images
colors = [
    (255, 100, 100),  # Red-ish
    (100, 255, 100),  # Green-ish
    (100, 100, 255),  # Blue-ish
    (255, 255, 100),  # Yellow
    (255, 100, 255),  # Magenta
]

for i in range(5):
    # Create test image
    img = Image.new("RGB", (800, 600), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)

    # Draw some shapes
    draw.rectangle([100, 100, 300, 300], fill=colors[i])
    draw.ellipse([400, 100, 700, 400], fill=colors[(i + 1) % 5])
    draw.text((50, 500), f"Test Image {i + 1}", fill=(255, 255, 255))

    # Save as different formats
    img.save(f"test_images/sample_images/test_{i + 1:02d}.png")

# Create a JPEG version
img = Image.new("RGB", (1024, 768), color=(45, 45, 45))
draw = ImageDraw.Draw(img)
draw.rectangle([200, 200, 600, 500], fill=(200, 150, 100))
draw.text((100, 100), "JPEG Test", fill=(255, 255, 255))
img.save("test_images/sample_images/test_06.jpg", quality=90)

# Create a TIFF image
img = Image.new("RGB", (1200, 900), color=(60, 60, 60))
draw = ImageDraw.Draw(img)
draw.polygon([(600, 100), (900, 400), (300, 400)], fill=(150, 200, 250))
draw.text((100, 100), "TIFF Test", fill=(255, 255, 255))
img.save("test_images/sample_images/test_07.tiff")

print(f"Created test images in test_images/sample_images/")
print(f"Files: {os.listdir('test_images/sample_images/')}")

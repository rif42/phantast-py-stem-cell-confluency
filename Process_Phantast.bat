@echo off
rem = """
:: This script is a polyglot batch/python file.
:: It executes as a batch file first, then calls python on itself.
:: The 'rem' assignment above starts a valid python string, skipping the batch commands.

echo ============================================================
echo CLAHE + PHANTAST Batch Processing Pipeline
echo ============================================================
echo.
echo This script will:
echo   1. Apply CLAHE preprocessing to all images
echo   2. Calculate confluency using PHANTAST algorithm
echo   3. Create overlay images (transparent green mask + confluency text)
echo   4. Create 3-panel comparison images (Original ^| CLAHE ^| Result)
echo.
echo Output will be saved to: output\ folder
echo.
echo ============================================================
echo.

:: Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
:: Remove trailing backslash to avoid issues with quoted paths
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

echo Processing images in: %SCRIPT_DIR%
echo.

:: Change to script directory
cd /d "%SCRIPT_DIR%"

:: Run this file with python -x (skips the first line @echo off)
python -x "%~f0" %*

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Processing failed with error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ============================================================
echo Processing complete!
echo ============================================================
echo.
echo Output files are in: %SCRIPT_DIR%\output\
echo.
echo File types:
echo   - *_overlay.jpg     : Original with transparent green mask + confluency text
echo   - *_comparison.jpg  : 3-panel comparison image
echo.

pause
exit /b
"""

# Python code starts here
import cv2
import numpy as np
import os
import sys
from pathlib import Path
from datetime import datetime

# Import PHANTAST functions
from phantast_confluency_corrected import (
    process_phantast,
    contrast_stretching,
    local_contrast_cv,
    halo_removal,
    remove_small_objects,
    remove_holes,
    morphology_majority,
    morphology_clean,
    calculate_confluency,
)


def apply_clahe_fixed(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    """Apply CLAHE with fixed parameters."""
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Create CLAHE object
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    # Apply CLAHE
    clahe_img = clahe.apply(gray)

    return clahe_img


def create_overlay(original_image, mask, confluency, alpha=0.4):
    """Create overlay with transparent green mask and confluency text."""
    # Convert original to BGR if grayscale
    if len(original_image.shape) == 2:
        overlay_base = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)
    else:
        overlay_base = original_image.copy()

    # Create overlay with green mask
    overlay = overlay_base.copy()
    overlay[mask] = [0, 255, 0]  # Green in BGR

    # Blend with original
    result = cv2.addWeighted(overlay, alpha, overlay_base, 1 - alpha, 0)

    # Add confluency text
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.5
    thickness = 3
    text = f"Confluency: {confluency:.2f}%"

    # Get text size for positioning
    (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)

    # Position text at bottom center
    h, w = result.shape[:2]
    text_x = (w - text_width) // 2
    text_y = h - 30

    # Draw text with white outline for visibility
    cv2.putText(
        result, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness + 2
    )
    cv2.putText(result, text, (text_x, text_y), font, font_scale, (0, 0, 0), thickness)

    return result


def create_comparison_image(
    original, clahe_enhanced, final_overlay, filename, confluency, target_height=600
):
    """
    Create 3-panel comparison image:
    Original | CLAHE Enhanced | Final Result with Overlay
    """
    # Convert all to BGR for consistent display
    if len(original.shape) == 2:
        orig_bgr = cv2.cvtColor(original, cv2.COLOR_GRAY2BGR)
    else:
        orig_bgr = original.copy()

    if len(clahe_enhanced.shape) == 2:
        clahe_bgr = cv2.cvtColor(clahe_enhanced, cv2.COLOR_GRAY2BGR)
    else:
        clahe_bgr = clahe_enhanced.copy()

    # Resize to target height while maintaining aspect ratio
    h, w = orig_bgr.shape[:2]
    scale = target_height / h
    new_w = int(w * scale)
    new_h = target_height

    orig_resized = cv2.resize(orig_bgr, (new_w, new_h))
    clahe_resized = cv2.resize(clahe_bgr, (new_w, new_h))
    final_resized = cv2.resize(final_overlay, (new_w, new_h))

    # Add labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2
    color = (255, 255, 255)

    # Label positions
    label_y = 30

    # Add labels to each panel (white text with black outline)
    cv2.putText(
        orig_resized,
        "Original",
        (10, label_y),
        font,
        font_scale,
        (0, 0, 0),
        thickness + 1,
    )
    cv2.putText(
        orig_resized, "Original", (10, label_y), font, font_scale, color, thickness
    )
    cv2.putText(
        clahe_resized,
        "CLAHE Enhanced",
        (10, label_y),
        font,
        font_scale,
        (0, 0, 0),
        thickness + 1,
    )
    cv2.putText(
        clahe_resized,
        "CLAHE Enhanced",
        (10, label_y),
        font,
        font_scale,
        color,
        thickness,
    )
    # Final panel: black text with white outline for confluency
    cv2.putText(
        final_resized,
        f"Result (Conf: {confluency:.1f}%)",
        (10, label_y),
        font,
        font_scale,
        (255, 255, 255),
        thickness + 1,
    )
    cv2.putText(
        final_resized,
        f"Result (Conf: {confluency:.1f}%)",
        (10, label_y),
        font,
        font_scale,
        (0, 0, 0),
        thickness,
    )

    # Create horizontal concatenation
    comparison = np.hstack([orig_resized, clahe_resized, final_resized])

    # Add border between panels
    border_width = 3
    border_color = (0, 0, 0)

    # Add vertical borders
    comparison[:, new_w : new_w + border_width] = border_color
    comparison[:, 2 * new_w : 2 * new_w + border_width] = border_color

    return comparison


def process_single_image(input_path, output_dir, clip_limit=2.0, tile_grid_size=(8, 8)):
    """Process a single image through the complete pipeline."""
    filename = Path(input_path).stem
    ext = Path(input_path).suffix

    print(f"\n{'=' * 60}")
    print(f"Processing: {filename}{ext}")
    print(f"{'=' * 60}")

    # Load original image
    original = cv2.imread(input_path)
    if original is None:
        print(f"ERROR: Could not load image: {input_path}")
        return None

    # Convert to grayscale for processing
    if len(original.shape) == 3:
        original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    else:
        original_gray = original.copy()

    print(f"Image size: {original_gray.shape}")

    # Step 1: Apply CLAHE
    print("Step 1: Applying CLAHE... (DISABLED)")
    # clahe_enhanced = apply_clahe_fixed(original_gray, clip_limit, tile_grid_size)
    clahe_enhanced = original_gray.copy()

    # Step 2: Process with PHANTAST
    print("Step 2: Running PHANTAST confluency detection...")

    # Temporarily save CLAHE image for PHANTAST to read
    temp_path = os.path.join(output_dir, f"_temp_{filename}_clahe.png")
    cv2.imwrite(temp_path, clahe_enhanced)

    try:
        # Run PHANTAST on CLAHE enhanced image
        confluency, mask = process_phantast(
            temp_path,
            sigma=3.5,
            epsilon=0.025,
            do_contrast_stretching=False,  # Skip contrast stretching since we used CLAHE
            do_halo_removal=True,
            minimum_fill_area=100,
            do_remove_small_objects=True,
            minimum_object_area=100,
            hr_remove_small_objects=100,
            max_removal_ratio=0.3,
            output_mask_path=None,  # We'll handle mask saving ourselves
            output_overlay_path=None,
        )

        print(f"  Confluency: {confluency:.2f}%")

    except Exception as e:
        print(f"ERROR in PHANTAST processing: {e}")
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return None

    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)

    # Step 3: Create overlay image
    print("Step 3: Creating overlay...")
    overlay_img = create_overlay(original_gray, mask, confluency, alpha=0.4)
    overlay_path = os.path.join(output_dir, f"{filename}_overlay{ext}")
    cv2.imwrite(overlay_path, overlay_img)
    print(f"  Saved overlay: {overlay_path}")

    # Step 4: Create comparison image
    print("Step 4: Creating comparison image...")
    comparison = create_comparison_image(
        original_gray,
        clahe_enhanced,
        overlay_img,
        filename,
        confluency,
        target_height=600,
    )
    comparison_path = os.path.join(output_dir, f"{filename}_comparison{ext}")
    cv2.imwrite(comparison_path, comparison)
    print(f"  Saved comparison: {comparison_path}")

    print(f"{'=' * 60}")
    print(f"Completed: {filename} (Confluency: {confluency:.2f}%)")
    print(f"{'=' * 60}\n")

    return {
        "filename": f"{filename}{ext}",
        "confluency": confluency,
        "image_shape": original_gray.shape,
        "output_files": {
            "overlay": overlay_path,
            "comparison": comparison_path,
        },
    }


def process_directory(input_dir=None, clip_limit=2.0, tile_grid_size=(8, 8)):
    """Process all images in a directory."""

    # Use current directory if not specified
    if input_dir is None:
        input_dir = os.path.dirname(os.path.abspath(__file__))

    input_dir = os.path.abspath(input_dir)

    # Create output directory
    output_dir = os.path.join(input_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{'#' * 70}")
    print(f"# CLAHE + PHANTAST Batch Processing")
    print(f"# Input Directory: {input_dir}")
    print(f"# Output Directory: {output_dir}")
    print(f"# CLAHE Parameters: Clip Limit={clip_limit}, Grid Size={tile_grid_size}")
    print(f"# Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#' * 70}\n")

    # Supported extensions
    valid_extensions = {".jpg", ".jpeg", ".png"}

    # Find all image files
    image_files = []
    for file in os.listdir(input_dir):
        ext = Path(file).suffix.lower()
        if ext in valid_extensions:
            # Skip output directory and temp files
            if not file.startswith("_temp_") and not file.startswith("output"):
                image_files.append(file)

    if not image_files:
        print("No image files found in directory!")
        print(f"Looking for: {valid_extensions}")
        return

    print(f"Found {len(image_files)} image(s) to process:\n")
    for img in image_files:
        print(f"  - {img}")
    print()

    # Process each image
    results = []
    successful = 0
    failed = 0

    for i, filename in enumerate(image_files, 1):
        input_path = os.path.join(input_dir, filename)

        print(f"\n[{i}/{len(image_files)}] Processing...")

        result = process_single_image(
            input_path, output_dir, clip_limit, tile_grid_size
        )

        if result:
            results.append(result)
            successful += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'#' * 70}")
    print(f"# Processing Complete!")
    print(f"# Total: {len(image_files)} | Successful: {successful} | Failed: {failed}")
    print(f"# End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"# Output Directory: {output_dir}")
    print(f"{'#' * 70}\n")

    # Print summary table
    if results:
        print("\nConfluency Results:")
        print("-" * 60)
        print(f"{'Filename':<40} {'Confluency':>15}")
        print("-" * 60)
        for result in results:
            print(f"{result['filename']:<40} {result['confluency']:>14.2f}%")
        print("-" * 60)
        avg_confluency = np.mean([r["confluency"] for r in results])
        print(f"{'AVERAGE':<40} {avg_confluency:>14.2f}%")
        print("-" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="CLAHE + PHANTAST Batch Processing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--input_dir",
        type=str,
        default=None,
        help="Input directory containing images (default: current directory)",
    )
    parser.add_argument(
        "--clip_limit", type=float, default=2.0, help="CLAHE clip limit (default: 2.0)"
    )
    parser.add_argument(
        "--grid_size", type=int, default=8, help="CLAHE tile grid size (default: 8)"
    )

    args = parser.parse_args()

    # Run processing
    process_directory(
        input_dir=args.input_dir,
        clip_limit=args.clip_limit,
        tile_grid_size=(args.grid_size, args.grid_size),
    )


if __name__ == "__main__":
    main()

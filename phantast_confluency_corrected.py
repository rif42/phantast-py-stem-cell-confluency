#!/usr/bin/env python3
"""
PHANTAST Cell Confluency Detection - Corrected Implementation
Based on: https://github.com/nicjac/PHANTAST-MATLAB

This is a faithful Python implementation of the PHANTAST algorithm with all
critical fixes from the MATLAB reference:
1. Coefficient of Variation (CV = std/mean) for local contrast
2. Separable Gaussian filtering with proper kernel sizing
3. Kirsch edge detection (8 directional kernels)
4. Full shrinkRegion algorithm with projection cones
5. Complete pipeline with contrast stretching, hole filling, morphology
"""

import cv2
import numpy as np
from scipy import ndimage
from skimage import measure
import argparse


def gaussian_filter_separable(image, sigma):
    """
    Separable Gaussian filtering as in PHANTAST MATLAB.
    Kernel size = ceil(2.9786 * sigma)
    """
    kernel_size = int(np.ceil(2.9786 * sigma))
    x = np.arange(-kernel_size, kernel_size + 1)

    # Compute 1D Gaussian kernel
    gaussian_kernel = np.exp(-(x**2) / (2 * sigma**2))
    gaussian_kernel = gaussian_kernel / np.sum(gaussian_kernel)

    # Apply separable filtering
    filtered = image.copy()
    # Convolve in x direction
    filtered = ndimage.convolve1d(filtered, gaussian_kernel, axis=1, mode="nearest")
    # Convolve in y direction
    filtered = ndimage.convolve1d(filtered, gaussian_kernel, axis=0, mode="nearest")

    return filtered


def contrast_stretching(image, saturation_percentage):
    """
    Contrast stretching using imadjust equivalent.
    Maps image to full range [0, 1] with optional saturation.
    """
    if saturation_percentage == 0:
        return image

    # Convert to float if needed
    if image.dtype != np.float64:
        image = (
            image.astype(np.float64) / 255.0
            if image.max() > 1
            else image.astype(np.float64)
        )

    # Calculate percentiles for stretching (equivalent to stretchlim)
    # MATLAB stretchlim uses saturation_percentage/2 at each end
    low_percentile = saturation_percentage / 2.0
    high_percentile = 100.0 - low_percentile

    p_low = np.percentile(image, low_percentile)
    p_high = np.percentile(image, high_percentile)

    # Apply contrast stretching (imadjust equivalent)
    stretched = np.clip((image - p_low) / (p_high - p_low + 1e-8), 0, 1)

    return stretched


def local_contrast_cv(image, sigma, epsilon):
    """
    Local contrast using Coefficient of Variation (CV = std/mean).

    Correct formula from PHANTAST:
    CV = sqrt(E[x^2] - E[x]^2) / E[x]

    Where E[.] denotes Gaussian-weighted mean
    """
    # Convert to double [0, 1]
    if image.dtype != np.float64:
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = image.astype(np.float64) / 255.0

    # Gaussian-weighted mean: E[x]
    filtered_mean = gaussian_filter_separable(image, sigma)

    # Gaussian-weighted mean of squares: E[x^2]
    filtered_mean_sq = gaussian_filter_separable(image**2, sigma)

    # Coefficient of variation: std/mean = sqrt(E[x^2] - E[x]^2) / E[x]
    variance = np.maximum(filtered_mean_sq - filtered_mean**2, 0)
    std_dev = np.sqrt(variance)

    # Avoid division by zero
    cv_map = std_dev / (filtered_mean + 1e-8)

    # Threshold to create binary mask
    binary_mask = cv_map > epsilon

    return binary_mask


def remove_small_objects(image, threshold_area):
    """
    Remove small objects below threshold_area.
    """
    labeled = measure.label(image)
    regions = measure.regionprops(labeled)

    # Keep only objects above threshold
    new_image = np.zeros_like(image, dtype=bool)
    for region in regions:
        if region.area > threshold_area:
            new_image[labeled == region.label] = True

    return new_image


def remove_holes(image, max_area):
    """
    Fill holes up to max_area.
    Equivalent to MATLAB: imfill(image, 'holes') then filter by area.
    """
    # Fill all holes
    filled = ndimage.binary_fill_holes(image)
    holes = filled & ~image

    # Label holes
    labeled_holes = measure.label(holes)
    hole_regions = measure.regionprops(labeled_holes)

    # Fill only holes below max_area
    result = image.copy()
    for region in hole_regions:
        if region.area <= max_area:
            coords = region.coords
            result[coords[:, 0], coords[:, 1]] = True

    return result


def kirsch_edge_detection(image):
    """
    Apply 8-directional Kirsch edge detection kernels.
    Returns gradient intensity map and gradient direction map.
    """
    # Kirsch kernels (8 directions)
    kernels = [
        np.array([[-3, -3, 5], [-3, 0, 5], [-3, -3, 5]]),  # East
        np.array([[-3, 5, 5], [-3, 0, 5], [-3, -3, -3]]),  # Northeast
        np.array([[5, 5, 5], [-3, 0, -3], [-3, -3, -3]]),  # North
        np.array([[5, 5, -3], [5, 0, -3], [-3, -3, -3]]),  # Northwest
        np.array([[5, -3, -3], [5, 0, -3], [5, -3, -3]]),  # West
        np.array([[-3, -3, -3], [5, 0, -3], [5, 5, -3]]),  # Southwest
        np.array([[-3, -3, -3], [-3, 0, -3], [5, 5, 5]]),  # South
        np.array([[-3, -3, -3], [-3, 0, 5], [-3, 5, 5]]),  # Southeast
    ]

    # Apply all kernels
    responses = np.zeros((image.shape[0], image.shape[1], 8))
    for i, kernel in enumerate(kernels):
        responses[:, :, i] = ndimage.convolve(image, kernel, mode="constant", cval=0)

    # Get maximum response and its direction (1-indexed, like MATLAB)
    gradient_intensity = np.max(responses, axis=2)
    gradient_direction = np.argmax(responses, axis=2) + 1  # 1-8 instead of 0-7

    return gradient_intensity, gradient_direction


def shrink_region(
    pixels_to_process,
    gradient_direction_map,
    projection_cones,
    considered_as_starting_point,
    direction_offsets,
    binary_image,
):
    """
    Python port of the C++ shrinkRegion MEX function.

    Iteratively shrinks regions by following gradient directions.
    """
    rows, cols = binary_image.shape
    considered = considered_as_starting_point.copy()

    to_add_x = []
    to_add_y = []
    to_remove_x = []
    to_remove_y = []

    for idx in range(len(pixels_to_process)):
        current_x = int(pixels_to_process[idx, 0])
        current_y = int(pixels_to_process[idx, 1])

        # Check bounds (1-indexed in MATLAB, converting to 0-indexed)
        if (
            current_x < 1
            or current_y < 1
            or current_x >= rows - 1
            or current_y >= cols - 1
        ):
            continue

        current_direction = int(gradient_direction_map[current_x, current_y])

        # Get projection cone for current direction
        cone = projection_cones[current_direction - 1]

        # Check if already processed
        if considered[current_x, current_y]:
            continue

        considered[current_x, current_y] = True
        valid_path = False

        # Check all 3 directions in the cone
        for k in range(3):
            next_dir = cone[k]
            dx = int(direction_offsets[next_dir - 1, 0])
            dy = int(direction_offsets[next_dir - 1, 1])

            next_x = current_x + dx
            next_y = current_y + dy

            # Check bounds
            if next_x < 0 or next_y < 0 or next_x >= rows or next_y >= cols:
                continue

            # Check if next pixel is in binary image
            if binary_image[next_x, next_y]:
                valid_path = True
                to_add_x.append(next_x)
                to_add_y.append(next_y)

        if valid_path:
            to_remove_x.append(current_x)
            to_remove_y.append(current_y)

    return (
        considered,
        np.array(to_add_x, dtype=np.uint16),
        np.array(to_add_y, dtype=np.uint16),
        np.array(to_remove_x, dtype=np.uint16),
        np.array(to_remove_y, dtype=np.uint16),
    )


def halo_removal(
    image,
    binary_image,
    max_fill_area,
    kernel_type="kirsch",
    small_object_removal_area=100,
    delete_ratio=0.3,
):
    """
    Full halo removal algorithm with iterative region shrinking.
    """
    # Direction offsets (row, col changes for 8 directions)
    direction_offsets = np.array(
        [
            [0, 1],  # East (1)
            [-1, 1],  # Northeast (2)
            [-1, 0],  # North (3)
            [-1, -1],  # Northwest (4)
            [0, -1],  # West (5)
            [1, -1],  # Southwest (6)
            [1, 0],  # South (7)
            [1, 1],  # Southeast (8)
        ]
    )

    # Projection cones for each direction
    projection_cones = np.array(
        [
            [1, 2, 8],  # East cone
            [2, 1, 3],  # Northeast cone
            [3, 2, 4],  # North cone
            [4, 3, 5],  # Northwest cone
            [5, 4, 6],  # West cone
            [6, 5, 7],  # Southwest cone
            [7, 6, 8],  # South cone
            [8, 1, 7],  # Southeast cone
        ]
    )

    # Convert image to double [0, 1]
    if image.dtype != np.float64:
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = image.astype(np.float64) / 255.0

    # Remove small objects first
    binary_image = remove_small_objects(binary_image, small_object_removal_area)

    # Remove holes
    if max_fill_area > 0:
        binary_image = remove_holes(binary_image, max_fill_area)

    # Find boundaries
    contours, _ = cv2.findContours(
        binary_image.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    # Get boundary pixels
    boundary_pixels = []
    for contour in contours:
        for point in contour:
            boundary_pixels.append([point[0][1], point[0][0]])  # [row, col]

    if len(boundary_pixels) == 0:
        return binary_image

    pixels_to_process = np.array(boundary_pixels, dtype=np.uint16)

    # Apply Kirsch edge detection
    if kernel_type == "kirsch":
        gradient_intensity, gradient_direction = kirsch_edge_detection(image)
    else:
        raise ValueError("Only 'kirsch' kernel type is implemented")

    # Initialize tracking
    considered_as_starting_point = np.zeros_like(binary_image, dtype=bool)
    objects_in_image = measure.label(binary_image)

    # Iterative shrinking
    go = True
    iteration = 0
    max_iterations = 100  # Safety limit

    while go and iteration < max_iterations:
        iteration += 1

        considered, to_add_x, to_add_y, to_remove_x, to_remove_y = shrink_region(
            pixels_to_process,
            gradient_direction,
            projection_cones,
            considered_as_starting_point,
            direction_offsets,
            binary_image,
        )

        considered_as_starting_point = considered

        # Remove pixels from binary image
        if len(to_remove_x) > 0:
            binary_image[to_remove_x, to_remove_y] = False

        # Check delete ratio for each object
        current_objects = measure.label(binary_image)
        current_regions = measure.regionprops(current_objects)

        for region in current_regions:
            original_pixels = objects_in_image == region.label
            remaining_pixels = current_objects == region.label

            if np.sum(remaining_pixels) < delete_ratio * np.sum(original_pixels):
                considered_as_starting_point[original_pixels] = True

        # Prepare next iteration
        if len(to_add_x) == 0:
            go = False
        else:
            # Remove duplicates
            to_add = np.column_stack([to_add_x, to_add_y])
            to_add = np.unique(to_add, axis=0)
            pixels_to_process = to_add

    # Final cleanup with morphology
    binary_image = morphology_majority(binary_image, iterations=20)
    binary_image = morphology_clean(binary_image)

    return binary_image


def morphology_majority(image, iterations=20):
    """
    Majority filter: pixel becomes foreground if majority of 3x3 neighbors are foreground.
    Equivalent to MATLAB: bwmorph(image, 'majority', iterations)
    """
    result = image.copy()
    for _ in range(iterations):
        # Count neighbors
        neighbors = ndimage.convolve(
            result.astype(np.uint8), np.ones((3, 3)), mode="constant"
        ) - result.astype(np.uint8)
        # Keep pixel if it has 5 or more neighbors (majority of 8 surrounding + itself)
        result = (neighbors >= 5) | result
    return result


def morphology_clean(image):
    """
    Remove isolated pixels.
    Equivalent to MATLAB: bwmorph(image, 'clean')
    """
    # Find isolated pixels (single foreground pixels with no neighbors)
    neighbors = ndimage.convolve(
        image.astype(np.uint8), np.ones((3, 3)), mode="constant"
    ) - image.astype(np.uint8)
    isolated = image & (neighbors == 0)
    return image & ~isolated


def calculate_confluency(mask):
    """Calculate confluency as area fraction."""
    total_pixels = mask.size
    cell_pixels = np.sum(mask)
    confluency = (cell_pixels / total_pixels) * 100.0
    return confluency


def process_phantast(
    image_input,
    sigma=8.0,
    epsilon=0.05,
    do_contrast_stretching=True,
    contrast_stretching_saturation=0.5,
    do_halo_removal=True,
    minimum_fill_area=100,
    do_remove_small_objects=True,
    minimum_object_area=100,
    hr_remove_small_objects=100,
    max_removal_ratio=0.3,
    do_additional_remove_holes=False,
    additional_hole_fill_area=100,
    output_mask_path=None,
    output_overlay_path=None,
):
    """
    Complete PHANTAST pipeline.
    Args:
        image_input: Path to image (str) OR numpy array (BGR or Gray).
    """
    # Load image
    if isinstance(image_input, str):
        image = cv2.imread(image_input)
        if image is None:
            raise ValueError(f"Could not load image: {image_input}")
        image_source_name = image_input
    elif isinstance(image_input, np.ndarray):
        image = image_input.copy()
        image_source_name = "Memory Array"
    else:
        raise ValueError("Input must be a file path or numpy array")

    # Convert to grayscale
    if len(image.shape) == 3:
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image_gray = image.copy()

    print(f"Processing image: {image_source_name}")
    print(f"Image size: {image_gray.shape}")
    print(f"Parameters: sigma={sigma}, epsilon={epsilon}")

    I = image_gray.copy()

    # Step 1: Contrast Stretching
    if do_contrast_stretching:
        print("Step 1: Contrast stretching...")
        I = contrast_stretching(
            I.astype(np.float64) / 255.0, contrast_stretching_saturation
        )

    # Step 2: Local Contrast (Coarse Masking)
    print("Step 2: Local contrast thresholding (CV = std/mean)...")
    J = local_contrast_cv(I, sigma, epsilon)

    # Step 3: Halo Removal
    if do_halo_removal:
        print("Step 3: Halo removal with Kirsch edge detection and region shrinking...")
        J = halo_removal(
            I,
            J,
            minimum_fill_area,
            "kirsch",
            hr_remove_small_objects,
            max_removal_ratio,
        )

    # Step 4: Additional hole removal
    if do_additional_remove_holes:
        print("Step 4: Additional hole filling...")
        J = remove_holes(J, additional_hole_fill_area)

    # Step 5: Remove small objects
    if do_remove_small_objects:
        print("Step 5: Removing small objects...")
        J = remove_small_objects(J, minimum_object_area)

    # Final cleanup
    J = morphology_majority(J, iterations=20)
    J = morphology_clean(J)

    # Calculate confluency
    confluency = calculate_confluency(J)

    print(f"\nResults:")
    print(f"  Confluency: {confluency:.2f}%")

    # Save outputs
    if output_mask_path:
        cv2.imwrite(output_mask_path, (J * 255).astype(np.uint8))
        print(f"  Mask saved to: {output_mask_path}")

    if output_overlay_path:
        overlay = cv2.cvtColor(image_gray, cv2.COLOR_GRAY2BGR)
        overlay[J] = [0, 255, 0]
        alpha = 0.4
        overlay = cv2.addWeighted(
            overlay, alpha, cv2.cvtColor(image_gray, cv2.COLOR_GRAY2BGR), 1 - alpha, 0
        )
        cv2.imwrite(output_overlay_path, overlay)
        print(f"  Overlay saved to: {output_overlay_path}")

    return confluency, J


def main():
    parser = argparse.ArgumentParser(
        description="PHANTAST Cell Confluency Detection (Corrected Implementation)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with defaults (optimized for stem cells)
  python phantast_confluency_corrected.py -i image.jpg
  
  # Adjust parameters
  python phantast_confluency_corrected.py -i image.jpg --sigma 6.0 --epsilon 0.06
  
  # Save results
  python phantast_confluency_corrected.py -i image.jpg -m mask.png -o overlay.png
  
Key Differences from Original:
  - Uses Coefficient of Variation (CV = std/mean) for local contrast
  - Separable Gaussian filtering with proper kernel sizing
  - Kirsch edge detection (8 directional kernels)
  - Full shrinkRegion algorithm with projection cones
  - Complete pipeline: contrast stretching, hole filling, morphology
        """,
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input phase contrast microscopy image path",
    )
    parser.add_argument(
        "--sigma",
        type=float,
        default=8.0,
        help="Scale parameter for local contrast (default: 8.0)",
    )
    parser.add_argument(
        "--epsilon",
        type=float,
        default=0.05,
        help="Sensitivity threshold (default: 0.05)",
    )
    parser.add_argument(
        "--no-contrast-stretch", action="store_true", help="Disable contrast stretching"
    )
    parser.add_argument(
        "--contrast-saturation",
        type=float,
        default=0.5,
        help="Contrast stretching saturation %% (default: 0.5)",
    )
    parser.add_argument(
        "--no-halo-removal", action="store_true", help="Disable halo removal"
    )
    parser.add_argument(
        "--min-fill-area",
        type=int,
        default=100,
        help="Minimum hole fill area (default: 100)",
    )
    parser.add_argument(
        "--no-remove-small", action="store_true", help="Disable small object removal"
    )
    parser.add_argument(
        "--min-object-area",
        type=int,
        default=100,
        help="Minimum object area (default: 100)",
    )
    parser.add_argument(
        "--hr-min-area",
        type=int,
        default=100,
        help="Halo removal: min area before processing (default: 100)",
    )
    parser.add_argument(
        "--max-removal-ratio",
        type=float,
        default=0.3,
        help="Max removal ratio for halo removal (default: 0.3)",
    )
    parser.add_argument("-m", "--mask", help="Output path for binary mask image")
    parser.add_argument("-o", "--overlay", help="Output path for overlay visualization")

    args = parser.parse_args()

    confluency, mask = process_phantast(
        args.input,
        sigma=args.sigma,
        epsilon=args.epsilon,
        do_contrast_stretching=not args.no_contrast_stretch,
        contrast_stretching_saturation=args.contrast_saturation,
        do_halo_removal=not args.no_halo_removal,
        minimum_fill_area=args.min_fill_area,
        do_remove_small_objects=not args.no_remove_small,
        minimum_object_area=args.min_object_area,
        hr_remove_small_objects=args.hr_min_area,
        max_removal_ratio=args.max_removal_ratio,
        output_mask_path=args.mask,
        output_overlay_path=args.overlay,
    )

    print(f"\n{'=' * 50}")
    print(f"FINAL CONFLUENCY: {confluency:.2f}%")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()

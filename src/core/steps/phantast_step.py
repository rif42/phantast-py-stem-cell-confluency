"""PHANTAST stem cell confluency detection step."""

import uuid

import cv2
import numpy as np
from scipy import ndimage
from skimage import measure

from . import StepParameter, register_step


STEP_NAME = "phantast"
STEP_DESCRIPTION = "PHANTAST - Stem cell confluency detection"
STEP_ICON = "🔬"

STEP_PARAMETERS = [
    StepParameter(
        name="sigma",
        type="float",
        default=8.0,
        min=1.0,
        max=20.0,
        step=0.1,
        description="Scale for local contrast filtering.",
    ),
    StepParameter(
        name="epsilon",
        type="float",
        default=0.05,
        min=0.01,
        max=0.5,
        step=0.01,
        description="Sensitivity threshold for local contrast.",
    ),
    StepParameter(
        name="contrast_stretch",
        type="bool",
        default=True,
        description="Enable contrast stretching before segmentation.",
    ),
    StepParameter(
        name="contrast_saturation",
        type="float",
        default=0.5,
        min=0.0,
        max=10.0,
        step=0.1,
        description="Saturation percentage used during contrast stretching.",
    ),
    StepParameter(
        name="halo_removal",
        type="bool",
        default=True,
        description="Enable PHANTAST halo removal refinement.",
    ),
    StepParameter(
        name="min_fill_area",
        type="int",
        default=100,
        min=0,
        max=1000,
        step=1,
        description="Maximum hole area to fill during halo removal.",
    ),
    StepParameter(
        name="remove_small_objects",
        type="bool",
        default=True,
        description="Enable small object removal in final mask.",
    ),
    StepParameter(
        name="min_object_area",
        type="int",
        default=100,
        min=0,
        max=1000,
        step=1,
        description="Minimum connected-component area to keep.",
    ),
    StepParameter(
        name="max_removal_ratio",
        type="float",
        default=0.3,
        min=0.0,
        max=1.0,
        step=0.01,
        description="Maximum shrink ratio during halo removal.",
    ),
]


def gaussian_filter_separable(image: np.ndarray, sigma: float) -> np.ndarray:
    kernel_size = int(np.ceil(2.9786 * sigma))
    x = np.arange(-kernel_size, kernel_size + 1)
    gaussian_kernel = np.exp(-(x**2) / (2 * sigma**2))
    gaussian_kernel = gaussian_kernel / np.sum(gaussian_kernel)

    filtered = ndimage.convolve1d(image, gaussian_kernel, axis=1, mode="nearest")
    filtered = ndimage.convolve1d(filtered, gaussian_kernel, axis=0, mode="nearest")
    return filtered


def contrast_stretching(image: np.ndarray, saturation_percentage: float) -> np.ndarray:
    if saturation_percentage == 0:
        return image

    if image.dtype != np.float64:
        image = (
            image.astype(np.float64) / 255.0
            if image.max() > 1
            else image.astype(np.float64)
        )

    low_percentile = saturation_percentage / 2.0
    high_percentile = 100.0 - low_percentile
    p_low = np.percentile(image, low_percentile)
    p_high = np.percentile(image, high_percentile)
    return np.clip((image - p_low) / (p_high - p_low + 1e-8), 0, 1)


def local_contrast_cv(image: np.ndarray, sigma: float, epsilon: float) -> np.ndarray:
    if image.dtype != np.float64:
        image = image.astype(np.float64) / 255.0

    filtered_mean = gaussian_filter_separable(image, sigma)
    filtered_mean_sq = gaussian_filter_separable(image**2, sigma)
    variance = np.maximum(filtered_mean_sq - filtered_mean**2, 0)
    std_dev = np.sqrt(variance)
    cv_map = std_dev / (filtered_mean + 1e-8)
    return cv_map > epsilon


def remove_small_objects_mask(image: np.ndarray, threshold_area: int) -> np.ndarray:
    labeled = measure.label(image)
    regions = measure.regionprops(labeled)
    new_image = np.zeros_like(image, dtype=bool)
    for region in regions:
        if region.area > threshold_area:
            new_image[labeled == region.label] = True
    return new_image


def remove_holes(image: np.ndarray, max_area: int) -> np.ndarray:
    filled = ndimage.binary_fill_holes(image)
    holes = filled & ~image
    labeled_holes = measure.label(holes)
    hole_regions = measure.regionprops(labeled_holes)

    result = image.copy()
    for region in hole_regions:
        if region.area <= max_area:
            coords = region.coords
            result[coords[:, 0], coords[:, 1]] = True
    return result


def kirsch_edge_detection(image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    kernels = [
        np.array([[-3, -3, 5], [-3, 0, 5], [-3, -3, 5]]),
        np.array([[-3, 5, 5], [-3, 0, 5], [-3, -3, -3]]),
        np.array([[5, 5, 5], [-3, 0, -3], [-3, -3, -3]]),
        np.array([[5, 5, -3], [5, 0, -3], [-3, -3, -3]]),
        np.array([[5, -3, -3], [5, 0, -3], [5, -3, -3]]),
        np.array([[-3, -3, -3], [5, 0, -3], [5, 5, -3]]),
        np.array([[-3, -3, -3], [-3, 0, -3], [5, 5, 5]]),
        np.array([[-3, -3, -3], [-3, 0, 5], [-3, 5, 5]]),
    ]

    responses = np.zeros((image.shape[0], image.shape[1], 8))
    for i, kernel in enumerate(kernels):
        responses[:, :, i] = ndimage.convolve(image, kernel, mode="constant", cval=0)

    gradient_intensity = np.max(responses, axis=2)
    gradient_direction = np.argmax(responses, axis=2) + 1
    return gradient_intensity, gradient_direction


def shrink_region(
    pixels_to_process: np.ndarray,
    gradient_direction_map: np.ndarray,
    projection_cones: np.ndarray,
    considered_as_starting_point: np.ndarray,
    direction_offsets: np.ndarray,
    binary_image: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rows, cols = binary_image.shape
    considered = considered_as_starting_point.copy()

    to_add_x: list[int] = []
    to_add_y: list[int] = []
    to_remove_x: list[int] = []
    to_remove_y: list[int] = []

    for idx in range(len(pixels_to_process)):
        current_x = int(pixels_to_process[idx, 0])
        current_y = int(pixels_to_process[idx, 1])

        if (
            current_x < 1
            or current_y < 1
            or current_x >= rows - 1
            or current_y >= cols - 1
        ):
            continue

        current_direction = int(gradient_direction_map[current_x, current_y])
        cone = projection_cones[current_direction - 1]

        if considered[current_x, current_y]:
            continue

        considered[current_x, current_y] = True
        valid_path = False

        for k in range(3):
            next_dir = cone[k]
            dx = int(direction_offsets[next_dir - 1, 0])
            dy = int(direction_offsets[next_dir - 1, 1])
            next_x = current_x + dx
            next_y = current_y + dy

            if next_x < 0 or next_y < 0 or next_x >= rows or next_y >= cols:
                continue

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
    image: np.ndarray,
    binary_image: np.ndarray,
    max_fill_area: int,
    kernel_type: str = "kirsch",
    small_object_removal_area: int = 100,
    delete_ratio: float = 0.3,
) -> np.ndarray:
    direction_offsets = np.array(
        [[0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1], [1, 0], [1, 1]]
    )
    projection_cones = np.array(
        [
            [1, 2, 8],
            [2, 1, 3],
            [3, 2, 4],
            [4, 3, 5],
            [5, 4, 6],
            [6, 5, 7],
            [7, 6, 8],
            [8, 1, 7],
        ]
    )

    if image.dtype != np.float64:
        image = image.astype(np.float64) / 255.0

    binary_image = remove_small_objects_mask(binary_image, small_object_removal_area)
    if max_fill_area > 0:
        binary_image = remove_holes(binary_image, max_fill_area)

    contours, _ = cv2.findContours(
        binary_image.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    boundary_pixels = []
    for contour in contours:
        for point in contour:
            boundary_pixels.append([point[0][1], point[0][0]])

    if not boundary_pixels:
        return binary_image

    pixels_to_process = np.array(boundary_pixels, dtype=np.uint16)

    if kernel_type != "kirsch":
        raise ValueError("Only 'kirsch' kernel type is implemented")
    _, gradient_direction = kirsch_edge_detection(image)

    considered_as_starting_point = np.zeros_like(binary_image, dtype=bool)
    objects_in_image = measure.label(binary_image)

    go = True
    iteration = 0
    max_iterations = 100
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
        if len(to_remove_x) > 0:
            binary_image[to_remove_x, to_remove_y] = False

        current_objects = measure.label(binary_image)
        current_regions = measure.regionprops(current_objects)
        for region in current_regions:
            original_pixels = objects_in_image == region.label
            remaining_pixels = current_objects == region.label
            if np.sum(remaining_pixels) < delete_ratio * np.sum(original_pixels):
                considered_as_starting_point[original_pixels] = True

        if len(to_add_x) == 0:
            go = False
        else:
            to_add = np.column_stack([to_add_x, to_add_y])
            pixels_to_process = np.unique(to_add, axis=0)

    binary_image = morphology_majority(binary_image, iterations=20)
    return morphology_clean(binary_image)


def morphology_majority(image: np.ndarray, iterations: int = 20) -> np.ndarray:
    result = image.copy()
    for _ in range(iterations):
        neighbors = ndimage.convolve(
            result.astype(np.uint8), np.ones((3, 3)), mode="constant"
        ) - result.astype(np.uint8)
        result = (neighbors >= 5) | result
    return result


def morphology_clean(image: np.ndarray) -> np.ndarray:
    neighbors = ndimage.convolve(
        image.astype(np.uint8), np.ones((3, 3)), mode="constant"
    ) - image.astype(np.uint8)
    isolated = image & (neighbors == 0)
    return image & ~isolated


def calculate_confluency(mask: np.ndarray) -> float:
    return (np.sum(mask) / mask.size) * 100.0


def process_phantast(
    image_input: np.ndarray,
    sigma: float = 8.0,
    epsilon: float = 0.05,
    do_contrast_stretching: bool = True,
    contrast_stretching_saturation: float = 0.5,
    do_halo_removal: bool = True,
    minimum_fill_area: int = 100,
    do_remove_small_objects: bool = True,
    minimum_object_area: int = 100,
    hr_remove_small_objects: int = 100,
    max_removal_ratio: float = 0.3,
) -> tuple[float, np.ndarray]:
    if image_input.ndim == 3:
        if image_input.shape[2] == 3:
            image_gray = cv2.cvtColor(image_input, cv2.COLOR_BGR2GRAY)
        elif image_input.shape[2] == 4:
            image_gray = cv2.cvtColor(image_input, cv2.COLOR_BGRA2GRAY)
        else:
            image_gray = image_input[:, :, 0]
    else:
        image_gray = image_input.copy()

    work_image = image_gray.copy()
    if do_contrast_stretching:
        work_image = contrast_stretching(
            work_image.astype(np.float64) / 255.0, contrast_stretching_saturation
        )

    mask = local_contrast_cv(work_image, sigma, epsilon)

    if do_halo_removal:
        mask = halo_removal(
            work_image,
            mask,
            minimum_fill_area,
            "kirsch",
            hr_remove_small_objects,
            max_removal_ratio,
        )

    if do_remove_small_objects:
        mask = remove_small_objects_mask(mask, minimum_object_area)

    mask = morphology_majority(mask, iterations=20)
    mask = morphology_clean(mask)
    confluency = calculate_confluency(mask)
    return confluency, mask


def process(
    image: np.ndarray,
    _metadata: dict | None = None,
    sigma: float = 8.0,
    epsilon: float = 0.05,
    contrast_stretch: bool = True,
    contrast_saturation: float = 0.5,
    halo_removal: bool = True,
    min_fill_area: int = 100,
    remove_small_objects: bool = True,
    min_object_area: int = 100,
    max_removal_ratio: float = 0.3,
) -> np.ndarray:
    """Apply full PHANTAST pipeline and return uint8 binary mask."""
    confluency, mask = process_phantast(
        image,
        sigma=sigma,
        epsilon=epsilon,
        do_contrast_stretching=contrast_stretch,
        contrast_stretching_saturation=contrast_saturation,
        do_halo_removal=halo_removal,
        minimum_fill_area=min_fill_area,
        do_remove_small_objects=remove_small_objects,
        minimum_object_area=min_object_area,
        hr_remove_small_objects=min_object_area,
        max_removal_ratio=max_removal_ratio,
    )
    if _metadata is not None:
        _metadata.update(
            {
                "confluency": confluency,
                "sigma": sigma,
                "epsilon": epsilon,
                "uuid": str(uuid.uuid4())[:8],
            }
        )
    return mask.astype(np.uint8) * 255


# Register the step
process = register_step(process)

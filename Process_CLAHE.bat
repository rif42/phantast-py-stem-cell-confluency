@echo off & python -x "%~f0" %* & pause & goto :eof
import cv2
import numpy as np
import os
from scipy.optimize import curve_fit

def calculate_entropy(img):
    """
    Calculates the discrete entropy of a grayscale image.
    H(x) = -sum(p(xi) * log2(p(xi)))
    """
    # Calculate histogram
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    # Normalize to get probabilities
    hist = hist.ravel() / hist.sum()
    # Filter out zero probabilities to avoid log calculation errors
    hist = hist[hist > 0]
    # Calculate entropy
    entropy = -np.sum(hist * np.log2(hist))
    return entropy

def double_exponential(x, c1, l1, c2, l2):
    """
    Double exponential function for curve fitting:
    f(x) = c1 * exp(-l1 * x) + c2 * exp(-l2 * x)
    """
    return c1 * np.exp(-l1 * x) + c2 * np.exp(-l2 * x)

def get_fitted_curvature(x, popt):
    """
    Calculates the curvature of the fitted double exponential function at points x.
    kappa = |f''| / (1 + f'^2)^(3/2)
    """
    c1, l1, c2, l2 = popt
    
    # First derivative: f'(x)
    dy = -c1 * l1 * np.exp(-l1 * x) - c2 * l2 * np.exp(-l2 * x)
    
    # Second derivative: f''(x)
    ddy = c1 * (l1**2) * np.exp(-l1 * x) + c2 * (l2**2) * np.exp(-l2 * x)
    
    # Curvature formula
    curvature = np.abs(ddy) / np.power(1 + dy**2, 1.5)
    return curvature

def optimize_clahe_parameters(img):
    """
    Determines optimal CLAHE parameters (Clip Limit and Block Size)
    using entropy maximization and curvature analysis.
    
    Returns:
        (optimal_clip_limit, optimal_tile_grid_size)
    """
    h, w = img.shape
    
    # --- STAGE A: Find Optimal Clip Limit ---
    # Fix Block Size to 8x8, vary Clip Limit
    
    # Range of Clip Limit to test (0.1 to 10.0)
    cl_range = np.linspace(0.1, 10.0, 20)
    entropies_cl = []
    
    fixed_grid_size = (8, 8)
    
    print("  Optimizing Clip Limit...")
    for cl in cl_range:
        clahe = cv2.createCLAHE(clipLimit=cl, tileGridSize=fixed_grid_size)
        res = clahe.apply(img)
        entropies_cl.append(calculate_entropy(res))
        
    entropies_cl = np.array(entropies_cl)
    
    optimal_cl = 2.0 # Default fallback
    
    try:
        # Fit double exponential curve
        # Initial guess: c1=max_entropy, l1=0.1, c2=max_entropy/2, l2=0.5
        p0 = [np.max(entropies_cl), 0.1, np.max(entropies_cl)/2, 0.5]
        try:
             popt_cl, _ = curve_fit(double_exponential, cl_range, entropies_cl, p0=p0, maxfev=10000)
        except:
             # Try without initial guess if specific one fails
             popt_cl, _ = curve_fit(double_exponential, cl_range, entropies_cl, maxfev=10000)
        
        # Calculate curvature along the fitted curve
        curvatures = get_fitted_curvature(cl_range, popt_cl)
        
        # Find point of maximum curvature
        max_k_idx = np.argmax(curvatures)
        optimal_cl = cl_range[max_k_idx]
        print(f"  Found optimal Clip Limit: {optimal_cl:.2f}")
        
    except Exception as e:
        print(f"  Warning: Optimization for Clip Limit failed ({e}). Using default {optimal_cl}.")

    # --- STAGE B: Find Optimal Block Size ---
    # Fix Clip Limit to optimal found, vary Block Size
    
    # Range of Block Sizes (2 to 32)
    bs_range = np.arange(2, 33, 2)
    entropies_bs = []
    
    print(f"  Optimizing Block Size using CL={optimal_cl:.2f}...")
    for bs in bs_range:
        clahe = cv2.createCLAHE(clipLimit=optimal_cl, tileGridSize=(bs, bs))
        res = clahe.apply(img)
        entropies_bs.append(calculate_entropy(res))
        
    entropies_bs = np.array(entropies_bs)
    
    optimal_bs = 8 # Default fallback
    
    try:
        # Fit double exponential curve
        p0 = [np.max(entropies_bs), 0.1, np.max(entropies_bs)/2, 0.5]
        try:
            popt_bs, _ = curve_fit(double_exponential, bs_range, entropies_bs, p0=p0, maxfev=10000)
        except:
            popt_bs, _ = curve_fit(double_exponential, bs_range, entropies_bs, maxfev=10000)
            
        curvatures_bs = get_fitted_curvature(bs_range, popt_bs)
        max_k_idx_bs = np.argmax(curvatures_bs)
        optimal_bs = bs_range[max_k_idx_bs]
        print(f"  Found optimal Block Size: {optimal_bs}x{optimal_bs}")
        
    except Exception as e:
        print(f"  Warning: Optimization for Block Size failed ({e}). Using default {optimal_bs}.")

    return optimal_cl, (int(optimal_bs), int(optimal_bs))

def apply_clahe(image_path, output_path, clip_limit=2.0, tile_grid_size=(8, 8), auto_optimize=False):
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return

    # Load image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error: Could not read image {image_path}")
        return

    if auto_optimize:
        print(f"Starting generic CLAHE optimization for {os.path.basename(image_path)}...")
        clip_limit, tile_grid_size = optimize_clahe_parameters(img)
        print(f"Applied optimized parameters: CL={clip_limit:.2f}, GS={tile_grid_size}")

    # Create CLAHE object
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    
    # Apply CLAHE
    clahe_img = clahe.apply(img)

    # Save output
    cv2.imwrite(output_path, clahe_img)
    print(f"Saved CLAHE corrected image to {output_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Apply CLAHE to images.")
    parser.add_argument("--input_dir", type=str, help="Input directory containing images.")
    parser.add_argument("--output_dir", type=str, help="Output directory for processed images.")
    parser.add_argument("--clip_limit", type=float, default=2.0, help="Clip limit for CLAHE.")
    parser.add_argument("--grid_size", type=int, default=8, help="Grid size for CLAHE (square grid).")
    parser.add_argument("--auto_optimize", action="store_true", help="Automatically optimize CLAHE parameters.")

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Determine input and output roots
    if args.input_dir:
        input_root = args.input_dir
    else:
        # Default to current directory if not specified
        input_root = script_dir

    if args.output_dir:
        output_root = args.output_dir
    else:
        # Default to processed_clahe subdirectory
        output_root = os.path.join(script_dir, "processed_clahe")

    # Use arguments or defaults
    clip_limit = args.clip_limit
    tile_grid_size = (args.grid_size, args.grid_size)
    auto_optimize = args.auto_optimize

    if not os.path.exists(output_root):
        os.makedirs(output_root)

    print(f"Input Directory: {input_root}")
    print(f"Output Directory: {output_root}")
    print(f"Clip Limit: {clip_limit}")
    print(f"Grid Size: {tile_grid_size}")
    print(f"Auto Optimize: {auto_optimize}")

    valid_extensions = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}

    processed_count = 0
    
    # Only list files in the input directory, no recursion
    try:
        files = [f for f in os.listdir(input_root) if os.path.isfile(os.path.join(input_root, f))]
    except FileNotFoundError:
        print(f"Error: Input directory {input_root} not found.")
        files = []

    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext in valid_extensions:
            # Skip output directory and other non-image files if they match extension somehow
            # (though listdir prevents recursing into dirs)
            
            # Avoid re-processing output files if output_dir is inside input_dir and we somehow listed them?
            # listdir is usually safe as it's not recursive.
            
            input_path = os.path.join(input_root, file)
            
            # Direct output to output_root, no subdirectory structure maintenance
            output_path = os.path.join(output_root, file)
            
            print(f"Processing {file}...")
            apply_clahe(input_path, output_path, clip_limit=clip_limit, tile_grid_size=tile_grid_size, auto_optimize=auto_optimize)
            processed_count += 1
    
    print(f"Done. Processed {processed_count} images.")

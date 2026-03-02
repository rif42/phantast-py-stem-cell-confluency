
import cv2
import numpy as np
from abc import ABC, abstractmethod

# Try to import PHANTAST integration if available
try:
    from phantast_confluency_corrected import process_phantast
except ImportError:
    process_phantast = None
    print("Warning: phantast_confluency_corrected module not found.")


class StepParameter:
    """Metdata for a step parameter to generate UI controls."""
    def __init__(self, name, param_type, default, min_val=None, max_val=None, description=""):
        self.name = name
        self.type = param_type  # 'float', 'int', 'bool', 'choice'
        self.default = default
        self.min = min_val
        self.max = max_val
        self.description = description


class PipelineStep(ABC):
    """Abstract base class for a processing step."""
    def __init__(self):
        self.enabled = True
        self.params = {}
        # Define parameters in subclass __init__ using self.define_params()

    def define_params(self):
        """Override to return a list of StepParameter objects."""
        return []

    def get_param(self, name):
        """Get current value of a parameter."""
        return self.params.get(name, self.get_default(name))

    def get_default(self, name):
        """Get default value of a parameter."""
        for p in self.define_params():
            if p.name == name:
                return p.default
        return None

    def set_param(self, name, value):
        """Set a parameter value."""
        self.params[name] = value

    @abstractmethod
    def process(self, image: np.ndarray, metadata: dict) -> np.ndarray:
        """
        Process the image.
        Args:
            image: Input image (numpy array, usually BGR or Gray).
            metadata: Dict to store/retrieve inter-step data (e.g. masks, metrics).
        Returns:
            Processed image.
        """
        pass

    @property
    def name(self):
        return self.__class__.__name__


class GrayscaleStep(PipelineStep):
    def process(self, image, metadata):
        if len(image.shape) == 3 and image.shape[2] == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image

    @property
    def name(self):
        return "Grayscale Conversion"


class GaussianBlurStep(PipelineStep):
    def define_params(self):
        return [
            StepParameter("kernel_size", "int", 5, 1, 31, "Kernel Size (odd number)"),
            StepParameter("sigma", "float", 0, 0, 10.0, "Sigma (0 = auto)"),
        ]

    def process(self, image, metadata):
        k = self.get_param("kernel_size")
        if k % 2 == 0: k += 1
        sigma = self.get_param("sigma")
        return cv2.GaussianBlur(image, (k, k), sigma)

    @property
    def name(self):
        return "Gaussian Blur"


class ClaheStep(PipelineStep):
    def define_params(self):
        return [
            StepParameter("clip_limit", "float", 2.0, 0.1, 10.0, "Clip Limit"),
            StepParameter("tile_grid_size", "int", 8, 1, 32, "Tile Grid Size"),
        ]

    def process(self, image, metadata):
        # Ensure grayscale
        if len(image.shape) == 3 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        clahe = cv2.createCLAHE(
            clipLimit=self.get_param("clip_limit"),
            tileGridSize=(self.get_param("tile_grid_size"), self.get_param("tile_grid_size"))
        )
        return clahe.apply(gray)

    @property
    def name(self):
        return "CLAHE (Contrast Limited Adaptive Histogram Equalization)"


class PhantastStep(PipelineStep):
    def define_params(self):
        return [
            StepParameter("sigma", "float", 4.0, 0.1, 20.0, "Sigma (Feature Scale)"), # Default 4.0 often good for 10x
            StepParameter("epsilon", "float", 0.05, 0.01, 0.2, "Epsilon (Sensitivity)"),
        ]

    def process(self, image, metadata):
        if process_phantast is None:
            return image

        # The PHANTAST integration now accepts numpy arrays directly.
        
        # We only need the mask return
        # But `process_phantast` returns (confluency, mask)
        
        confluency, mask = process_phantast(
            image,
            sigma=self.get_param("sigma"),
            epsilon=self.get_param("epsilon"),
            output_mask_path=None,
            output_overlay_path=None
        )
        
        # Store results in metadata for the UI
        metadata["phantast_confluency"] = confluency
        metadata["phantast_mask"] = mask
        
        # Create overlay visualization for the pipeline chain
        # Green overlay
        overlay = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR) if len(image.shape) == 2 else image.copy()
        
        # Ensure mask is boolean or uint8 0/1 for indexing
        # mask from phantast is boolean
        
        # We need to make sure overlay is big enough or matching size
        # Should be same size as input image
        
        # Create a colored mask
        colored_mask = np.zeros_like(overlay)
        colored_mask[mask] = [0, 255, 0] # BGR Green
        
        # Blend: Original Image + Green Mask
        # If original is grayscale, convert to BGR first (done above)
        
        # Use addWeighted for transparency
        # To do this only on the masked area efficiently:
        # result = image * (1-alpha) + mask_color * alpha
        
        # cv2.addWeighted works on full images
        
        result = cv2.addWeighted(overlay, 0.7, colored_mask, 0.3, 0)
        
        # But wait, addWeighted on the whole image will darken the non-masked areas if colored_mask is black there.
        # We want: non-masked areas -> original image
        # Masked areas -> blend
        
        # Correct approach:
        final_overlay = overlay.copy()
        # Indices where mask is True
        # blend manually or using ROI
        
        # Actually simplest:
        # result = image.copy()
        # result[mask] = result[mask] * 0.7 + green * 0.3  <-- logic
        
        # Using cv2:
        # Create a full green image
        green_img = np.zeros_like(overlay)
        green_img[:] = [0, 255, 0]
        
        # Blend full images
        blended = cv2.addWeighted(overlay, 0.7, green_img, 0.3, 0)
        
        # Combine using mask
        final_output = overlay.copy()
        final_output[mask] = blended[mask]
        
        return final_output

    @property
    def name(self):
        return "PHANTAST Confluency"

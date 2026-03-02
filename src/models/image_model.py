import os

class ImageSessionModel:
    """
    Manages the current state of an image viewing session (single file or folder).
    Contains no PyQt GUI or Qt classes, meaning it can be unit tested without Qt.
    """
    def __init__(self):
        self.mode = "EMPTY"  # EMPTY, SINGLE, FOLDER
        self.current_folder = None
        self.active_image = None  # Expected format: {'filename': '...', 'filepath': '...'}
        self.files = []
        
        self.valid_extensions = ('.png', '.jpg', '.jpeg', '.tif', '.tiff')

    def set_single_image(self, filepath: str):
        """Sets the model state to a single valid image."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Image not found: {filepath}")
            
        self.mode = "SINGLE"
        self.current_folder = None
        self.files = []
        self.active_image = {
            'filename': os.path.basename(filepath),
            'filepath': filepath
        }

    def set_folder(self, folderpath: str):
        """Sets the model state to a folder and loads all valid images."""
        if not os.path.exists(folderpath):
            raise NotADirectoryError(f"Folder not found: {folderpath}")
            
        self.mode = "FOLDER"
        self.current_folder = folderpath
        
        # Load files and filter by valid extensions
        all_files = os.listdir(folderpath)
        self.files = [f for f in all_files if f.lower().endswith(self.valid_extensions)]
        
        if self.files:
            first_file = self.files[0]
            self.active_image = {
                'filename': first_file,
                'filepath': os.path.join(folderpath, first_file)
            }
        else:
            self.active_image = None

    def set_active_image(self, filename: str):
        """Sets the active image from the currently loaded folder."""
        if self.mode != "FOLDER":
            raise ValueError("Cannot select file by name if not in FOLDER mode.")
            
        if filename not in self.files:
            raise FileNotFoundError(f"File {filename} not found in loaded files.")
            
        self.active_image = {
            'filename': filename,
            'filepath': os.path.join(self.current_folder, filename)
        }

    def clear(self):
        """Clears the session state."""
        self.mode = "EMPTY"
        self.current_folder = None
        self.active_image = None
        self.files = []

    def get_file_size_formatted(self, filepath: str) -> str:
        """Returns format e.g. '1.50 MB' or '500 KB' for a given file without using Qt."""
        if not filepath or not os.path.exists(filepath):
            return "-"
            
        file_size_bytes = os.path.getsize(filepath)
        if file_size_bytes > 1024 * 1024:
            return f"{file_size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{file_size_bytes / 1024:.0f} KB"

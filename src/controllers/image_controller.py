from PyQt6.QtGui import QImageReader, QImage


class ImageNavigationController:
    """
    Acts as the glue between the ImageNavigationWidget (View) and ImageSessionModel (Model).
    """

    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Connect View Signals to Controller Methods
        self.view.open_single_image_requested.connect(self.handle_open_single_image)
        self.view.open_folder_requested.connect(self.handle_open_folder)
        self.view.file_selected.connect(self.handle_file_selected)

    def handle_open_single_image(self, file_path: str):
        """Called by the View when a single file is selected from OS dialog."""
        try:
            self.model.set_single_image(file_path)
            self._update_view_from_model()
        except Exception as e:
            print(f"Error opening image: {e}")

    def handle_open_folder(self, folder_path: str):
        """Called by the View when a folder is selected from OS dialog."""
        try:
            self.model.set_folder(folder_path)
            self._update_view_from_model()
        except Exception as e:
            print(f"Error opening folder: {e}")

    def handle_file_selected(self, filename: str):
        """Called by the View when an item is clicked in the file list."""
        try:
            self.model.set_active_image(filename)

            # Update view to show VIEWING status
            self.view.set_active_file(filename)

            self._update_metadata_ui()

            # Request the view to load the image onto the canvas
            if self.model.active_image:
                self.view.load_image_to_canvas(self.model.active_image["filepath"])
        except Exception as e:
            print(f"Error selecting file: {e}")

    def _update_view_from_model(self):
        """Syncs the entire View state with the Model's current state."""
        self.view.set_mode(self.model.mode)

        # Update file list if in FOLDER mode
        if self.model.mode == "FOLDER":
            self.view.update_file_list(self.model.files, self.model.current_folder)

        # Update metadata for the initial active image (if any)
        self._update_metadata_ui()

        # Set active file in view and load onto canvas
        if self.model.active_image:
            filename = self.model.active_image["filename"]
            self.view.set_active_file(filename)
            self.view.load_image_to_canvas(self.model.active_image["filepath"])

    def _update_metadata_ui(self):
        """Extracts metadata via Model and Qt, then pushes string values to the View."""
        if not self.model.active_image:
            self.view.update_metadata_display("-", "-", "-", "-", "-", "-")
            return

        filepath = self.model.active_image.get("filepath")
        filename = self.model.active_image.get("filename")

        if not filepath:
            self.view.update_metadata_display("-", "-", "-", "-", "-", "-")
            return

        # 1. Dimensions
        reader = QImageReader(filepath)
        size = reader.size()
        dim_str = f"{size.width()} x {size.height()}" if size.isValid() else "Unknown"

        # 2. Qt Image Formats -> Bit Depth / Channels
        img_format = reader.imageFormat()
        if img_format == QImage.Format.Format_Grayscale8:
            bitdepth_str = "8-bit"
            channels_str = "Grayscale (1)"
        elif img_format == QImage.Format.Format_Grayscale16:
            bitdepth_str = "16-bit"
            channels_str = "Grayscale (1)"
        else:
            bitdepth_str = "8-bit/channel"  # Approximate default
            channels_str = "RGB (3)"

        # 3. File Size (via Model)
        filesize_str = self.model.get_file_size_formatted(filepath)

        # 4. Total files (if folder)
        file_count_str = (
            f"{len(self.model.files)} Files"
            if self.model.mode == "FOLDER"
            else filename
        )

        # Push to View
        self.view.update_metadata_display(
            filename=filename,
            subtitle=file_count_str,
            dimensions=dim_str,
            bitdepth=bitdepth_str,
            channels=channels_str,
            filesize=filesize_str,
        )

import os
import sys
import unittest
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

# Ensure we can import the src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from sections.image_navigation_inspection.views.image_navigation import ImageNavigationWidget

app = QApplication(sys.argv)

TEST_IMAGE_PATH = r"e:\work\stemcell\phantast-py\stemcell.jpg"
TEST_FOLDER_PATH = r"e:\work\stemcell\phantast-py\testfolder"

class TestImageNavigationUI(unittest.TestCase):
    def setUp(self):
        # Create a real widget instance
        self.widget = ImageNavigationWidget()
        self.widget.show()

    @patch('sections.image_navigation_inspection.views.image_navigation.QFileDialog.getOpenFileName')
    def test_a_open_single_image_click(self, mock_getOpenFileName):
        """Simulate clicking 'Open an Image' with test data"""
        mock_getOpenFileName.return_value = (TEST_IMAGE_PATH, "Images (*.*)")
        
        # Verify initial UI state uses the empty overlay
        self.assertEqual(self.widget.mode, "EMPTY")
        self.assertTrue(self.widget.empty_overlay.isVisible())

        # Programmatically click the button
        QTest.mouseClick(self.widget.btn_open_img, Qt.MouseButton.LeftButton)

        # Verify UI transitions to SINGLE mode
        self.assertEqual(self.widget.mode, "SINGLE")
        self.assertTrue(self.widget.left_panel.isVisible())
        self.assertTrue(self.widget.right_panel.isVisible())
        self.assertFalse(self.widget.empty_overlay.isVisible())
        
        # Verify the dimensions populated without crashing
        dims = self.widget.row_dimensions.text()
        self.assertNotEqual(dims, "")
        self.assertNotEqual(dims, "-")

    @patch('sections.image_navigation_inspection.views.image_navigation.QFileDialog.getExistingDirectory')
    def test_b_open_folder_click(self, mock_getExistingDirectory):
        """Simulate clicking 'Open a Folder' with test data"""
        mock_getExistingDirectory.return_value = TEST_FOLDER_PATH

        # Programmatically click the button
        QTest.mouseClick(self.widget.btn_open_folder, Qt.MouseButton.LeftButton)

        # Verify UI transitions to FOLDER mode  
        self.assertEqual(self.widget.mode, "FOLDER")
        self.assertTrue(self.widget.folder_explorer_widget.isVisible())
        
        # Verify folder list populated.
        if os.path.exists(TEST_FOLDER_PATH):
            self.assertGreater(self.widget.file_list.count(), 0)
        
        # Verify mode label
        self.assertEqual(self.widget.input_node_title.text(), "Sample Data")

    def tearDown(self):
        self.widget.close()

if __name__ == '__main__':
    unittest.main()

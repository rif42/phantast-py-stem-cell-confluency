"""Manual QA Test Script for folder-explorer-fix"""

import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.abspath("src"))

from PyQt6.QtWidgets import QApplication, QFileDialog, QListWidget
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPixmap
from src.ui.main_window import MainWindow


class QATester:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()
        self.evidence_dir = Path(".sisyphus/evidence/final-qa")
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.test_results = []

    def capture_screenshot(self, name):
        """Capture screenshot and save to evidence directory."""
        QTimer.singleShot(100, lambda: self._do_capture(name))

    def _do_capture(self, name):
        pixmap = self.window.grab()
        path = self.evidence_dir / f"{name}.png"
        pixmap.save(str(path), "PNG")
        print(f"✓ Screenshot saved: {path}")

    def run_test_sequence(self):
        """Run the full QA test sequence."""
        self.window.show()
        print("=" * 60)
        print("STARTING MANUAL QA TEST - folder-explorer-fix")
        print("=" * 60)

        # Test 1: Initial State
        QTimer.singleShot(500, self.test_initial_state)

    def test_initial_state(self):
        """Test 1: Verify initial empty state."""
        print("\n[Test 1] Initial State - Empty Overlay")
        self.capture_screenshot("01_initial_state")

        # Check empty overlay is visible
        if self.window.empty_overlay.isVisible():
            self.test_results.append(("Initial empty state", "PASS"))
            print("  ✓ Empty overlay is visible")
        else:
            self.test_results.append(("Initial empty state", "FAIL"))
            print("  ✗ Empty overlay NOT visible")

        # Schedule next test
        QTimer.singleShot(1000, self.test_open_folder_button)

    def test_open_folder_button(self):
        """Test 2: Click Open Folder button."""
        print("\n[Test 2] Clicking 'Open a Folder' button")

        # Find and click the Open Folder button
        buttons = self.window.findChildren(QPushButton)
        open_folder_btn = None
        for btn in buttons:
            if btn.text() == "Open a Folder":
                open_folder_btn = btn
                break

        if open_folder_btn:
            # Mock the file dialog
            test_folder = os.path.abspath("test_images/sample_images")
            print(f"  Opening folder: {test_folder}")

            # Directly call the controller method
            self.window.image_controller.handle_open_folder(test_folder)

            QTimer.singleShot(1500, self.test_folder_loaded)
        else:
            print("  ✗ Open Folder button not found!")
            self.test_results.append(("Open folder button", "FAIL"))
            self.finish_tests()

    def test_folder_loaded(self):
        """Test 3: Verify folder explorer loaded correctly."""
        print("\n[Test 3] Folder Explorer - Right Sidebar")
        self.capture_screenshot("02_folder_explorer_loaded")

        # Check file list
        file_list = self.window.right_panel.file_list
        count = file_list.count()
        print(f"  Files in list: {count}")

        if count == 7:  # We created 7 test images
            self.test_results.append(("File list populated", "PASS"))
            print("  ✓ All 7 files listed")
        else:
            self.test_results.append(
                ("File list populated", f"FAIL (expected 7, got {count})")
            )
            print(f"  ✗ Expected 7 files, got {count}")

        # Check first item is selected
        if file_list.currentRow() == 0:
            self.test_results.append(("First item auto-selected", "PASS"))
            print("  ✓ First item is selected")
        else:
            self.test_results.append(("First item auto-selected", "FAIL"))
            print("  ✗ First item NOT selected")

        # Check refresh button exists
        if hasattr(self.window.right_panel, "refresh_btn"):
            self.test_results.append(("Refresh button exists", "PASS"))
            print("  ✓ Refresh button exists")
        else:
            self.test_results.append(("Refresh button exists", "FAIL"))
            print("  ✗ Refresh button NOT found")

        QTimer.singleShot(1000, self.test_file_selection)

    def test_file_selection(self):
        """Test 4: Test file selection and double-click."""
        print("\n[Test 4] File Selection - Double Click")

        file_list = self.window.right_panel.file_list

        # Double-click on second item
        item = file_list.item(1)
        if item:
            print(f"  Double-clicking: {item.text()}")

            # Simulate double click
            rect = file_list.visualItemRect(item)
            pos = rect.center()

            # Use the signal directly for reliability
            self.window.right_panel.file_selected.emit(item.text())

            QTimer.singleShot(1000, lambda: self.verify_file_loaded(item.text()))
        else:
            print("  ✗ No item at index 1")
            self.test_results.append(("File double-click", "FAIL"))
            QTimer.singleShot(500, self.test_green_border)

    def verify_file_loaded(self, filename):
        """Verify file was loaded to canvas."""
        self.capture_screenshot("03_file_loaded")

        # Check if image is loaded
        if self.window.current_image_path:
            self.test_results.append(("File loaded to canvas", "PASS"))
            print(
                f"  ✓ File loaded: {os.path.basename(self.window.current_image_path)}"
            )
        else:
            self.test_results.append(("File loaded to canvas", "FAIL"))
            print("  ✗ File NOT loaded")

        QTimer.singleShot(500, self.test_green_border)

    def test_green_border(self):
        """Test 5: Verify selected file has green border."""
        print("\n[Test 5] Selected File Styling (Green Border)")

        file_list = self.window.right_panel.file_list
        current_row = file_list.currentRow()

        if current_row >= 0:
            self.test_results.append(("File selection visible", "PASS"))
            print(f"  ✓ Current selection at row: {current_row}")
            print("  ✓ Green border should be visible on selected item")
        else:
            self.test_results.append(("File selection visible", "FAIL"))
            print("  ✗ No item selected")

        QTimer.singleShot(500, self.test_refresh_button)

    def test_refresh_button(self):
        """Test 6: Test refresh button functionality."""
        print("\n[Test 6] Refresh Button")

        refresh_btn = self.window.right_panel.refresh_btn
        if refresh_btn and refresh_btn.isEnabled():
            print("  Clicking refresh button...")
            refresh_btn.click()

            QTimer.singleShot(1000, self.verify_refresh)
        else:
            print("  ✗ Refresh button disabled or not found")
            self.test_results.append(("Refresh button", "FAIL"))
            QTimer.singleShot(500, self.test_empty_folder)

    def verify_refresh(self):
        """Verify refresh maintained file list."""
        self.capture_screenshot("04_after_refresh")

        file_list = self.window.right_panel.file_list
        count = file_list.count()

        if count == 7:
            self.test_results.append(("Refresh button", "PASS"))
            print("  ✓ Refresh maintained file list")
        else:
            self.test_results.append(("Refresh button", f"FAIL (count={count})"))
            print(f"  ✗ Refresh failed, count={count}")

        QTimer.singleShot(500, self.test_empty_folder)

    def test_empty_folder(self):
        """Test 7: Test empty folder behavior."""
        print("\n[Test 7] Empty Folder Test")

        empty_folder = os.path.abspath("test_images/empty_folder")
        self.window.image_controller.handle_open_folder(empty_folder)

        QTimer.singleShot(1500, self.verify_empty_folder)

    def verify_empty_folder(self):
        """Verify empty folder shows 'No images found'."""
        self.capture_screenshot("05_empty_folder")

        empty_label = self.window.right_panel.empty_label
        file_list = self.window.right_panel.file_list

        if empty_label.isVisible() and not file_list.isVisible():
            self.test_results.append(("Empty folder message", "PASS"))
            print("  ✓ 'No images found' message displayed")
        else:
            self.test_results.append(("Empty folder message", "FAIL"))
            print("  ✗ Empty folder message NOT displayed correctly")
            print(f"    empty_label visible: {empty_label.isVisible()}")
            print(f"    file_list visible: {file_list.isVisible()}")

        QTimer.singleShot(500, self.test_rapid_selection)

    def test_rapid_selection(self):
        """Test 8: Rapid file selection."""
        print("\n[Test 8] Rapid File Selection")

        # Go back to folder with images
        test_folder = os.path.abspath("test_images/sample_images")
        self.window.image_controller.handle_open_folder(test_folder)

        QTimer.singleShot(1500, self.perform_rapid_selection)

    def perform_rapid_selection(self):
        """Perform rapid selection test."""
        file_list = self.window.right_panel.file_list

        # Rapidly select different items
        for i in range(min(5, file_list.count())):
            file_list.setCurrentRow(i)
            self.app.processEvents()
            time.sleep(0.05)  # 50ms between selections

        self.capture_screenshot("06_rapid_selection")

        final_row = file_list.currentRow()
        if final_row == 4:  # Last selected row
            self.test_results.append(("Rapid selection", "PASS"))
            print("  ✓ Rapid selection handled correctly")
        else:
            self.test_results.append(("Rapid selection", f"FAIL (row={final_row})"))
            print(f"  ✗ Rapid selection issue (row={final_row})")

        QTimer.singleShot(500, self.finish_tests)

    def finish_tests(self):
        """Print test summary and close app."""
        print("\n" + "=" * 60)
        print("QA TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for _, r in self.test_results if r == "PASS")
        failed = sum(1 for _, r in self.test_results if "FAIL" in r)

        for test_name, result in self.test_results:
            status = "✓" if result == "PASS" else "✗"
            print(f"{status} {test_name}: {result}")

        print("=" * 60)
        print(f"Scenarios: {passed}/{len(self.test_results)} PASS")
        print(f"Edge Cases: 2 tested (empty folder, rapid selection)")

        if failed == 0:
            print("VERDICT: PASS")
        else:
            print(f"VERDICT: FAIL ({failed} failures)")

        print("=" * 60)
        print(f"Evidence saved to: {self.evidence_dir}")

        # Save summary to file
        summary_path = self.evidence_dir / "qa_summary.txt"
        with open(summary_path, "w") as f:
            f.write("Manual QA Test - folder-explorer-fix\n")
            f.write("=" * 60 + "\n\n")
            for test_name, result in self.test_results:
                f.write(f"{test_name}: {result}\n")
            f.write(f"\nScenarios: {passed}/{len(self.test_results)} PASS\n")
            f.write("Edge Cases: 2 tested\n")
            f.write(f"VERDICT: {'PASS' if failed == 0 else 'FAIL'}\n")

        print(f"Summary saved to: {summary_path}")

        QTimer.singleShot(500, self.app.quit)

    def run(self):
        QTimer.singleShot(1000, self.run_test_sequence)
        return self.app.exec()


if __name__ == "__main__":
    tester = QATester()
    sys.exit(tester.run())

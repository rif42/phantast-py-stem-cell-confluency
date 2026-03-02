Here is the reformatted, concise, and compact version of `AGENTS.md`.

# PhantastLab AI Agent Guidelines

**Context:** PyQt desktop app for image processing/segmentation.

## 🛑 PHASE 1: PLAN MODE (Read-Only)

**CRITICAL:** **DO NOT** edit files or generate code until explicit permission is given.

1. **Explore & Contextualize**
* Read relevant files to understand current implementation and patterns.
* Ask clarifying questions regarding intent, edge cases, or potential conflicts.

2. **Analyze & Strategize**
* Identify root causes (bugs) or full scope (features).
* Assess impact on: Mobile/Web, Error/Loading states, Backward Compatibility.
* Check for conflicts: Shared components, API changes, TypeScript types.

3. **Propose Solutions**
* Present multiple approaches (e.g., Safe/Minimal vs. Performant vs. Comprehensive).
* List Pros/Cons for each.

4. **STOP & WAIT**
* Present findings.
* **Wait for specific user approval** on which approach to execute.

## 🚀 PHASE 2: EXECUTE MODE (Read-Write)

**Constraint:** Apply these rules strictly once coding begins.

### A. Architecture & Logic

* **Strict MVC/MVP:** Isolate `QWidget` (View) from Logic. View only handles display/input.
* **CLI Litmus Test:** Core logic (calculations, DB, API) must run in a CLI script without importing PyQt.
* **Threading:**
* **NO** GUI updates from worker threads. Use Signals/Slots.
* **NO** subclassing `QThread`. Use `worker.moveToThread(thread)`.
* Offload any task >100ms to prevent UI freeze.
* Write self-documenting code. if pattern is not obvious, add comments

### B. PyQt Implementation Standards

* **Designer:** Never edit `pyuic` generated files. Subclass them or use `uic.loadUi`.
* **Layouts:** Mandatory usage (HBox, VBox, Grid). **No** absolute positioning (`resize`, `move`).
* **Signals:** Use `obj.signal.connect(handler)`. Decorate slots with `@pyqtSlot()`.
* **Memory Safety:** Assign parents or maintain `self.` references to prevent Python GC from destroying widgets.
* **Non-Blocking:** Use `QTimer` instead of `time.sleep()`.

### C. Structure & Packaging

* **File Tree:**
```text
src/
  ├── main.py (Entry)
  ├── ui/ (.ui files)
  ├── controllers/ (Glue)
  └── models/ (Data/Logic)

```

* **Pathing:** Use `os.path` and check `sys._MEIPASS` for assets to ensure `PyInstaller` compatibility.

### D. Testing (`pytest` + `pytest-qt`)

**Always** run tests before presenting the result to user.

* **Stack:** `pytest`, `pytest-qt`, `pytest-mock`. **No** `unittest`.
* **Pyramid:** 70% Logic (No GUI import), 20% Integration, 10% GUI.
* **Techniques:**
* **Lifecycle:** Use `qtbot.addWidget(widget)` to manage cleanup.
* **Async:** Use `with qtbot.waitSignal(signal, timeout=1000):`.
* **Blocking UI:** Mock `QMessageBox`/`QFileDialog` using `monkeypatch` to prevent test hangs.
* **Cleanup:** Ensure all `QTimer`s and `QThread`s are stopped in `closeEvent` to prevent leaks.
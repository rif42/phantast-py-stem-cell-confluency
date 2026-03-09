Manual UI capture checklist (headless CLI cannot produce desktop screenshots):

1) Progress feedback screenshot/GIF
- Launch app: `python src/main.py`
- Load an image and run pipeline with at least one processing step.
- Capture status bar showing: `Processing: <Step Name>...` and visible progress bar.

2) Error dialog screenshot
- Introduce an invalid step config or force an unknown step.
- Run pipeline and capture the `Pipeline Error` dialog.

Save captures in this folder with suggested names:
- `progress-feedback.png` (or `.gif`)
- `error-dialog.png`

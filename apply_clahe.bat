@echo off
set "SCRIPT_PATH=%~dp0.\CLAHE.py"
echo Running CLAHE on images in %~dp0...
python "%SCRIPT_PATH%" --input_dir "%~dp0." --output_dir "%~dp0processed_clahe" --clip_limit 2.0 --grid_size 8
echo Done.
pause

# Phantast Lab

## Description
A desktop application designed to streamline the analysis of mesenchymal stem cell microscope images. It allows researchers to experiment with and build custom image processing pipelines to clean, enhance, and annotate raw images before calculating confluency using the PHANTAST algorithm.

## Problems & Solutions

### Problem 1: Variable Image Quality
Raw microscope images often have uneven lighting or artifacts, making direct analysis unreliable.
**Solution:** Customizable processing pipelines allow users to chain preprocessing steps (like CLAHE, noise reduction, cropping) to standardize images.

### Problem 2: Trial and Error Analysis
Finding the right parameters for image segmentation requires significant experimentation.
**Solution:** An iterative workflow lets users easily tweak settings, apply basic effects (grayscale), and re-run pipelines on single images to find the perfect recipe.

### Problem 3: Manual Repetition
Applying the same steps to many images individually is tedious and prone to error.
**Solution:** Define a pipeline once on a representative image and apply it to an entire batch of images seamlessly.

## Key Features
- **Pipeline Builder:** Select and order processing steps (Preprocessing → Enhancement → PHANTAST).
- **Basic Processing:** Essential tools including cropping, grayscaling, and adding text or freeform drawings.
- **Image Inspection:** specialized tools for detailed examination, including Zoom In/Out, Panning, and a Ruler for measurements.
- **Phantast Integration:** Built-in execution of the PHANTAST algorithm for accurate confluency calculation.
- **Batch & Single Modes:** Process one image to test parameters, then run the approved pipeline on a full dataset.

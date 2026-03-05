# Phantast Lab - Product Overview

## Description

Phantast Lab is a desktop application designed to streamline the analysis of mesenchymal stem cell microscope images. It allows researchers to experiment with and build custom image processing pipelines to clean, enhance, and annotate raw images before calculating confluency using the PHANTAST algorithm.

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

| Feature | Description |
|---------|-------------|
| **Pipeline Builder** | Select and order processing steps (Preprocessing → Enhancement → PHANTAST) |
| **Basic Processing** | Essential tools including cropping, grayscaling, and adding text or freeform drawings |
| **Image Inspection** | Specialized tools for detailed examination: Zoom, Pan, Ruler for measurements |
| **Phantast Integration** | Built-in execution of the PHANTAST algorithm for accurate confluency calculation |
| **Batch & Single Modes** | Process one image to test parameters, then run the approved pipeline on a full dataset |

## Product Roadmap

### 1. Image Navigation & Inspection
Managing the input (single images or folders) and tools for detailed examination (zoom, pan, ruler).

### 2. Pipeline Construction
The core editor for adding, reordering, and toggling processing steps (including the default PHANTAST node).

### 3. Node Configuration
The property sidebar for fine-tuning parameters and settings of each selected processing node.

### 4. Batch Execution & Output
Applying the finalized pipeline across full datasets and managing the exported confluency results.

## Target Users

- Biology researchers working with stem cell microscopy
- Lab technicians analyzing cell confluency
- Scientists needing standardized image processing protocols

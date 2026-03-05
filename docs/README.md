# Phantast Lab Documentation

**A desktop application for mesenchymal stem cell image analysis and confluency detection.**

## Quick Links

- [Product Overview](./product-overview.md) - What Phantast Lab is and its key features
- [Architecture](./architecture.md) - System design, shell specification, and data model
- [User Flows](./user-flows.md) - Complete user journey from image navigation to batch processing
- [Implementation Guide](./implementation-guide.md) - Technical guidance for developers
- [Feature Specifications](./specs/) - Detailed specs for each feature section

## Getting Started

1. Install Python 3.9+
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python src/main.py`

## Project Structure

```
src/
├── main.py              # Application entry point
├── ui/                  # PyQt6 widgets (views)
├── models/              # Data models and logic
└── controllers/         # Glue between UI and models
```

## Core Stack

- **PyQt6** - Desktop GUI framework
- **OpenCV** - Image processing
- **NumPy/SciPy** - Numerical computing
- **scikit-image** - Image processing algorithms

---

*This documentation consolidates all product specifications and implementation guides for Phantast Lab.*

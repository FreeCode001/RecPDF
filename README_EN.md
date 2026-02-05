# RecPDF

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/release/python-3110/)

RecPDF is a Python package that uses large models to parse and convert PDF documents. It can recognize text, images, tables, formulas, and other elements in PDFs and convert them into structured markdown format.

## Features

- 📄 Parse text, images, tables, formulas, and other elements in PDF documents
- 🤖 Support for intelligent parsing using various large models
- 🔄 Multi-threaded parallel processing for faster parsing
- 📝 Output structured markdown format that preserves the original document hierarchy
- 🎨 Intelligent title level recognition and document structure optimization
- 🖼️ Automatic processing of images and tables to maintain visual integrity

## Installation

Install RecPDF using pip:

```bash
pip install recpdf
```

## Dependencies

- python-dotenv>=1.2.1
- shapely>=2.1.2
- langchain>=1.2.8
- pymupdf>=1.26.7
- langchain-openai>=1.1.7

## Quick Start

### Basic Usage

```python
from recpdf import parse_pdf

# Parse PDF file
content, rect_images = parse_pdf(
    pdf_path="path/to/your/document.pdf",
    output_dir="./output",
    api_key="your_api_key",
    base_url="your_api_base_url",
    model="your_model_name",
    workers=2  # Multi-threaded processing
)

print("Parsing completed, markdown content saved to the specified directory")
```

### Using Environment Variables

You can also set API-related parameters through environment variables, so you don't need to pass these parameters when calling the function:

1. Create a `.env` file:

```
VLM_API_KEY=your_api_key
VLM_API_BASE=your_api_base_url
VLM_API_MODEL=your_model_name
```

2. Then load the environment variables in your code:

```python
import os
from dotenv import load_dotenv
from recpdf import parse_pdf

load_dotenv()

api_key = os.getenv('VLM_API_KEY')
base_url = os.getenv('VLM_API_BASE')
model = os.getenv('VLM_API_MODEL')

content, rect_images = parse_pdf(
    pdf_path="path/to/your/document.pdf",
    output_dir="./output",
    api_key=api_key,
    base_url=base_url,
    model=model
)
```

### Advanced Features

#### Refine Markdown Structure

RecPDF also provides a `refine_markdown` function that can further optimize the structure of the generated markdown document:

```python
from recpdf.parser import refine_markdown

refined_content = refine_markdown(
    markdown_path="path/to/your/output.md",
    api_key="your_api_key",
    base_url="your_api_base_url",
    model="your_model_name"
)

print("Markdown structure optimization completed")
```

## Working Principle

1. **PDF Parsing**: Extract text, images, and graphic elements from PDF pages using PyMuPDF library
2. **Region Recognition**: Identify and merge content regions on the page through geometric analysis
3. **Image Generation**: Convert recognized regions into high-definition images
4. **Large Model Parsing**: Call the configured large model to parse image content, recognizing text, tables, formulas, etc.
5. **Markdown Generation**: Convert parsing results into structured markdown format
6. **Optional Optimization**: Use large models to further optimize markdown document structure

## Project Structure

```
recpdf/
├── __init__.py          # Package entry point, exports main functions
├── parser.py            # Core parsing functionality implementation
├── models.py            # Model initialization module
├── prompts.py           # Parsing prompt definitions
└── utils.py             # Utility functions
```

## Examples

The project provides some example PDF files and output results, located in the `examples/` directory:

- `examples/test1.pdf` - Simple text PDF example
- `examples/test2.pdf` - PDF example with images
- `examples/test3.pdf` - Complex PDF example with tables and formulas
- `examples/output/` - Parsing result output directory

## Configuration Requirements

- Python 3.11 or higher
- Valid large model API key and access address
- Large model with visual understanding capabilities (such as GPT-4V, Claude 3, etc.)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contribution

Welcome to submit issues and pull requests to improve this project!

## Contact

- Author: FreeCode
- Email: freecode0902@gmail.com

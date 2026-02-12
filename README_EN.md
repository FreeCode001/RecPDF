# RecPDF

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![PyPI Version](https://img.shields.io/pypi/v/recpdf.svg)](https://pypi.org/project/recpdf/)

RecPDF is a Python package that uses large language models to parse and convert PDF documents. It can recognize text, images, tables, formulas, and other elements in PDFs and convert them into structured markdown format, with support for multi-language translation.

## Features

- 📄 **Intelligent PDF Parsing** - Recognize text, images, tables, formulas, and other elements in PDFs
- 🤖 **Multi-Model Support** - Support for various LLMs for intelligent parsing (GPT-4V, Claude 3, etc.)
- 🔄 **Multi-threading** - Parallel processing for faster parsing
- 📝 **Structured Output** - Output in markdown format while preserving original document hierarchy
- 🎨 **Smart Optimization** - Use LLMs to optimize markdown document structure
- 🌍 **Multi-Language Translation** - Support multiple translation engines (Google, DeepL, HuggingFace, OpenAI)
- ⚙️ **Flexible Configuration** - Support environment variables and configuration files
- 🖼️ **Visual Integrity** - Automatic processing of images and tables to maintain visual document integrity

## Installation

Install RecPDF using pip:

```bash
pip install recpdf
```

Or install from source:

```bash
git clone https://github.com/FreeCode001/RecPDF.git
cd RecPDF
pip install -e .
```

## Dependencies

- python-dotenv>=1.2.1
- shapely>=2.1.2
- langchain>=1.2.8
- pymupdf>=1.26.7
- langchain-openai>=1.1.7
- googletrans>=4.0.2
- transformers>=5.1.0
- pydantic-settings>=2.12.0
- deepl>=1.28.0
- torch>=2.7.1
- google-trans-new>=1.1.9

## Quick Start

### Basic PDF Parsing

```python
from recpdf import parse_pdf, Settings

# Method 1: Using Settings object configuration
settings = Settings()
settings.parser_api_key = "your_api_key"
settings.parser_api_base = "your_api_base_url"
settings.parser_api_model = "your_model_name"

content, rect_images = parse_pdf(
    pdf_path="path/to/your/document.pdf",
    output_dir="./output",
    settings=settings,
    workers=2  # Multi-threaded processing
)

# Method 2: Using environment variable configuration (recommended)
# Set in .env file: PARSER_API_KEY, PARSER_API_BASE, PARSER_API_MODEL
content, rect_images = parse_pdf(
    pdf_path="path/to/your/document.pdf",
    output_dir="./output",
    workers=2  # Multi-threaded processing
)

print("Parsing completed, markdown content saved to the specified directory")
```

### Environment Variable Configuration

1. Create a `.env` file:

```env
# Parser API configuration
PARSER_API_KEY=your_parser_api_key
PARSER_API_BASE=your_parser_api_base
PARSER_API_MODEL=your_parser_model

# Refiner API configuration
REFINE_API_KEY=your_refine_api_key
REFINE_API_BASE=your_refine_api_base
REFINE_API_MODEL=your_refine_model

# Translation configuration
TRANSLATION_ENGINE=openai
TRANSLATOR_API_KEY=your_translator_api_key
TRANSLATOR_API_BASE=your_translator_api_base
TRANSLATOR_API_MODEL=your_translator_model
```

2. Auto load environment variables:

```python
import os
from recpdf import parse_pdf, Settings

# recpdf auto load environment variables, no need to pass them explicitly
content, rect_images = parse_pdf(
    pdf_path="path/to/your/document.pdf",
    output_dir="./output"
)
```

### Markdown Structure Refinement

```python
from recpdf import refine_markdown, Settings

# Using Settings object configuration
settings = Settings()
settings.refine_api_key = "your_api_key"
settings.refine_api_base = "your_api_base_url"
settings.refine_api_model = "your_model_name"

# Optimize markdown document structure
refined_content = refine_markdown(
    markdown_path="path/to/your/output.md",
    settings=settings
)

# Or using environment variable configuration
# Set in .env file: REFINE_API_KEY, REFINE_API_BASE, REFINE_API_MODEL
refined_content = refine_markdown(
    markdown_path="path/to/your/output.md"
)

print("Markdown structure optimization completed")
```

### Document Translation

RecPDF supports multiple translation engines:

#### 1. Google Translate

```python
from recpdf import translate_markdown, Settings

settings = Settings()
settings.translation_engine = "googletrans"

# Translate markdown file
translate_markdown(
    input_path="input.md",
    output_path="output.md",
    settings=settings,
    source_lang="EN",
    target_lang="ZH"
)
```

#### 2. DeepL Translation

```python
settings = Settings()
settings.translation_engine = "deepl"
settings.deepl_api_key = "your_deepl_api_key"

translate_markdown(
    input_path="input.md",
    output_path="output.md",
    settings=settings,
    source_lang="EN",
    target_lang="ZH"
)
```

#### 3. OpenAI Translation

```python
settings = Settings()
settings.translation_engine = "openai"
settings.translator_api_key = "your_openai_api_key"
settings.translator_api_base = "https://api.openai.com/v1"
settings.translator_api_model = "gpt-4"

translate_markdown(
    input_path="input.md",
    output_path="output.md",
    settings=settings,
    source_lang="EN",
    target_lang="ZH"
)
```

#### 4. HuggingFace Translation

```python
settings = Settings()
settings.translation_engine = "huggingface"
settings.huggingface_model = "Helsinki-NLP/opus-mt-en-zh"

translate_markdown(
    input_path="input.md",
    output_path="output.md",
    settings=settings,
    source_lang="EN",
    target_lang="ZH"
)
```

## API Reference

### Main Functions

#### `parse_pdf()`
Parse PDF documents and convert them to markdown format.

**Parameters:**
- `pdf_path` (str): Path to PDF file
- `output_dir` (str, optional): Output directory, default is './'
- `settings` (Settings, optional): Configuration object containing API key, base URL, model name, etc.
- `workers` (int, optional): Number of worker threads, default is 1
- `prompt` (str, optional): Custom parsing prompt
- `rect_prompt` (str, optional): Rectangle parsing prompt
- `sys_prompt` (str, optional): System prompt

**Returns:**
- `content` (str): Parsed markdown content
- `rect_images` (List[str]): List of rectangle image paths

#### `refine_markdown()`
Optimize markdown document structure.

**Parameters:**
- `markdown_path` (str): Path to markdown file
- `settings` (Settings, optional): Configuration object containing API key, base URL, model name, etc.
- `prompt` (str, optional): Custom optimization prompt
- `sys_prompt` (str, optional): System prompt

**Returns:**
- `str`: Optimized markdown content

#### `translate_markdown()`
Translate markdown documents.

**Parameters:**
- `input_path` (str): Input file path
- `output_path` (str): Output file path
- `settings` (Settings, optional): Configuration object
- `source_lang` (str, optional): Source language, default "EN"
- `target_lang` (str, optional): Target language, default "ZH"

**Returns:**
- `str`: Translated file path

#### `translate_text()`
Translate plain text content.

**Parameters:**
- `input_path` (str): Input file path
- `output_path` (str): Output file path
- `settings` (Settings, optional): Configuration object
- `source_lang` (str, optional): Source language, default "EN"
- `target_lang` (str, optional): Target language, default "ZH"

**Returns:**
- `str`: Translated file path

### Configuration Class

#### `Settings`
RecPDF configuration management class, supporting the following configuration options:

**Parser Configuration:**
- `parser_api_key` (str): Parser API key
- `parser_api_base` (str): Parser API base URL
- `parser_api_model` (str): Parser model name

**Refiner Configuration:**
- `refine_api_key` (str): Refiner API key
- `refine_api_base` (str): Refiner API base URL
- `refine_api_model` (str): Refiner model name

**Translator Configuration:**
- `translation_engine` (str): Translation engine (deepl, googletrans, huggingface, openai)
- `translator_api_key` (str): Translator API key
- `translator_api_base` (str): Translator API base URL
- `translator_api_model` (str): Translator model name
- `deepl_api_key` (str): DeepL API key
- `huggingface_model` (str): HuggingFace model name

## Working Principle

1. **PDF Parsing** - Extract text, images, and graphic elements from PDF pages using PyMuPDF library
2. **Region Recognition** - Identify and merge content regions on pages through Shapely geometric analysis
3. **Image Generation** - Convert recognized regions into high-definition images
4. **LLM Parsing** - Call configured large models to parse image content, recognizing text, tables, formulas, etc.
5. **Markdown Generation** - Convert parsing results into structured markdown format
6. **Structure Optimization** - Optionally use LLMs to further optimize markdown document structure
7. **Multi-Language Translation** - Support multiple translation engines for document translation

## Project Structure

```
recpdf/
├── __init__.py          # Package entry point, exports main functions
├── parser.py            # Core PDF parsing functionality
├── translator.py        # Multi-language translation functionality
├── models.py            # Model initialization and management
├── prompts.py           # Parsing and optimization prompts
├── config.py            # Configuration management
└── utils.py             # Utility functions

tests/
├── test_parser.py       # Parser tests
└── test_translator.py   # Translator tests

examples/
├── test1.pdf           # Simple text PDF example
├── test2.pdf           # PDF example with images
├── test3.pdf           # Complex PDF example with tables and formulas
└── output/             # Parsing result output directory
```

## Configuration Requirements

- **Python Version**: 3.11 or higher
- **API Requirements**: Valid large model API key and access address
- **Recommended Models**: Large models with visual understanding capabilities (e.g., GPT-4V, Claude 3, Gemini Pro Vision, etc.)
- **Translation Services**: API keys required depending on the chosen translation engine

## Examples

The project provides complete example files and output results:

- `examples/test1.pdf` - Simple text PDF example
- `examples/test2.pdf` - PDF example with images
- `examples/test3.pdf` - Complex PDF example with tables and formulas
- `examples/output/` - Parsing result output directory, including markdown and image files

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Welcome to submit issues and pull requests to improve this project!

### Development Environment Setup

```bash
# Clone repository
git clone https://github.com/FreeCode001/RecPDF.git
cd RecPDF

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
pip install -r requirements-dev.txt  # if available

# Run tests
python -m pytest tests/
```

## Contact

- **Author**: FreeCode001
- **Email**: freecode0902@gmail.com
- **Project URL**: https://github.com/FreeCode001/RecPDF

## Changelog

### v0.1.8
- Added multi-language translation functionality
- Support for Google, DeepL, HuggingFace, OpenAI translation engines
- Optimized PDF parsing performance
- Improved markdown structure optimization algorithm

### v0.1.7
- Initial release
- Basic PDF parsing functionality
- Markdown output support
- Multi-threading support
# RecPDF

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![PyPI Version](https://img.shields.io/pypi/v/recpdf.svg)](https://pypi.org/project/recpdf/)

RecPDF是一个使用大模型解析和转换PDF文档的Python包，能够识别PDF中的文本、图片、表格、公式等元素，并将其转换为结构化的markdown格式，同时支持多语言翻译功能。

## 功能特点

- 📄 **智能PDF解析** - 识别PDF中的文本、图片、表格、公式等元素
- 🤖 **多模型支持** - 支持各种大模型进行智能解析（GPT-4V、Claude 3等）
- 🔄 **多线程处理** - 并行处理提高解析速度
- 📝 **结构化输出** - 输出markdown格式，保留原始文档层次结构
- 🎨 **智能优化** - 使用大模型优化markdown文档结构
- 🌍 **多语言翻译** - 支持多种翻译引擎（Google、DeepL、HuggingFace、OpenAI）
- ⚙️ **灵活配置** - 支持环境变量和配置文件
- 🖼️ **视觉完整性** - 自动处理图片和表格，保持文档视觉效果

## 安装

使用pip安装RecPDF：

```bash
pip install recpdf
```

或从源码安装：

```bash
git clone https://github.com/FreeCode001/RecPDF.git
cd RecPDF
pip install -e .
```

## 依赖项

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

## 快速开始

### 基本PDF解析

```python
from recpdf import parse_pdf, Settings

# 方法1：使用Settings对象配置
settings = Settings()
settings.parser_api_key = "your_api_key"
settings.parser_api_base = "your_api_base_url"
settings.parser_api_model = "your_model_name"

content, rect_images = parse_pdf(
    pdf_path="path/to/your/document.pdf",
    output_dir="./output",
    settings=settings,
    workers=2  # 多线程处理
)

# 方法2：使用环境变量配置（推荐）
# 在.env文件中设置：PARSER_API_KEY, PARSER_API_BASE, PARSER_API_MODEL
content, rect_images = parse_pdf(
    pdf_path="path/to/your/document.pdf",
    output_dir="./output",
    workers=2  # 多线程处理
)

print("解析完成，markdown内容已保存到指定目录")
```
### 环境变量配置文件
1. 创建 `.env`文件：

```env
# 解析器API配置
PARSER_API_KEY=your_parser_api_key
PARSER_API_BASE=your_parser_api_base
PARSER_API_MODEL=your_parser_model

# 优化器API配置  
REFINE_API_KEY=your_refine_api_key
REFINE_API_BASE=your_refine_api_base
REFINE_API_MODEL=your_refine_model

# 翻译配置
TRANSLATION_ENGINE=openai
TRANSLATOR_API_KEY=your_translator_api_key
TRANSLATOR_API_BASE=your_translator_api_base
TRANSLATOR_API_MODEL=your_translator_model
```

2. 自动加载环境变量：

```python
import os
from recpdf import parse_pdf

# recpdf自动加载环境变量配置
content, rect_images = parse_pdf(
    pdf_path="path/to/your/document.pdf",
    output_dir="./output",
)
```

### Markdown结构优化

```python
from recpdf import refine_markdown, Settings

# 使用Settings对象配置
settings = Settings()
settings.refine_api_key = "your_api_key"
settings.refine_api_base = "your_api_base_url"
settings.refine_api_model = "your_model_name"

# 优化markdown文档结构
refined_content = refine_markdown(
    markdown_path="path/to/your/output.md",
    settings=settings
)

# 或使用环境变量配置
# 在.env文件中设置：REFINE_API_KEY, REFINE_API_BASE, REFINE_API_MODEL
refined_content = refine_markdown(
    markdown_path="path/to/your/output.md"
)

print("Markdown结构优化完成")
```

### 文档翻译

RecPDF支持多种翻译引擎：

#### 1. Google翻译

```python
from recpdf import translate_markdown, Settings

settings = Settings()
settings.translation_engine = "googletrans"

# 翻译markdown文件
translate_markdown(
    input_path="input.md",
    output_path="output.md",
    settings=settings,
    source_lang="EN",
    target_lang="ZH"
)
```

#### 2. DeepL翻译

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

#### 3. OpenAI翻译

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

#### 4. HuggingFace翻译

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

## API参考

### 主要函数

#### `parse_pdf()`

解析PDF文档并转换为markdown格式。

**参数：**

- `pdf_path` (str): PDF文件路径
- `output_dir` (str, optional): 输出目录，默认为'./'
- `settings` (Settings, optional): 配置对象，包含API密钥、基础URL、模型名称等
- `workers` (int, optional): 工作线程数，默认为1
- `prompt` (str, optional): 自定义解析提示词
- `rect_prompt` (str, optional): 矩形解析提示词
- `sys_prompt` (str, optional): 系统提示词

**返回：**

- `content` (str): 解析后的markdown内容
- `rect_images` (List[str]): 矩形图片路径列表

#### `refine_markdown()`

优化markdown文档结构。

**参数：**

- `markdown_path` (str): markdown文件路径
- `settings` (Settings, optional): 配置对象，包含API密钥、基础URL、模型名称等
- `prompt` (str, optional): 自定义优化提示词
- `sys_prompt` (str, optional): 系统提示词

**返回：**

- `str`: 优化后的markdown内容

#### `translate_markdown()`

翻译markdown文档。

**参数：**

- `input_path` (str): 输入文件路径
- `output_path` (str): 输出文件路径
- `settings` (Settings, optional): 配置对象
- `source_lang` (str, optional): 源语言，默认"EN"
- `target_lang` (str, optional): 目标语言，默认"ZH"

**返回：**

- `str` (str): 翻译后的文件路径

#### `translate_text()`

翻译纯文本内容。

**参数：**

- `input_path` (str): 输入文件路径
- `output_path` (str): 输出文件路径
- `settings` (Settings, optional): 配置对象
- `source_lang` (str, optional): 源语言，默认"EN"
- `target_lang` (str, optional): 目标语言，默认"ZH"

**返回：**

- `str` (str): 翻译后的文件路径

### 配置类

#### `Settings`

RecPDF配置管理类，支持以下配置项：

**解析器配置：**

- `parser_api_key` (str): 解析器API密钥
- `parser_api_base` (str): 解析器API基础URL
- `parser_api_model` (str): 解析器模型名称

**优化器配置：**

- `refine_api_key` (str): 优化器API密钥
- `refine_api_base` (str): 优化器API基础URL
- `refine_api_model` (str): 优化器模型名称

**翻译器配置：**

- `translation_engine` (str): 翻译引擎 (deepl, googletrans, huggingface, openai)
- `translator_api_key` (str): 翻译器API密钥
- `translator_api_base` (str): 翻译器API基础URL
- `translator_api_model` (str): 翻译器模型名称
- `deepl_api_key` (str): DeepL API密钥
- `huggingface_model` (str): HuggingFace模型名称

## 工作原理

1. **PDF解析** - 使用PyMuPDF库提取PDF页面中的文本、图片和图形元素
2. **区域识别** - 通过Shapely几何分析识别和合并页面中的内容区域
3. **图像生成** - 将识别到的区域转换为高清图像
4. **大模型解析** - 调用配置的大模型解析图像内容，识别文本、表格、公式等
5. **Markdown生成** - 将解析结果转换为结构化的markdown格式
6. **结构优化** - 可选使用大模型进一步优化markdown文档结构
7. **多语言翻译** - 支持多种翻译引擎进行文档翻译

## 项目结构

```
recpdf/
├── __init__.py          # 包入口，导出主要函数
├── parser.py            # 核心PDF解析功能
├── translator.py        # 多语言翻译功能
├── models.py            # 模型初始化和管理
├── prompts.py           # 解析和优化提示词
├── config.py            # 配置管理
└── utils.py             # 工具函数

tests/
├── test_parser.py       # 解析器测试
└── test_translator.py   # 翻译器测试

examples/
├── test1.pdf           # 简单文本PDF示例
├── test2.pdf           # 包含图片的PDF示例
├── test3.pdf           # 包含表格和公式的复杂PDF示例
└── output/             # 解析结果输出目录
```

## 配置要求

- **Python版本**: 3.11或更高版本
- **API要求**: 有效的大模型API密钥和访问地址
- **推荐模型**: 支持视觉理解的大模型（如GPT-4V、Claude 3、Gemini Pro Vision等）
- **翻译服务**: 根据选择的翻译引擎需要相应的API密钥

## 示例

项目提供了完整的示例文件和输出结果：

- `examples/test1.pdf` - 简单文本PDF示例
- `examples/test2.pdf` - 包含图片的PDF示例
- `examples/test3.pdf` - 包含表格和公式的复杂PDF示例
- `examples/output/` - 解析结果输出目录，包含markdown和图片文件

## 许可证

本项目采用MIT许可证，详见[LICENSE](LICENSE)文件。

## 贡献

欢迎提交问题和拉取请求来改进这个项目！

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/FreeCode001/RecPDF.git
cd RecPDF

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .
pip install -r requirements-dev.txt  # 如果有的话

# 运行测试
python -m pytest tests/
```

## 联系方式

- **作者**: FreeCode001
- **邮箱**: freecode0902@gmail.com
- **项目地址**: https://github.com/FreeCode001/RecPDF

## 更新日志

### v0.1.8

- 添加多语言翻译功能
- 支持Google、DeepL、HuggingFace、OpenAI翻译引擎
- 优化PDF解析性能
- 改进markdown结构优化算法

### v0.1.7

- 初始版本发布
- 基础PDF解析功能
- Markdown输出支持
- 多线程处理

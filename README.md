# RecPDF

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/release/python-3110/)

RecPDF是一个使用大模型解析和转换PDF文档的Python包，能够识别PDF中的文本、图片、表格、公式等元素，并将其转换为结构化的markdown格式。

## 功能特点

- 📄 解析PDF文档中的文本、图片、表格、公式等元素
- 🤖 支持使用各种大模型进行智能解析
- 🔄 多线程并行处理，提高解析速度
- 📝 输出结构化的markdown格式，保留原始文档的层次结构
- 🎨 智能识别标题层级，优化文档结构
- 🖼️ 自动处理图片和表格，保持文档的视觉完整性

## 安装

使用pip安装RecPDF：

```bash
pip install recpdf
```

## 依赖项

- python-dotenv>=1.2.1
- shapely>=2.1.2
- langchain>=1.2.8
- pymupdf>=1.26.7
- langchain-openai>=1.1.7

## 快速开始

### 基本使用

```python
from recpdf import parse_pdf

# 解析PDF文件
content, rect_images = parse_pdf(
    pdf_path="path/to/your/document.pdf",
    output_dir="./output",
    api_key="your_api_key",
    base_url="your_api_base_url",
    model="your_model_name",
    workers=2  # 多线程处理
)

print("解析完成，markdown内容已保存到指定目录")
```

### 使用环境变量

您也可以通过环境变量设置API相关参数，这样在调用函数时就不需要传递这些参数了：

1. 创建一个 `.env`文件：

```
VLM_API_KEY=your_api_key
VLM_API_BASE=your_api_base_url
VLM_API_MODEL=your_model_name
```

2. 然后在代码中加载环境变量：

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

### 高级功能

#### 调整Markdown结构

RecPDF还提供了一个 `refine_markdown`函数，可以进一步优化生成的markdown文档结构：

```python
from recpdf.parser import refine_markdown

refined_content = refine_markdown(
    markdown_path="path/to/your/output.md",
    api_key="your_api_key",
    base_url="your_api_base_url",
    model="your_model_name"
)

print("Markdown结构优化完成")
```

## 工作原理

1. **PDF解析**：使用PyMuPDF库提取PDF页面中的文本、图片和图形元素
2. **区域识别**：通过几何分析识别和合并页面中的内容区域
3. **图像生成**：将识别到的区域转换为高清图像
4. **大模型解析**：调用配置的大模型解析图像内容，识别文本、表格、公式等
5. **Markdown生成**：将解析结果转换为结构化的markdown格式
6. **可选优化**：使用大模型进一步优化markdown文档结构

## 项目结构

```
recpdf/
├── __init__.py          # 包入口，导出主要函数
├── parser.py            # 核心解析功能实现
├── models.py            # 模型初始化模块
├── prompts.py           # 解析提示词定义
└── utils.py             # 工具函数
```

## 示例

项目提供了一些示例PDF文件和输出结果，位于 `examples/`目录中：

- `examples/test1.pdf` - 简单文本PDF示例
- `examples/test2.pdf` - 包含图片的PDF示例
- `examples/test3.pdf` - 包含表格和公式的复杂PDF示例
- `examples/output/` - 解析结果输出目录

## 配置要求

- Python 3.11或更高版本
- 有效的大模型API密钥和访问地址
- 支持视觉理解的大模型（如GPT-4V、Claude 3等）

## 许可证

本项目采用MIT许可证，详见[LICENSE](LICENSE)文件。

## 贡献

欢迎提交问题和拉取请求来改进这个项目！

## 联系方式

- 作者：FreeCode
- 邮箱：freecode0902@gmail.com

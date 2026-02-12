"""
模型初始化模块
parse_model: 解析模型，用于将PDF文档解析为Markdown格式
refine_model: 格式优化模型，用于对Markdown格式的文档进行格式优化
translator_model: 翻译模型，用于将文本翻译成目标语言
"""
from langchain.chat_models import init_chat_model


def init_parser_model(api_key: str, base_url: str, model: str, temperature: float = 0.5, max_tokens: int = 96000):
    parse_model = init_chat_model(
        api_key = api_key,
        base_url = base_url,
        model = model,
        model_provider = "openai",
        temperature = temperature,
        max_tokens = max_tokens,
    )
    return parse_model

def init_refine_model(api_key: str, base_url: str, model: str, temperature: float = 0.5, max_tokens: int = 102400):
    refine_model = init_chat_model(
        api_key = api_key,
        base_url = base_url,
        model = model,
        model_provider = "openai",
        temperature = temperature,
        max_tokens = max_tokens,
    )
    return refine_model

def init_translator_model(api_key: str, base_url: str, model: str, temperature: float = 0.5, max_tokens: int = 102400):
    translator_model = init_chat_model(
        api_key = api_key,
        base_url = base_url,
        model = model,
        model_provider = "openai",
        temperature = temperature,
        max_tokens = max_tokens,
    )
    return translator_model

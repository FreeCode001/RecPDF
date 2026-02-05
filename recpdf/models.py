"""
模型初始化模块
解析模型：parse_model
"""
import os
from langchain.chat_models import init_chat_model


def init_vlm(api_key: str, base_url: str, model: str, temperature: float = 0.5, max_tokens: int = 96000):
    model = init_chat_model(
        api_key = api_key,
        base_url = base_url,
        model = model,
        model_provider = "openai",
        temperature = temperature,
        max_tokens = max_tokens,
    )
    return model

def init_llm(api_key: str, base_url: str, model: str, temperature: float = 0.5, max_tokens: int = 102400):
    model = init_chat_model(
        api_key = api_key,
        base_url = base_url,
        model = model,
        model_provider = "openai",
        temperature = temperature,
        max_tokens = max_tokens,
    )
    return model